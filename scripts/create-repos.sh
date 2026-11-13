#!/usr/bin/env bash
# Creates the public GitHub repositories of the scalp EEG workflows in the pennsieve-apps
# organization (empty; each app is pushed from its own checkout). Idempotent: a repo that already
# exists is skipped.
set -euo pipefail
ORG=pennsieve-apps
while IFS='|' read -r name desc; do
  if gh repo view "$ORG/$name" >/dev/null 2>&1; then echo "exists: $ORG/$name"; continue; fi
  gh repo create "$ORG/$name" --public -d "$desc"
done <<'LIST'
workflow-scalp-eeg|Pennsieve workflows for clinical scalp EEG: interictal biomarkers (spectral, spikes, sleep, connectivity) and seizure detection and monitoring
eeg-prep|Pennsieve app: reads clinical scalp EEG (BIDS-EEG, EDF, BrainVision, Nihon Kohden, Natus), finds bad channels, filters, re-references, removes artifacts (ICA + ICLabel) and writes one BIDS-EEG derivative
eeg-spectral|Pennsieve app: spectral biomarkers of scalp EEG: band power, aperiodic exponent (specparam), posterior dominant rhythm, hemispheric asymmetry and slowing indices
eeg-spikes|Pennsieve app: interictal epileptiform discharge (spike) detection on scalp EEG with rates per channel, lateralisation and rates per sleep stage
eeg-seizures|Pennsieve app: seizure detection on scalp EEG in the SzCORE format, scored with timescoring against annotations
eeg-sleep|Pennsieve app: sleep staging, sleep statistics, spindles and slow waves from scalp EEG (YASA)
eeg-connectivity|Pennsieve app: sensor-space functional connectivity (wPLI, imaginary coherence, envelope correlation), graph measures and hemispheric asymmetry of scalp EEG
eeg-report|Pennsieve app: HTML and PDF report for the scalp EEG workflows
LIST
