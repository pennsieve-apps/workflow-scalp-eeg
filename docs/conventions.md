# Conventions shared by the scalp EEG apps

Every app of the scalp EEG workflows (Scalp EEG Interictal Biomarkers; Scalp EEG Seizure Detection &
Monitoring) follows this contract, so any step's output can be linked to any other step's input
without glue, and so every app also works on data that never went through the other apps: a
hospital's routine or long-term EEG as exported (EDF, BrainVision, Nihon Kohden, Natus), or any
BIDS-EEG dataset on OpenNeuro.

The sibling family is the epilepsy iEEG workflows (`~/code/pennsieve/workflow-epilepsy-ieeg`); the
tables here keep the same shapes (`recording_id` + `channel` long format, the shared `features.csv`)
so the two families' outputs can sit side by side. Where the two differ, this file wins for scalp apps.

## Apps

| App | Workflow | What | Compute |
|---|---|---|---|
| `eeg-prep` | both | Read clinical scalp EEG (BIDS-EEG, EDF/EDF+, BDF, BrainVision, EEGLAB `.set`, FIF, Nihon Kohden `.EEG`, Natus/Nicolet `.e`), keep the EEG channels, canonical 10-20 names and positions, bad channels (pyprep), filters, re-reference, artifact handling (ICA + ICLabel, optional ASR), bad segments, labels; one BIDS-EEG derivative | standard |
| `eeg-spectral` | Biomarkers | Band power, aperiodic exponent and periodic peaks (specparam), posterior dominant rhythm, hemispheric asymmetry (revised Brain Symmetry Index), slowing indices | standard (Lambda-eligible if it fits) |
| `eeg-spikes` | both | Interictal epileptiform discharges (spikes) per channel, multi-channel spike events, rates, lateralisation; rates per sleep stage when `eeg-sleep` is linked | standard |
| `eeg-seizures` | Seizure | Seizure detection: events in the SzCORE format, scored against annotations with `timescoring` when they exist | standard |
| `eeg-sleep` | both | Sleep staging (YASA), sleep statistics, spindles and slow waves | standard |
| `eeg-connectivity` | Biomarkers | Sensor-space functional connectivity (wPLI, imaginary coherence, orthogonalised envelope correlation), graph measures, hemispheric asymmetry | standard |
| `eeg-report` | both | HTML report of whatever steps are linked into it, plus a tables folder | standard (Lambda-eligible if it fits) |

Repo names carry **no `processor-` prefix**. Ports, parameters and file layouts are below.

Workflows:

- **Scalp EEG Interictal Biomarkers:** `eeg-prep → {eeg-spectral, eeg-connectivity, eeg-sleep → eeg-spikes} → eeg-report`
- **Scalp EEG Seizure Detection & Monitoring:** `eeg-prep → {eeg-seizures, eeg-sleep → eeg-spikes} → eeg-report`

## Runtime contract (Pennsieve processors)

- Read from `$INPUT_DIR`, write to `$OUTPUT_DIR`. Parameters arrive as environment variables named
  as in `app.yml`. Scratch goes to `$TMPDIR` (and `$HOME`), never a hard-coded `/tmp/...` path: on
  Lambda the file system is read-only except `INPUT_DIR`, `OUTPUT_DIR`, `HOME`, `TMPDIR` (see the
  builder brief, "How a Lambda step runs").
- One output port: it is the whole `$OUTPUT_DIR`. Two or more outputs: each is written to
  `$OUTPUT_DIR/<port>/`.
- **Everything an analysis app writes into a port lives under one top folder named after the app**:
  `$OUTPUT_DIR/[<port>/]<app>/...`, e.g. `eeg-spikes/spikes.csv`. This keeps `provenance.json`,
  `summary.json` and figures of different steps from colliding when several steps are linked into
  one input port (the report). An app that can run more than once in a workflow adds a `LABEL`
  level below it (`<app>/<label>/...`; `LABEL` defaults to empty = no extra level). The one
  exception is `eeg-prep`: its `eeg` port **is** the BIDS derivative (`dataset_description.json`
  at the port root, like a BIDS dataset), with its `provenance.json` next to it.
- Inputs with several ports use `placement: subfolder` (each arrives at `$INPUT_DIR/<port>/`).
  Apps must also work when everything is merged side by side at the root of `$INPUT_DIR`, so they
  find files **by name and content, recursively, following symlinks** (INPUT_DIR entries are
  symlinks), never by fixed paths. Readers find tables by file name anywhere under a port.
- Port names: lowercase letters, digits and `-`.
- Each app's top folder gets a `provenance.json` (exact keys below) and a `summary.json` with the
  headline numbers and the figures the report shows.
- A recording that fails is logged and skipped; the step fails only when every recording failed or
  no input was found. Exit codes: `0` ok, `1` no usable input / every recording failed, `2` bad
  parameters.
- Logs go to stdout: one line per recording with channel counts and timings, plus progress at least
  every minute during long steps (ICA on hours of EEG, staging, seizure detection) so a run never
  looks hung.
- Memory: process one recording at a time, and read long recordings in windows. Never load every
  recording at once. A 24 h, 25-channel, 512 Hz recording is 4.4 GB as float32: every step reads
  by window (`WINDOW_S`) or by channel, and `eeg-prep` writes EDF+ incrementally. Each app's README
  states the peak memory measured on the demo data.
- Threads: `THREADS` (default `0` = from the cgroup CPU quota (v2 `cpu.max`, v1
  `cpu.cfs_quota_us`/`cpu.cfs_period_us`), else the CPU affinity, else the CPU count, **never the
  host's core count**), capped so that an estimated per-worker footprint fits the cgroup memory
  limit (`memory.max`); log the number and why, and keep both in `provenance.json`. Set
  `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMBA_NUM_THREADS` before importing
  numpy. Copy `processor/resources.py` from `~/code/pennsieve/processor-ieeg-hfo`.
- Reproducible: every random step takes `SEED` (default `42`) (ICA, permutations, LightGBM).
- No network at run time. Model weights (ICLabel, YASA's classifiers), fonts, and anything a
  library downloads on first use are fetched **at image build time**, verified by checksum, and
  live under a read-only path in `/opt/<app>/` (never `/tmp` or `HOME`, both replaced at run time
  on Lambda); set the library's cache env vars to point there.
- Runs as uid 1000 on ECS (give it a passwd entry) and as an arbitrary least-privileged user on
  Lambda: work with any uid.

## The data between steps: a BIDS-EEG derivative

`eeg-prep` turns whatever it is given into one BIDS-EEG derivative dataset, and every later step
reads that (and also accepts a plain BIDS-EEG dataset or loose EDF files, so each step can be run
on its own). Layout of the `eeg` output port of `eeg-prep`:

```
dataset_description.json            (BIDS derivative, GeneratedBy eeg-prep)
participants.tsv                    (subject, age, sex, group when known; copied from the source)
recordings.csv                      (index, below)
provenance.json
sub-<label>/[ses-<label>/]eeg/
  <stem>_desc-preproc_eeg.edf       signals after channel selection, filtering, re-referencing and
                                    artifact handling, EDF+ (16-bit, per-channel physical range
                                    from the data; amplitudes in µV)
  <stem>_desc-preproc_eeg.json      BIDS sidecar (SamplingFrequency, EEGReference, PowerLineFrequency,
                                    RecordingDuration, SoftwareFilters, EEGChannelCount, ...)
  <stem>_desc-preproc_channels.tsv  one row per channel kept (columns below)
  <stem>_desc-preproc_events.tsv    events (columns below)
  <stem>_desc-preproc_electrodes.tsv  10-20/10-10 positions (template positions when the source
                                    has none; `space` = `CapTrak`-style template name, e.g. `standard_1005`)
```

`<stem>` is the BIDS entity chain of the source recording
(`sub-PN06_ses-01_task-szMonitoring_run-01`; for loose files, eeg-prep makes one up from the file
name: `sub-chb01_task-eeg_run-03`). A **recording id** is that stem; it is the key in every table
below. A **subject** is the `sub-` label.

### Montage and reference

`eeg-prep` canonicalises channel names to the 10-20/10-10 spelling MNE uses (`Fp1`, `T7` for `T3`,
`P7` for `T5`, `O1`, ...; `EEG Fp1-Ref` → `Fp1`), drops non-EEG channels (ECG, EMG, EOG, respiration,
SpO2, triggers, annotations, empty), and keeps them listed in `qc.csv`. Two cases:

- **Referential recordings** (channels are single electrodes): the output is in the reference
  the `REFERENCE` parameter asks for: `average` (default; the common average of the good EEG
  channels, as SzCORE expects), `linked-ears` (A1/A2 or M1/M2 when present), or `as-recorded`.
  `recordings.csv` `montage` says which. Downstream apps build the longitudinal bipolar montage
  ("double banana") themselves when a method wants it; eeg-prep does not write bipolar data for
  referential recordings.
- **Bipolar-only recordings** (CHB-MIT and many exported clinical files: channels are pairs
  `FP1-F7`): there is no way back to a referential montage, so the output keeps the pairs as
  channels (`Fp1-F7`), `montage` = `bipolar-longitudinal`, and each pair's `contacts` column names
  the two electrodes. Every analysis app must run on both montages and say in `provenance.json`
  which one it saw; a method that needs referential data (`eeg-connectivity` by default,
  `eeg-sleep` when it wants `C4-M1`) says so in its README and either derives what it needs
  (`eeg-sleep` uses the best available central pair) or skips the recording with a reason.

Filtering: notch at the mains frequency and its harmonics (from the sidecar; `LINE_FREQ` to
override, `auto` detects 50 vs 60 Hz from the spectrum), high-pass `HIGHPASS` (default 0.5 Hz),
low-pass `LOWPASS` (default none: eeg-spikes and eeg-spectral want the full band; a user may set
70 Hz). No resampling by default (`RESAMPLE_HZ`, e.g. 256 for seizure models). Artifact handling:
`ARTIFACTS` = `iclabel` (default: ICA on the good channels, components ICLabel calls eye, muscle,
heart, line noise or channel noise with probability ≥ `ICLABEL_THRESHOLD` (0.8) are removed;
needs ≥ 8 channels with positions; skipped with a note otherwise), `asr`, `both`, or `none`.
Removed components are listed in `qc.csv`. Bad segments (amplitude, flat, muscle z-score) go to
`_events.tsv` as `bad_segment` rows; later steps leave them out.

### `recordings.csv`

One row per recording: `recording_id, subject, session, task, run, path` (relative to the port
root), `sfreq, n_channels, n_good, duration_s, montage` (`average` | `linked-ears` |
`as-recorded` | `bipolar-longitudinal`), `reference` (the reference channel name, or `average`),
`kind` (`routine` ≤ 2 h | `long-term` > 2 h | `sleep` | `unknown`), `start_time` (ISO 8601 wall
clock when the source has it, else empty: eeg-seizures needs it for `dateTime` and FP/day,
eeg-sleep for time of night), `n_seizures` (annotated seizures in the source), `source_format`
(`bids-edf`, `edf`, `brainvision`, `eeglab`, `fif`, `nihon-kohden`, `natus`, ...), `age`, `sex`
(from participants.tsv or the EDF header when known, else empty). Then any extra recording-level
columns of `labels.csv` (see "Labels on input").

### `_channels.tsv`

BIDS columns `name, type` (`EEG` | `ECG` | `EOG` | `EMG` | `MISC`, only `EEG` is kept in the data),
`units` (`µV`), `low_cutoff, high_cutoff, sampling_frequency, status` (`good` | `bad`),
`status_description` (why bad), plus `contacts` (`Fp1|F7` for a bipolar pair, the name itself
otherwise), `hemisphere` (`L` | `R` | `Z` midline, from the 10-20 name: odd = left, even = right),
`region` (`frontal` | `temporal` | `central` | `parietal` | `occipital` | `midline`), `x, y, z`
(template head coordinates in metres, MNE's `standard_1005` montage, when the name is a known
10-20/10-10 label) and `original_name` (the name in the source file).

### `_events.tsv`

BIDS `onset, duration, trial_type` plus `source` (`annotation` | `labels.csv` | `eeg-prep`) and
`channels` (comma-separated, empty = all). `trial_type` values used here: `seizure` (onset and
duration as annotated; `duration` empty when the end is unknown), `artifact` (annotated),
`bad_segment` (found by eeg-prep), `eyes_open`, `eyes_closed`, `photic`, `hyperventilation`,
`sleep` / `wake` (annotated states), `lights_off`, `lights_on`. HED-SCORE events of SzCORE-style
BIDS datasets (`eventType` `sz`, `sz-foc`, ...) are read as `seizure` with the HED type kept in an
extra `hed` column. Detections written by later steps are **not** put here (they go to the step's
own tables).

### Labels on input

`eeg-prep` reads labels from BIDS sidecars (`_events.tsv` seizure rows, HED-SCORE columns,
`_channels.tsv` `status`), from EDF+ annotations (text matching `seizure|sz|onset|ictal`, case
insensitive, and the CHB-MIT `-summary.txt` files next to the EDFs), and from an optional
`labels.csv` anywhere in its input with columns `subject, recording_id` (empty = every recording of
the subject), `onset_s, duration_s` (one seizure per row), `trial_type` (default `seizure`), plus
recording-level rows carrying extra columns (e.g. `lateralisation` = `left` | `right` |
`bilateral`, `outcome`), which are carried into `recordings.csv` as columns of the same name.

### Precision

EDF stores 16-bit integers per channel with a physical min/max. `eeg-prep` sets each channel's
range from its own data (robust max of |x| × 1.1, at least ±1 µV), so quantisation is far below
the noise floor of scalp EEG. Amplitudes are in µV.

## Tables written by the analysis steps

All CSV, UTF-8, header row, `.` decimal, long format keyed by `recording_id` (and `channel`: the
`_channels.tsv` name). Times are seconds from the recording start. Windows and events exclude
`bad_segment` and `artifact` intervals unless a parameter says otherwise. Each step writes its
parameters into `provenance.json`.

| Step | Files (under `<app>/`) |
|---|---|
| eeg-spectral | `bandpower.csv` (recording_id, channel, band, abs_power, rel_power, log_power; bands delta 1–4, theta 4–8, alpha 8–13, beta 13–30, gamma 30–45 Hz by default, plus `broadband` 1–45) ; `aperiodic.csv` (recording_id, channel, exponent, offset, knee, r_squared, error, n_peaks); `peaks.csv` (recording_id, channel, cf_hz, power, bandwidth); `pdr.csv` (recording_id, pdr_hz, pdr_amplitude_uv, pdr_left_hz, pdr_right_hz, asymmetry, reactivity, n_eyes_closed_s, method); `asymmetry.csv` (recording_id, pair, band, bsi: the revised BSI per homologous pair and band, plus a `recording` row with the overall rBSI); `slowing.csv` (recording_id, channel, theta_alpha_ratio, delta_theta_over_alpha_beta); `features.csv` (shared shape: `relpow_<band>`, `logpow_<band>`, `aperiodic_exponent`, `aperiodic_offset`, `pdr_hz`, `theta_alpha_ratio`, `bsi`); optionally `windowed.csv` (recording_id, channel, window_start_s, feature, value) when `WINDOWED=true` |
| eeg-spikes | `spikes.csv` (recording_id, channel, time_s, amplitude_uv, duration_ms, detector, sleep_stage when known); `spike_rates.csv` (recording_id, channel, n_spikes, minutes, rate_per_min, detector); `spike_events.csv` (recording_id, event_id, time_s, n_channels, channels, leading_channel, hemisphere); `lateralisation.csv` (recording_id, n_left, n_right, n_midline, laterality_index = (L−R)/(L+R), dominant_region); `rates_by_stage.csv` (recording_id, channel, stage, n_spikes, minutes, rate_per_min) when a hypnogram is linked; `features.csv` (`spikerate_<detector>`) |
| eeg-seizures | `seizures.csv` (recording_id, onset_s, duration_s, confidence, channels, detector); `szcore/<recording_id>.tsv` in the exact SzCORE event format (onset, duration, eventType, confidence, channels, dateTime, recordingDuration); `probability.csv` (recording_id, time_s, probability; one row per `STEP_S`) ; `scores.csv` (recording_id, scope `sample` | `event`, metric sensitivity / precision / f1 / fp_per_day, value) with `timescoring` against the annotated seizures when there are any, plus a `pooled` row |
| eeg-sleep | `hypnogram.csv` (recording_id, epoch, start_s, duration_s, stage W/N1/N2/N3/R, confidence, channel); `sleep_stats.csv` (recording_id, metric, value: TST, SE, SOL, WASO, minutes and percent per stage, latencies); `spindles.csv` (recording_id, channel, start_s, end_s, duration_s, frequency_hz, amplitude_uv, stage); `slow_waves.csv` (recording_id, channel, start_s, end_s, amplitude_uv, frequency_hz, stage) |
| eeg-connectivity | `connectivity.csv` (recording_id, channel_a, channel_b, band, measure, value); `node_strength.csv` (recording_id, channel, band, measure, strength); `graph.csv` (recording_id, band, measure, metric, value: clustering, path_length, global_efficiency, modularity, small_worldness, density at the chosen threshold); `hemisphere.csv` (recording_id, band, measure, left, right, interhemispheric, asymmetry); `features.csv` (`<measure>_<band>` node strength) |
| eeg-report | `report/index.html` (+ `figures/`), `tables/` (copies of every table it found, plus `recordings.csv`) |

### Per-channel features: `features.csv`, the shared shape

Any app that computes one number per channel also writes it as `features.csv`:
`recording_id, channel, feature, value`, one row per channel and feature, `value` empty when not
defined. Feature names are lowercase `<kind>_<qualifier>` (letters, digits, `-`, `_`), the same
prefixes as the iEEG family (`relpow_`, `logpow_`, `coh_`, `spikerate_`), plus the scalp ones
(`aperiodic_`, `pdr_`, `wpli_`, `bsi`). A future `eeg-normative` step z-scores every feature it
finds against a reference in this shape.

## Sleep stages shared between steps

`eeg-sleep` writes `hypnogram.csv` (30 s epochs). `eeg-spikes` takes it through its optional `sleep`
input port and labels each spike with the stage of its epoch, then writes `rates_by_stage.csv`.
Without a hypnogram `eeg-spikes` uses the annotated `sleep`/`wake` events when there are any, else
leaves `sleep_stage` empty and skips `rates_by_stage.csv`. Stages are `W`, `N1`, `N2`, `N3`, `R`;
`NREM` = N1+N2+N3 in summaries.

## Ports

| App | Inputs | Outputs |
|---|---|---|
| eeg-prep | `eeg` (anything readable, subfolder; plus optional `labels.csv`) | `eeg` (the derivative), `qc` (qc.csv, one PNG per recording) |
| eeg-spectral / eeg-connectivity / eeg-seizures / eeg-sleep | `eeg` | the step's tables (one output port named after the step: `spectral`, `connectivity`, `seizures`, `sleep`) |
| eeg-spikes | `eeg`, `sleep` (optional: `hypnogram.csv` from eeg-sleep) | `spikes` |
| eeg-report | `eeg`, `qc`, and any of `spectral, spikes, seizures, sleep, connectivity` (all optional, subfolder) | `report` (index.html + figures), `tables` |

Media types in `app.yml` (platform registry only): EDF `application/edf`, tables `text/csv`,
`text/tab-separated-values`, JSON `application/json`, HTML `text/html`, PNG `image/png`;
BrainVision/EEGLAB/FIF inputs are listed by their registry types where one exists, else
`application/octet-stream`. Check `GET /packages/formats` on api2 before adding a type.

### Tables, figures, summaries

- Figures are PNG, 150 dpi, `<recording_id>_<what>.png`, with the recording id in the title.
- `summary.json` per app top folder (paths in `figures` and `tables` are **relative to the app's
  top folder**; tables are `{"path", "caption"}` like figures; headline numbers are JSON numbers,
  not strings; `recordings` is keyed by `recording_id`): `{"app": ..., "version": ...,
  "recordings": {<recording_id>: {headline numbers}}, "figures": [{"path": ..., "caption": ...}],
  "tables": [...], "warnings": [...]}`. **The report renders the `figures` list in order with its
  captions**, so every app decides which figures matter and explains them in a caption an
  epileptologist understands.

### `provenance.json` (exact keys)

```json
{"app": "eeg-spikes", "version": "0.1.0", "variant": null,
 "tools": {"mne": "1.11.0", "epycom": "0.3.0"},
 "parameters": {"DETECTOR": "janca"},
 "inputs": ["eeg/recordings.csv", "eeg/sub-PN06/ses-01/eeg/sub-PN06_ses-01_task-szMonitoring_run-01_desc-preproc_eeg.edf"],
 "started": "2026-11-12T12:00:00Z", "finished": "...", "wall_seconds": 0.0,
 "peak_rss_mb": 0, "threads": {"requested": 0, "used": 2, "why": "cgroup cpu.max 2"},
 "recordings": {"sub-PN06_ses-01_task-szMonitoring_run-01": {"status": "ok", "seconds": 0.0, "montage": "average"}},
 "citations": ["10.1007/s10548-014-0379-1"],
 "licence_notice": null}
```

`licence_notice` (optional) states usage terms a user must see; `eeg-report` shows it prominently.
`citations` lists the DOIs the report should cite for this step.

## Demo data

Staged by `scripts/fetch-sample-data.sh` under `data/` (gitignored). See `data/README.md` once
staged. Read only; never modify.

| Folder | What | Source |
|---|---|---|
| `data/siena/BIDS_Siena/` | BIDS Siena Scalp EEG Database: 14 adults with focal epilepsy, 41 EDF runs, 19-channel 10-20 EEG already in average reference (`Fp1-Avg`, old names T3/T4/T5/T6), 256 Hz (resampled from 512 Hz by the BIDS conversion), 47 annotated seizures (HED-SCORE events.tsv with wall-clock `dateTime`) | Zenodo 10640762 (Dan et al., CC BY 4.0), from PhysioNet doi:10.13026/5d4a-j060 (Detti et al.) |
| `data/chbmit/chb01/` | CHB-MIT Scalp EEG Database, subject chb01: 42 one-hour EDFs, 23 longitudinal-bipolar channels only (`FP1-F7`, …), 256 Hz, 7 seizures in `chb01-summary.txt` and `*.edf.seizures` | PhysioNet doi:10.13026/C2K01R (ODC-By 1.0) |
| `data/ds003555/` | First 3 of 30 children with epilepsy: 3 h of sleep EEG, 10-20, EDF, with the authors' scalp HFO markings in `derivatives/` | OpenNeuro ds003555 v1.0.1 (CC0; Cserpan et al. 2021) |

Outputs of finished apps on the demo data go to `data/work/<demo>/<app>/` for the builders after
them (e.g. `data/work/siena/eeg-prep/`).

For local tests use a few recordings and short windows unless measuring memory and time; Docker on
the dev Mac has 8 GB and is shared.

## Research notes

`docs/research/1-scalp-eeg-survey.md` (tools, licences, datasets, 2026-11-12) and
`docs/research/citations.md` (every DOI, verified against Crossref/DataCite on 2026-11-12, with
the registry's title and first author; and the corrections to the survey found by that check).
