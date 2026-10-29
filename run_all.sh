#!/usr/bin/env bash
# Jalankan seluruh pipeline dari data/raw/ (zip dari DataCenter) sampai outputs/, lalu uji dashboard.
set -euo pipefail
rm -rf data/raw/fb data/raw/yt data/clean data/sample outputs/*.csv
for s in src/01_ingest.py src/02_clean.py src/03_analysis.py src/04_sql_kpi.py src/05_manual_sample.py src/07_eval_llm_ref.py src/08_dashboard_export.py; do
  python3 -I "$s" > /dev/null
done
python3 -I -m pytest -q tests/test_dashboard.py
