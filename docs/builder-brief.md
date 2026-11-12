# Brief for building an app of the scalp EEG workflows

You are building one or more Pennsieve processor apps, each in its own git repo under
`~/code/pennsieve/<repo>` (remote `git@github.com:pennsieve-apps/<repo>.git`, public). Repo names
carry **no `processor-` prefix**: `eeg-prep`, `eeg-spectral`, `eeg-spikes`, `eeg-seizures`,
`eeg-sleep`, `eeg-connectivity`, `eeg-report`. Refer to sibling apps by these names. They form two
workflows for epilepsy and neurology research on **clinical scalp EEG** (routine EEG and long-term
video-EEG monitoring), meant to be used broadly (any hospital's exported EEG, any BIDS-EEG dataset),
not only on the demo data:

- **Scalp EEG Interictal Biomarkers:** `eeg-prep → {eeg-spectral, eeg-connectivity, eeg-sleep → eeg-spikes} → eeg-report`
- **Scalp EEG Seizure Detection & Monitoring:** `eeg-prep → {eeg-seizures, eeg-sleep → eeg-spikes} → eeg-report`

Audience: epileptologists, neurologists and EEG researchers who are not software engineers.
Defaults must do the right thing on a typical clinical recording; every figure gets a caption that
says what to look at; every number that could be mistaken for a clinical finding is labelled as a
research output to be reviewed.

The sibling family is `~/code/pennsieve/workflow-epilepsy-ieeg` (intracranial). Its apps
(`processor-ieeg-prep`, `processor-ieeg-spikes`, `processor-ieeg-bandpower`, `processor-ieeg-hfo`,
`processor-ieeg-report`) are the closest finished code: copy their reading, windowing, threading
(`processor/resources.py`) and table-writing patterns, and keep the table shapes compatible
(conventions.md). Do not copy their SEEG/ECoG channel filtering: scalp EEG keeps the EEG channels.

## Read first

1. `~/code/pennsieve/workflow-scalp-eeg/docs/conventions.md`: the file, port, recording and
   montage contract between apps. Follow it exactly. If something in it is wrong or missing, say so
   in your report instead of silently diverging.
2. `~/code/pennsieve/workflow-scalp-eeg/docs/research/1-scalp-eeg-survey.md`: tools, versions,
   licences, datasets (as of 2026-11-12; re-check PyPI and pin exact versions) and
   `docs/research/citations.md`: every DOI verified against the registries, **and the corrections
   to the survey** (read them: two of the survey's claims about spike detectors were wrong).
3. Finished apps to copy layout, tone and level of care from:
   `~/code/pennsieve/processor-ieeg-hfo` (electrophysiology step: windowed reading, `resources.py`,
   `tests/make_fixture.py`, the `review` block in `app.yml`), `~/code/pennsieve/processor-ieeg-prep`
   (reading many formats, BIDS derivative writing, EDF+ output), `~/code/pennsieve/st-svg` (small
   CPU app, Lambda-capable layout: `processor/`, Makefile, tests, `docker-compose.yml`, `dev.env`,
   README, `THIRD_PARTY.md`, `CITATION.cff`, `sample-input/README.md`),
   `~/code/pennsieve/processor-ieeg-report` and `~/code/pennsieve/neuro-report` (report apps).
4. The app manifest: schema `docs/app-manifest.v1.schema.json` in the workflow repo, and the docs in
   `~/code/pennsieve/app-deploy-service/docs/` (`app-manifest-review.md`, `app-manifest-folders.md`).
   Validate `app.yml` against the schema (`python3.12 -m venv` + `pip install jsonschema pyyaml` in
   your scratch dir). Do NOT add `application.relations`.

## Every repo has

`app.yml` (`# yaml-language-server: $schema=https://schemas.pennsieve.io/app-manifest/v1.json`,
`schemaVersion: "1.0"`, `application` with name/description/type processor/tags, `runtime`
cpu/memory/computeTypes/timeoutSeconds, `parameters`, `inputs`, `outputs`, and a **`review` block**
with a `generate` command that writes small test inputs, like processor-ieeg-hfo).
Tags: `eeg`, `scalp-eeg`, `electrophysiology`, `epilepsy`, `neurology`, `neuroscience`, plus task
tags (`preprocessing`, `quality-control`, `spike-detection`, `seizure-detection`, `sleep`,
`spectral-analysis`, `connectivity`, `biomarkers`, `report`, ...).

`Dockerfile` (linux/amd64, base image pinned by digest, pinned package versions, non-interactive,
no network at run time, as small as reasonable; `python:3.12-slim` + pinned `requirements.txt`
installed with `--no-deps --only-binary=:all:` as processor-ieeg-hfo does; model weights (ICLabel's
are inside the `mne-icalabel` wheel; YASA's classifiers inside the `yasa` wheel: check and record
their paths and licences) verified at build time), `processor/` code, `tests/` (pytest on a tiny
synthetic fixture, no Docker; `tests/make_fixture.py` writes it, also used by `review.generate`),
`Makefile` (`test`, `fixture`, `run` = docker compose over a fixture into `data/output/`, `clean`),
`docker-compose.yml`, `dev.env`, `sample-input/README.md` (how to get real input: which PhysioNet
or OpenNeuro files), `README.md`, `THIRD_PARTY.md` (every bundled component and model weight, with
its licence), `LICENSE`, `VERSION` (`0.1.0`), `CITATION.cff`, `.gitignore`.

**Lambda needs no extra code.** The platform decides whether a version can run as a Lambda step
from its `runtime` and image (app-deploy-service `docs/builds.md`, "Lambda eligibility"): `memory`
≤ 10240 MiB, `cpu` ≤ 6144, `timeoutSeconds` ≤ 900 (or unset), image ≤ 10 GB compressed, not
GPU-only. So do **not** write a `processor/handler.py`, and do not list `lambda` in `computeTypes`
(`[standard]`). Size `cpu`, `memory` and `timeoutSeconds` from what you measured, and keep light
steps within those limits where they honestly fit (`eeg-report`, probably `eeg-spectral` on routine
EEG); don't inflate them. Long-term EEG steps (`eeg-prep`, `eeg-seizures`, `eeg-sleep`,
`eeg-spikes` on 24 h) are sized from measurement with timeouts of hours.

How a Lambda step runs (compute-node-aws-provisioner `cmd/lambda-step-runtime`): every image built
by the App Store gets a runtime binary as the function's entrypoint; it fetches inputs into `/tmp`,
runs the image's own ENTRYPOINT/CMD with the ECS contract, and pushes `OUTPUT_DIR`. So **every app
must be Lambda-safe**, whatever it is sized for:
- The file system is read-only except `INPUT_DIR`, `OUTPUT_DIR`, `HOME` and `TMPDIR`, all under a
  step folder in `/tmp`, which the runtime sets. **Write scratch only to `$TMPDIR` (`tempfile`) or
  `$HOME`, never to a hard-coded `/tmp/...` path.**
- `/tmp` is the function's own disk: anything the image put in `/tmp` is **not there**. Bake model
  weights, font caches, numba caches into a read-only path such as `/opt/<app>/` and point the
  library at it with an env var; caches that must be written (matplotlib, numba) go to
  `$TMPDIR`-relative paths set at startup (`MPLCONFIGDIR=$TMPDIR/mpl`), not in the Dockerfile.
- `HOME` is overridden, so nothing may depend on files in the image's HOME (`~/.cache`, MNE's
  config and data dirs: set `MNE_DONTWRITE_HOME=true`, `MNE_DATA`, `MNE_USE_CUDA=false`).
- The app runs as a least-privileged user, not the image's `USER` (uid 1000 on ECS): don't rely on
  a particular uid or on owning files in the image.
- Inputs + outputs + scratch share at most 10 GB of `/tmp`; a step has at most 15 min.
- Test it: `docker run --read-only --user 65534:65534 --tmpfs /tmp:mode=1777 -e HOME=/tmp/w/home
  -e TMPDIR=/tmp/w/tmp -e INPUT_DIR=/tmp/s/input -e OUTPUT_DIR=/tmp/s/output -v <in>:/tmp/s/input:ro
  -v <out>:/tmp/s/output ...` (the app must create HOME/TMPDIR itself if missing) must work.

Python 3.12. Synthetic fixtures: a small BIDS-EEG derivative written with MNE (`tests/make_fixture.py`),
a few minutes of 19-channel 10-20 EEG at 256 Hz with a planted posterior alpha rhythm, planted
spikes (known times and channels, so tests assert recovery), a planted seizure-like rhythmic
discharge, and a sleep-like segment with slow waves; plus a bipolar-only variant (CHB-MIT style)
so both montages are tested.

## Methods and defaults per app (decided; deviations go in your report)

- **eeg-prep**: MNE-Python readers (EDF/EDF+/BDF, BrainVision, EEGLAB, FIF, Nihon Kohden `.EEG`,
  Natus `.e` via `mne.io.read_raw_nihon` / `read_raw_nicolet`; MNE-BIDS for BIDS-EEG). Channel
  canonicalisation to 10-20/10-10 (MNE `standard_1005`), non-EEG channels dropped and listed;
  pyprep `NoisyChannels` for bad channels (flat, deviation, HF noise, correlation, RANSAC when
  positions exist), robust average reference as in PREP; filters as in conventions.md; ICA (MNE
  `picard` or `infomax`, `n_components` ≤ good channels−1, on 1 Hz high-passed data) + mne-icalabel
  for artifact components (needs positions and ≥ 8 channels); optional ASR via python-meegkit;
  bad segments by `mne.preprocessing.annotate_amplitude` and `annotate_muscle_zscore`; EDF+
  written incrementally in windows (copy processor-ieeg-prep's `edfout.py`); labels from BIDS
  events (HED-SCORE too), EDF+ annotations, CHB-MIT `-summary.txt`, `labels.csv`. QC table + one
  figure per recording (PSD per channel, bad channels, removed components' topographies).
- **eeg-spectral**: Welch PSD (MNE `compute_psd`, 4 s Hamming windows, 50 % overlap) on
  artifact-free windows; band powers (absolute, relative, log); specparam (`specparam` 2.x or
  `fooof` 1.1, fixed mode, 1–45 Hz, `peak_width_limits` 1–8 Hz, `max_n_peaks` 6; report `r_squared`
  and flag fits < 0.9); posterior dominant rhythm from O1/O2 (and P3/P4 fallback) on eyes-closed
  segments when annotated, else on all artifact-free windows with a note, as the specparam peak in
  6–14 Hz (Lodder & van Putten 2011; Zibrandtsen & Kjaer 2021 as validation reference); revised
  Brain Symmetry Index (van Putten 2007) per homologous pair and overall; theta/alpha and
  (delta+theta)/(alpha+beta) slowing ratios. Figures: mean PSD per region with the aperiodic fit,
  topomap of alpha power and of the aperiodic exponent, PDR left vs right.
- **eeg-spikes**: default detector `janca` (epycom's envelope-distribution detector, Janca et al.
  2015) and `barkmeier` (epycom, Barkmeier et al. 2012), **both intracranial-validated**: the
  README must say so, and the app must be validated by you on scalp data. Validation: (a) the
  planted-spike fixture (sensitivity/precision at ±50 ms); (b) if `data/vepiset/` has been staged
  (vEpiSet, 4-s epochs with expert IED labels and 29-channel scalp EEG), the per-epoch detection
  rate on IED vs non-IED epochs with AUROC and the operating point; (c) on Siena, the spike rate
  per channel against the annotated lateralisation in `participants.tsv` (left/right temporal).
  Run on the longitudinal bipolar montage derived in-app from referential data (set
  `MONTAGE=bipolar|referential`), since clinicians read spikes bipolar; spikes within 50 ms across
  channels are merged into one `spike_events.csv` row with the leading channel (earliest peak)
  and hemisphere. Rates per sleep stage from the linked hypnogram (Malow 1998; Conrad 2023 as the
  motivating iEEG result; say it is an iEEG result). Seizures and `bad_segment`s left out
  (`EXCLUDE_SEIZURE`, margin 60 s). Figures: spike-rate topomap, rate per stage, example spikes.
- **eeg-seizures**: the SzCORE contract (Dan et al. 2024): operate on the 19 10-20 channels in
  average reference at 256 Hz (resample in-app; keep bipolar-only recordings bipolar and say so),
  write `szcore/<recording_id>.tsv` exactly as SzCORE's `Annotations` class does (`onset, duration,
  eventType, confidence, channels, dateTime, recordingDuration`), score with `timescoring`
  (`SampleScoring` and `EventScoring` with SzCORE's defaults: 30 s tolerance before, 60 s after,
  minimum overlap 0, max event duration 5 min, min duration between events 90 s) against the
  annotated seizures. Detector `DETECTOR=linelength` (default): per-channel line length (Esteller
  et al. 2001) in 2 s windows, 1 s step, normalised per channel by a rolling 5-min median/MAD
  baseline, combined across channels (mean of the top-k channels), thresholded with hysteresis and
  SzCORE's post-processing (merge events closer than 90 s, minimum duration `MIN_DURATION_S` 10 s,
  maximum 5 min); `DETECTOR=gotman` is **not** to be implemented from the GPL reimplementation
  (write your own from Gotman 1982 if you add it, or leave it out). A `model` input port
  (optional) accepts a user-supplied model folder with a documented interface (ONNX or
  TorchScript taking 19×256·W float32 windows, returning per-second probabilities), so open-weight
  models can be plugged in later without rebuilding; no model is bundled in v0.1.0. Outputs are
  review candidates: the README and the report say so, and FP/day is always shown next to
  sensitivity.
- **eeg-sleep**: YASA `SleepStaging` (one central EEG channel, C4-M1 or C3-M2 when available, else
  the best central/bipolar pair, plus EOG/EMG if the source kept them: eeg-prep does not, so say
  the staging is EEG-only and quote YASA's reported accuracy for that case), 30 s epochs, stage
  probabilities and confidence; `sleep_statistics`; spindles (`spindles_detect`) and slow waves
  (`sw_detect`) on N2/N3 for central and frontal channels. Hypnogram figure, spectrogram, spindle
  density topomap. Recordings shorter than `MIN_SLEEP_MINUTES` (default 60) are skipped with a
  note (routine EEG has little sleep).
- **eeg-connectivity**: mne-connectivity `spectral_connectivity_epochs` on 4 s artifact-free
  epochs, measures `wpli` (default), `imcoh`, and `envelope correlation` (orthogonalised,
  `mne_connectivity.envelope_correlation` on band-passed Hilbert envelopes), bands as eeg-spectral;
  on referential data in average reference (bipolar-only recordings: computed on the pairs with a
  clear warning that bipolar derivations share electrodes). Node strength; graph metrics with
  networkx (not bctpy, GPL) on proportional-threshold (`DENSITY` 0.2) weighted graphs, with a
  degree-preserving null for small-worldness (Rubinov & Sporns 2010 for definitions); hemispheric
  means and asymmetry (Verhoeven et al. 2018 as the design reference, sensor-level proxy; say so).
  Figures: connectivity matrix per band, circle plot of the strongest edges, node-strength topomap.
- **eeg-report**: like neuro-report: renders each linked step's `summary.json` figures in order
  with captions, a recordings table, the QC summary, seizure scores, spike lateralisation, PDR and
  asymmetry headline numbers, `licence_notice`s prominently, and a references section built from
  each step's `citations` DOIs (bundle a citation table with the verified references). HTML +
  PDF (WeasyPrint) + `tables/`.

## Licences

Re-check the LICENSE of what you bundle (the survey has them as of 2026-11-12). Our own code is
Apache-2.0. Everything chosen above is BSD/MIT/Apache: MNE-Python, MNE-BIDS, pyprep, autoreject,
mne-icalabel (ICLabel weights: BSD-2 upstream, shipped BSD-3), python-meegkit, specparam/fooof,
YASA (+ bundled LightGBM classifiers), mne-connectivity, networkx, epycom (Apache-2.0 LICENSE.txt),
timescoring and szcore (MIT), WeasyPrint (BSD-3), antropy (BSD-3).

Do **not** use: SpikeNet/SpikeNet2 (CC BY-NC, gated weights), SeizureTransformer weights (only
inside a Docker image, no licence), the EPFL `gotman_1982`, `eventnet_2024` and SeizUnet
reimplementations (GPL-3), DynaSD for scalp (CC BY-NC per its SzCORE entry), PyHFO (academic
licence), GSSC (AGPL), bctpy (GPL), U-Sleep weights (web service only), anything with no licence
(DeepSOZ, Epilepsy-IEDs). Never use anything with no licence. If you think an exception is worth it,
report it instead of building it.

## README

What the app does and why, for an epileptologist and for a researcher; port table; parameters
table (defaults, what each does); outputs with columns; runtime (cpu/memory chosen and
**measured** peak memory and wall time on the demo data, saying it was amd64 emulation on an
M-series Mac); limitations (what the method cannot tell you; which validations are intracranial
only); licences; **Citations**.

## Attribution to the original developers (required)

These apps package other people's methods; the credit is theirs and must be impossible to miss:

- **README, first paragraph after the title**: name the tool(s) the app is built on, who made them
  (developers and their lab/institute, e.g. "YASA, developed by Raphael Vallat and Matthew Walker
  at the University of California, Berkeley"; "MNE-Python, developed by Alexandre Gramfort and
  the MNE community"; "epycom, from the Brno Epilepsy Center (FNUSA-ICRC)"), a link to their
  repository and paper, and a sentence that Pennsieve packages the method and did not develop it.
  Same for model weights (ICLabel: Luca Pion-Tonachini, Ken Kreutz-Delgado and Scott Makeig at the
  Swartz Center, UC San Diego) and for the demo datasets' authors (Siena: Paolo Detti and
  colleagues at the University of Siena; the BIDS conversion by Jonathan Dan et al., EPFL; CHB-MIT:
  Ali Shoeb and John Guttag, MIT, with Children's Hospital Boston; ds003555: Dorottya Cserpan,
  Johannes Sarnthein and colleagues, University Hospital Zurich). **Every name must be verifiable
  from the project's own repository, paper or website**; if you cannot verify a name, leave it out.
- **README `## Citations`**: the primary method paper(s) with the **full author list**; other works
  may use "et al." when the full list is in CITATION.cff. A line "Please cite these works if you
  use this app" and "Verified on Crossref/DataCite and PubMed; full author lists in CITATION.cff".
  Software without a paper: cite its Zenodo/software DOI or repository URL with its authors.
- **README `## Acknowledgements`**: the upstream projects and their funders/consortia where the
  project asks for it.
- **CITATION.cff**: `message: If you use this app, please cite it and the works it builds on,
  listed under references.`; the entity author plus `contact:` (`given-names: Joost`,
  `family-names: Wagenaar`, `orcid: https://orcid.org/0009-0004-5925-5451`, `affiliation:
  University of Pennsylvania`), exactly as `~/code/pennsieve/cell2location/CITATION.cff`;
  `references:` for **every** tool, model and dataset the app uses or the README cites (articles,
  software (`type: software` with `repository-code`), datasets (`type: data` with the DOI and its
  creators as DataCite/PhysioNet list them)), all authors in order.
- **THIRD_PARTY.md**: each bundled component, its authors/copyright holder, licence and URL.
- Respect each project's own "how to cite" (its CITATION.cff, README or docs): cite everything it
  asks for (MNE asks for Gramfort 2013; YASA for Vallat & Walker 2021; PhysioNet asks for the
  database DOI **and** Goldberger et al. 2000 Circulation; the Siena database for Detti et al.
  2020 Processes; mne-icalabel for Li et al. 2022 JOSS **and** Pion-Tonachini 2019).

## Citations: verified, and in CITATION.cff

Every paper or software you cite: authors, title, journal, year, volume:pages, DOI (and PMID if it
has one). Verify each via `https://api.crossref.org/works/<DOI>` (or DataCite for Zenodo, PhysioNet,
OpenNeuro and figshare DOIs, `https://api.datacite.org/dois/<DOI>`) and, for the PMID,
`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<DOI>[doi]&retmode=json`
then `esummary`: title, author list and year must match. Never cite something you could not
verify; cite the software repo URL instead. **Never write an author name, title, journal, volume,
page or year from memory**: copy every field from the registry response. Before you report, run
`~/code/pennsieve/workflow-scalp-eeg/scripts/verify-citations.py <your repo>` (needs pyyaml) and
fix everything it flags; it checks every CITATION.cff reference (title, all authors in order,
year, journal, PMID→DOI) and every DOI/PMID in the README. Paste its final line in your report. An
independent reviewer reruns it and checks your citations again before anything is published.
Verified DOIs are in `docs/research/citations.md`; re-fetch each by DOI anyway.

`CITATION.cff` (CFF 1.2.0): `type: software`, title = app name, abstract, `repository-code`
`https://github.com/pennsieve-apps/<repo>`, license, keywords, **one entity author**
`- name: Pennsieve (University of Pennsylvania)`, no `version`/`date-released`, and `references:`
for every cited work (PMIDs as `identifiers: [{type: other, value: "<digits>"}]` so the checker
verifies them), with **authors exactly as Crossref/DataCite list them** (all of them, in order; a
consortium as `name:`). Validate with `cffconvert --validate`.

## Test on real data

Demo data (read-only, do not modify) is under `~/code/pennsieve/workflow-scalp-eeg/data/` (see
conventions.md, "Demo data", and `data/README.md`). If your folder is not there yet, build and test
on the synthetic fixture first, then check again before you finish. Upstream outputs are in
`data/work/<demo>/<app>/` (`data/work/siena/eeg-prep/eeg` is what every analysis app reads); if
what you need isn't there yet, use your fixture generator and say so; once you have run on real
data, put your output under `data/work/<demo>/<your app>/` for the builders after you.

Local Docker has **8 GB shared with other builders running in parallel**: test on 2–4 recordings
and short windows, give `docker run` a `--memory` limit (≤ 3 GB unless you must), measure peak
memory (`/sys/fs/cgroup/memory.peak` or `docker stats`), remove your containers and dangling
images, and use `docker build --platform linux/amd64`. For one long recording (Siena PN06 is
hours) measure once, at the end, and report the number.

## Git

`git init -b main` (if not yet a repo), commit with clear messages ending with
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, commit as
`-c user.name="Joost Wagenaar" -c user.email="1605953+jwagenaar@users.noreply.github.com"`, and add
the remote `git@github.com:pennsieve-apps/<repo>.git`. **Do not push, tag or create releases**: the
coordinator pushes and releases.

## Report back

Short: repo path, commits, ports and parameters as built, what you ran it on and the results
(numbers), measured memory/time, image size(s), chosen cpu/memory, citations with DOIs/PMIDs and
how you verified them (the verify-citations.py final line), deviations from conventions.md, open
problems.
