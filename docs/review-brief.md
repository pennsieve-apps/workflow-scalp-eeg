# Brief for the independent review of an app before its pull request

You review one or more apps of the scalp EEG workflows that **another agent built**. You did not
write them, and you must not trust the builder's report: check claims against the code, the
outputs and the registries yourself. The apps will be used by epilepsy and neurology labs; a wrong
citation, a misattributed method, a silently wrong result, an intracranial validation presented as
a scalp one, or a licence problem is worse than a missing feature.

Read first: `~/code/pennsieve/workflow-scalp-eeg/docs/conventions.md`, `docs/builder-brief.md`,
`docs/research/1-scalp-eeg-survey.md` and `docs/research/citations.md` (including its corrections).

## What to check

1. **Citations and attribution (zero tolerance for invented facts).**
   - Run `scripts/verify-citations.py <repo>`; every line must be `ok`.
   - Independently, for **every** reference: open the Crossref/DataCite/PubMed record yourself and
     compare title, every author in order, journal, year, volume, pages. Check that the work is the
     right one for the claim (the detector's own paper for the detector; the dataset's DOI for the
     dataset; PhysioNet's two requested citations for PhysioNet data).
   - Every person, lab or institute named in the README (opening attribution paragraph,
     acknowledgements) must be verifiable from the tool's own repository, paper or website. Check
     each name. Remove or flag anything you cannot verify.
   - Every tool, model weight and dataset the code imports or bundles is credited (README +
     CITATION.cff + THIRD_PARTY.md), and each project's own "how to cite" is honoured.
   - Claims about validation: a method validated on intracranial EEG (Janca, Barkmeier) must not
     be described as validated on scalp EEG; our own scalp validation numbers must be reproducible
     from `data/work/`.
2. **Licences.** Every bundled package and weight file: licence matches its LICENSE/model card at
   the pinned version; nothing from the builder brief's "do not use" list; academic-only parts
   nowhere.
3. **Science and method.** Defaults match the brief / upstream best practice (and the README says
   where they come from); statistics have proper nulls and corrections; units and time bases are
   right (seconds from the recording start; µV; `dateTime` in SzCORE files is wall clock);
   nothing silently drops data (bad segments and seizures are excluded only where the contract says
   so, and the minutes analysed are reported); the montage case (referential vs bipolar-only) is
   handled and recorded; the README's limitations are honest. Re-derive at least one headline
   number from the outputs in `data/work/` yourself (e.g. a spike rate from `spikes.csv`, an event
   F1 from `szcore/*.tsv` with `timescoring`, a band power from the EDF with MNE).
4. **Contract.** Ports, folder layout (`<port>/<app>/`, eeg-prep's derivative at the port root),
   recording_id rules, `recordings.csv` columns, provenance.json keys, summary.json with figures +
   captions, exit codes, THREADS/SEED, no network at run time, uid 1000 on ECS, and **Lambda-safe**
   (builder brief, "How a Lambda step runs"): no handler.py, no writes outside
   `$TMPDIR`/`$HOME`/INPUT/OUTPUT, nothing needed from the image's `/tmp` or `HOME`; run the
   documented `--read-only --user 65534:65534 --tmpfs /tmp` test yourself. Run the app on the
   bipolar-only fixture as well as the referential one.
5. **Code.** Read all of `processor/`. Look for bugs: off-by-one in windows, sample/second
   confusion, wrong unit conversions (V vs µV in MNE), file matching that picks the wrong file,
   crashes on edge cases (one recording, no seizures annotated, no sleep, missing positions, a
   recording shorter than a window), memory blow-ups on long recordings (a 24 h file must stream).
   Run the tests (`make test`) and `make run` on the fixture. Validate `app.yml` against
   `docs/app-manifest.v1.schema.json`; check the review block's generate command works.
6. **README claims.** Every number (runtime, memory, accuracy, image size) must be backed by a
   measurement you can find in the repo, `data/work/` or the builder's logs; otherwise flag it.

## Output

Fix only what is **clearly wrong and mechanical** (a wrong author name, a typo'd DOI, a missing
reference, an incorrect licence string) in a separate commit per repo (`review: ...`, same
author/co-author lines as the brief). Do not refactor or change methods; list those as findings.
Do not push.

Report per app: verdict (`ready`, `ready after fixes I made`, `needs builder work`), each finding
with file:line, severity (blocker / should-fix / nit), and evidence (registry URL, command output).
The coordinator puts a summary of your review in the pull request.
