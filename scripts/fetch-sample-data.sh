#!/usr/bin/env bash
# Downloads the demo data of the scalp EEG workflows into data/ (gitignored). Every source is
# public, no login, and redistributable:
#   - Siena Scalp EEG Database, BIDS version by Dan et al. (Zenodo 10640762, CC BY 4.0):
#     14 adults with focal epilepsy, 19-channel 10-20 EEG, 512 Hz, 47 annotated seizures,
#     HED-SCORE events TSV. Original: Detti et al., PhysioNet doi:10.13026/5d4a-j060.
#   - CHB-MIT Scalp EEG Database (PhysioNet doi:10.13026/C2K01R, ODC-By 1.0): one paediatric
#     subject (chb01 by default), 23 bipolar channels, 256 Hz, seizure annotations.
#   - OpenNeuro ds003555 (CC0, doi:10.18112/openneuro.ds003555.v1.0.1): sleep EEG of children
#     with epilepsy, with scalp HFO markings (Cserpan et al. 2021); the first 3 subjects by default.
# Usage: scripts/fetch-sample-data.sh [out-dir]   (env: CHB_SUBJECTS="chb01", DS003555_SUBJECTS="01 02 03")
set -euo pipefail
OUT="${1:-data}"; mkdir -p "$OUT"
CHB_SUBJECTS="${CHB_SUBJECTS:-chb01}"
DS003555_SUBJECTS="${DS003555_SUBJECTS:-01 02 03}"

# Siena (BIDS)
if [ ! -d "$OUT/siena/BIDS_Siena" ] && [ ! -f "$OUT/siena/dataset_description.json" ]; then
  mkdir -p "$OUT/siena"
  echo "fetch Siena BIDS (4.3 GB)"
  curl -L --retry 5 -C - -o "$OUT/siena/BIDS_Siena.zip" "https://zenodo.org/records/10640762/files/BIDS_Siena.zip?download=1"
  want=$(curl -sS "https://zenodo.org/api/records/10640762" | python3 -c "import json,sys; print([f['checksum'] for f in json.load(sys.stdin)['files'] if f['key']=='BIDS_Siena.zip'][0])")
  have="md5:$(md5 -q "$OUT/siena/BIDS_Siena.zip" 2>/dev/null || md5sum "$OUT/siena/BIDS_Siena.zip" | cut -d' ' -f1)"
  [ "$want" = "$have" ] || { echo "Siena checksum mismatch: $want vs $have"; exit 1; }
  (cd "$OUT/siena" && unzip -q BIDS_Siena.zip && rm BIDS_Siena.zip)
fi

# CHB-MIT, selected subjects, straight from PhysioNet
for s in $CHB_SUBJECTS; do
  d="$OUT/chbmit/$s"; mkdir -p "$d"
  base="https://physionet.org/files/chbmit/1.0.0"
  curl -sS -L --retry 5 -o "$OUT/chbmit/SHA256SUMS.txt" "$base/SHA256SUMS.txt"
  for f in $(grep -E "^[0-9a-f]+ +$s/" "$OUT/chbmit/SHA256SUMS.txt" | awk '{print $2}'); do
    [ -f "$OUT/chbmit/$f" ] && continue
    echo "fetch $f"; curl -sS -L --retry 5 -o "$OUT/chbmit/$f" "$base/$f"
  done
  (cd "$OUT/chbmit" && grep -E " +$s/" SHA256SUMS.txt | shasum -a 256 -c --quiet) || { echo "CHB-MIT checksum mismatch"; exit 1; }
done
curl -sS -L -o "$OUT/chbmit/LICENSE.txt" "https://physionet.org/files/chbmit/1.0.0/LICENSE.txt" || true

# ds003555, selected subjects, from the OpenNeuro S3 bucket (public)
mkdir -p "$OUT/ds003555"
for f in dataset_description.json participants.tsv participants.json README CHANGES; do
  aws s3 cp --no-sign-request "s3://openneuro.org/ds003555/$f" "$OUT/ds003555/$f" --only-show-errors || true
done
for s in $DS003555_SUBJECTS; do
  aws s3 sync --no-sign-request "s3://openneuro.org/ds003555/sub-$s/" "$OUT/ds003555/sub-$s/" --only-show-errors
done
echo "done: $(du -sh "$OUT" | cut -f1) in $OUT"
