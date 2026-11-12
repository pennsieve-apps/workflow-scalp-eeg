# Scalp EEG workflows for Pennsieve

Two workflows for epilepsy and neurology research on clinical scalp EEG (routine EEG and long-term
video-EEG monitoring), built from reusable Pennsieve apps in the
[pennsieve-apps](https://github.com/pennsieve-apps) organization:

- **Scalp EEG Interictal Biomarkers:** `eeg-prep → {eeg-spectral, eeg-connectivity, eeg-sleep → eeg-spikes} → eeg-report`
- **Scalp EEG Seizure Detection & Monitoring:** `eeg-prep → {eeg-seizures, eeg-sleep → eeg-spikes} → eeg-report`

| App | What it adds |
|---|---|
| [eeg-prep](https://github.com/pennsieve-apps/eeg-prep) | Reads clinical formats and BIDS-EEG, canonical 10-20 channels, bad channels (pyprep), filters, re-referencing, artifact removal (ICA + ICLabel, optional ASR), labels; one BIDS-EEG derivative + QC |
| [eeg-spectral](https://github.com/pennsieve-apps/eeg-spectral) | Band power, aperiodic exponent and peaks (specparam), posterior dominant rhythm, revised Brain Symmetry Index, slowing ratios |
| [eeg-spikes](https://github.com/pennsieve-apps/eeg-spikes) | Interictal spikes per channel (epycom detectors), multi-channel events, rates, lateralisation, rates per sleep stage |
| [eeg-seizures](https://github.com/pennsieve-apps/eeg-seizures) | Seizure detection in the SzCORE event format, scored with timescoring against annotations |
| [eeg-sleep](https://github.com/pennsieve-apps/eeg-sleep) | Sleep staging (YASA), sleep statistics, spindles, slow waves |
| [eeg-connectivity](https://github.com/pennsieve-apps/eeg-connectivity) | wPLI / imaginary coherence / envelope correlation, graph measures, hemispheric asymmetry |
| [eeg-report](https://github.com/pennsieve-apps/eeg-report) | HTML + PDF report of whatever steps are linked into it |

The contract between the apps is `docs/conventions.md`; `docs/builder-brief.md` and
`docs/review-brief.md` are the briefs the apps were built and reviewed against; the literature and
licence survey and the verified citation table are in `docs/research/`. Workflow definitions are in
`workflow/`.

## Demo data

`scripts/fetch-sample-data.sh` downloads redistributable demo data into `data/` (gitignored): the
BIDS Siena Scalp EEG Database (CC BY 4.0), one CHB-MIT subject (ODC-By 1.0) and three subjects of
OpenNeuro ds003555 (CC0). See `data/README.md` after fetching, and the credits in each app's README.

## Licence

The workflow definitions and scripts here are Apache-2.0. Each app lists the licences of what it
bundles in its `THIRD_PARTY.md`.
