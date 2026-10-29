"""Pembanding berbasis LLM (BUKAN label manual): VADER dan label dataset vs label_llm pada 200 sampel.

Input : data/sample/manual_label_key.csv (dari 05_manual_sample.py), labels/llm_label_200.csv (label dibuat asisten AI, tidak diverifikasi manusia)
Output: outputs/llm_ref_eval.csv, outputs/llm_ref_confusion.csv
Catatan: hasil ini tidak menggantikan label manual. Q9 dan H5 tetap menunggu label manual.
"""
import pandas as pd

k = pd.read_csv("data/sample/manual_label_key.csv")
l = pd.read_csv("labels/llm_label_200.csv")
m = k.merge(l, on="sample_id", validate="one_to_one", suffixes=("", "_llm"))
assert (m.comment_row == m.comment_row_llm).all(), "ID sampel tidak cocok dengan label; sampel berubah"
rows = []
for name, col in [("vader", "vader_label"), ("dataset", "label_dataset")]:
    rows.append([name, len(m), float((m.label_llm == m[col]).mean())])
out = pd.DataFrame(rows, columns=["pembanding", "n", "akurasi_vs_llm_ref"])
out.to_csv("outputs/llm_ref_eval.csv", index=False)
pd.crosstab(m.label_llm, m.vader_label).to_csv("outputs/llm_ref_confusion.csv")
print(out.to_string(index=False))
