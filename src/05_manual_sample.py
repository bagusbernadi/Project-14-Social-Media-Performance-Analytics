"""Ambil 200 komentar acak untuk dilabeli manual (Q9, H5). Label dataset dan skor VADER disembunyikan.

Input : data/clean/yt_comments.csv
Output: data/sample/manual_label_sample.csv (kolom label_manual kosong, tidak di-commit)
        data/sample/manual_label_key.csv    (kunci: comment_row -> label dataset & VADER, tidak di-commit)
"""
import os

import pandas as pd

SEED = 20261028
N = 200


def main():
    os.makedirs("data/sample", exist_ok=True)
    c = pd.read_csv("data/clean/yt_comments.csv")
    s = c.sample(n=N, random_state=SEED).sort_values("comment_row", kind="mergesort").reset_index(drop=True)
    s.insert(0, "sample_id", range(1, N + 1))
    out = pd.DataFrame({"sample_id": s.sample_id, "text": s.text, "label_manual": ""})
    out.to_csv("data/sample/manual_label_sample.csv", index=False)
    key = s[["sample_id", "comment_row", "label_dataset", "vader_label"]]
    key.to_csv("data/sample/manual_label_key.csv", index=False)
    print("sampel:", len(out), "| label manual kosong:", int((out.label_manual == "").sum()))


if __name__ == "__main__":
    main()
