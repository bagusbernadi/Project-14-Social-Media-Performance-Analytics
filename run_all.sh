#!/usr/bin/env bash
# Jalankan seluruh pipeline dari data/raw/ (zip dari DataCenter) sampai outputs/.
set -euo pipefail
rm -rf data/raw/fb data/raw/yt data/clean outputs/*.csv
for s in src/01_ingest.py src/02_clean.py src/03_analysis.py src/04_sql_kpi.py; do
  python3 -I "$s"
done
