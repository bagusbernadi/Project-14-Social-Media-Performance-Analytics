"""Bandingkan VADER dan label dataset dengan label manual (Q9, H5). Jalankan setelah label diisi.

Input : data/sample/manual_label_sample.csv (kolom label_manual: positive/neutral/negative)
        data/sample/manual_label_key.csv
Output: outputs/manual_eval.csv, outputs/manual_confusion.csv
"""
import sys

import pandas as pd

VALID = {"positive", "neutral", "negative"}


def main():
    s = pd.read_csv("data/sample/manual_label_sample.csv", keep_default_na=False)
    k = pd.read_csv("data/sample/manual_label_key.csv")
    m = s.merge(k, on="sample_id", how="left", validate="one_to_one")
    bad = set(m.label_manual.unique()) - VALID - {""}
    if bad:
        sys.exit(f"label tidak valid: {sorted(bad)}")
    if (m.label_manual == "").any():
        sys.exit(f"masih {int((m.label_manual == '').sum())} label kosong")
    rows = []
    for name, col in [("vader", "vader_label"), ("dataset", "label_dataset")]:
        acc = float((m.label_manual == m[col]).mean())
        rows.append([name, len(m), acc])
    pd.DataFrame(rows, columns=["pembanding", "n", "akurasi_vs_manual"]).to_csv("outputs/manual_eval.csv", index=False)
    pd.crosstab(m.label_manual, m.vader_label).to_csv("outputs/manual_confusion.csv")
    print(pd.DataFrame(rows, columns=["pembanding", "n", "akurasi_vs_manual"]).to_string(index=False))


if __name__ == "__main__":
    main()
