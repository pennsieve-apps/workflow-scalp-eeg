# Demo data for the scalp EEG workflows

Staged by `scripts/fetch-sample-data.sh` (everything here except this file is gitignored). Read
only; apps write their outputs under `work/<demo>/<app>/`.

| Folder | What | Source and licence |
|---|---|---|
| `siena/BIDS_Siena/` | BIDS Siena Scalp EEG Database: 14 adults with focal epilepsy (`sub-00` … `sub-17`, 14 folders), `participants.tsv` with age and sex; 41 EDF runs (`sub-XX_ses-01_task-szMonitoring_run-NN_eeg.edf`, tens of minutes to hours each), **19 channels in average reference** (`Fp1-Avg` … `T6-Avg`, old 10-20 names T3/T4/T5/T6 for T7/T8/P7/P8) **at 256 Hz** (the BIDS conversion resampled the 512 Hz originals), plus an `EDF Annotations` channel; seizures as HED-SCORE rows in `*_events.tsv` (`onset, duration, eventType` e.g. `sz_foc_ia`, `confidence, channels, dateTime, recordingDuration`); 4.7 GB | Zenodo 10640762 (Jonathan Dan, Paolo Detti; the Zenodo record says CC BY 4.0, `dataset_description.json` says ODC-By 1.0: both allow redistribution with attribution). Original: Detti P. Siena Scalp EEG Database v1.0.0, PhysioNet, doi:10.13026/5d4a-j060; cite also Detti et al. 2020 Processes doi:10.3390/pr8070846 and Goldberger et al. 2000 Circulation |
| `chbmit/chb01/` | CHB-MIT Scalp EEG Database, subject chb01 (paediatric, 11 y, female): 42 one-hour EDFs (`chb01_01.edf` …), **23 bipolar channels** (`FP1-F7`, …, longitudinal bipolar, no referential data) **at 256 Hz**, 7 seizures listed in `chb01-summary.txt` (file name, seizure start/end in seconds) and as `*.edf.seizures` sidecars; 1.6 GB, SHA-256 verified against PhysioNet's `SHA256SUMS.txt` | PhysioNet doi:10.13026/C2K01R, ODC-By 1.0 (`LICENSE.txt`). Cite Shoeb 2009 (MIT thesis), Guttag 2010 (database) and Goldberger et al. 2000 |
| `ds003555/` | OpenNeuro ds003555 v1.0.1, "Dataset of EEG recordings of pediatric patients with epilepsy based on the 10-20 system": first 3 of 30 children (`sub-01` … `sub-03`), first 3 h of sleep EEG, 10-20, EDF; the authors' scalp HFO markings under `derivatives/` | CC0; Cserpan D, Boran E, Rosch R, Lo Biundo SP, Ramantani G, Sarnthein J (OpenNeuro doi:10.18112/openneuro.ds003555.v1.0.1); paper Cserpan et al. 2021 Brain Communications doi:10.1093/braincomms/fcab052 |

Not staged (too large for the demo; fetch on request): vEpiSet (figshare doi:10.6084/m9.figshare.28069568.v2,
CC BY 4.0, 16 GB zip of 4-s .mat epochs with expert IED labels, 84 patients, 29 channels) for validating
eeg-spikes; the full CHB-MIT and Siena databases; MPI-LEMON (PDDL) as a normative reference.

Conventions for the recording ids these produce: Siena `sub-00_ses-01_task-szMonitoring_run-01`; CHB-MIT
(loose EDFs) `sub-chb01_task-eeg_run-03` (eeg-prep derives the subject from the folder/file name and the
run from the file number); ds003555 from its BIDS names.
