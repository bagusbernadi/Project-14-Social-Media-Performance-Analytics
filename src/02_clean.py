"""Cleaning dua dataset dan skor VADER untuk komentar YouTube.

Input : data/raw/fb/dataset_Facebook.csv, data/raw/yt/videos-stats.csv, data/raw/yt/comments.csv
Output: data/clean/fb_posts.csv, data/clean/yt_videos.csv, data/clean/yt_comments.csv,
        outputs/cleaning_log.csv

Asumsi (ditulis di docs/definitions.md):
- Kode Sentiment Kaggle: 2 = positive, 1 = neutral, 0 = negative (tidak tertulis di sumber).
- Viral: ER > Q3 + 3*IQR, dihitung per platform.
- Batas VADER compound: >= 0.05 positive, <= -0.05 negative, selainnya neutral.
"""
import csv
import sys
import html
import os

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

FB_IN = "data/raw/fb/dataset_Facebook.csv"
YT_V_IN = "data/raw/yt/videos-stats.csv"
YT_C_IN = "data/raw/yt/comments.csv"
LOG = []


def log(source, key, action, reason):
    LOG.append([source, str(key), action, reason])


def viral_flag(er):
    q1, q3 = er.quantile([0.25, 0.75])
    cut = q3 + 3 * (q3 - q1)
    return er > cut, cut


def clean_fb():
    d = pd.read_csv(FB_IN, sep=";")
    d.columns = ["page_likes", "type", "category", "month", "weekday", "hour", "paid", "reach",
                 "impressions", "engaged", "consumers", "consumptions", "imp_fans", "reach_fans",
                 "engaged_fans", "comment", "like", "share", "total"]
    d = d.reset_index().rename(columns={"index": "post_id"})
    d["post_id"] = d["post_id"] + 1
    for _, r in d[d[["paid", "like", "share"]].isna().any(axis=1)].iterrows():
        cols = [c for c in ["paid", "like", "share"] if pd.isna(r[c])]
        log("fb", r.post_id, "dipertahankan, kolom kosong", "kosong: " + ",".join(cols))
    for _, r in d[d.total == 0].iterrows():
        log("fb", r.post_id, "dipertahankan, total 0", "total interaksi 0 (ER = 0)")
    if (d.reach <= 0).any():
        sys.exit("reach <= 0 ditemukan; perlu aturan sebelum lanjut")
    d["er"] = d.total / d.reach
    d["viral"], cut_fb = viral_flag(d.er)
    d["hour_bucket"] = pd.cut(d.hour, bins=[-1, 4, 10, 15, 19, 24],
                              labels=["Malam 00-04", "Pagi 05-10", "Siang 11-15", "Sore 16-19", "Malam 20-23"]).astype(str)
    d["jam_kerja_08_17"] = d.hour.between(8, 17)
    d["paid_label"] = d.paid.map({0.0: "organik", 1.0: "berbayar"}).fillna("tidak diketahui")
    d.to_csv("data/clean/fb_posts.csv", index=False)
    return cut_fb, int(d.viral.sum())


def clean_yt():
    v = pd.read_csv(YT_V_IN)
    v = v.rename(columns={"Unnamed: 0": "row_no", "Title": "title", "Video ID": "video_id",
                          "Published At": "published_date", "Keyword": "keyword",
                          "Likes": "likes", "Comments": "comments", "Views": "views"})
    v["title"] = v["title"].fillna("").map(html.unescape)
    for _, r in v[v[["likes", "comments", "views"]].isna().any(axis=1)].iterrows():
        log("yt_video", r.video_id, "dibuang", "likes/comments/views kosong")
    v = v.dropna(subset=["likes", "comments", "views"])
    dup = v.duplicated(subset=["video_id"], keep="first")
    for _, r in v[dup].iterrows():
        log("yt_video", r.video_id, "dibuang", "video_id ganda (baris pertama dipertahankan)")
    v = v[~dup].copy()
    for c in ["likes", "comments", "views"]:
        v[c] = v[c].astype("int64")
    v["er"] = (v.likes + v.comments) / v.views
    v["viral"], cut_yt = viral_flag(v.er)
    v = v.sort_values(["video_id"], kind="mergesort")
    v.to_csv("data/clean/yt_videos.csv", index=False)

    c = pd.read_csv(YT_C_IN)
    c = c.rename(columns={"Unnamed: 0": "comment_row", "Video ID": "video_id", "Comment": "text",
                          "Likes": "likes", "Sentiment": "label_dataset_code"})
    empty = c.text.isna() | (c.text.astype(str).str.strip() == "")
    for _, r in c[empty].iterrows():
        log("yt_comment", r.comment_row, "dibuang", "teks kosong")
    c = c[~empty].copy()
    c["label_dataset"] = c.label_dataset_code.map({2.0: "positive", 1.0: "neutral", 0.0: "negative"})
    c["text"] = c.text.astype(str).map(html.unescape)
    analyzer = SentimentIntensityAnalyzer()
    c["vader_compound"] = c.text.map(lambda t: analyzer.polarity_scores(t)["compound"])
    c["vader_label"] = pd.cut(c.vader_compound, bins=[-1.01, -0.05, 0.05, 1.01],
                              labels=["negative", "neutral", "positive"], right=False).astype(str)
    c = c.sort_values(["video_id", "comment_row"], kind="mergesort")
    c.to_csv("data/clean/yt_comments.csv", index=False)
    return cut_yt, int(v.viral.sum()), len(v), len(c)


def main():
    os.makedirs("data/clean", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    cut_fb, n_viral_fb = clean_fb()
    cut_yt, n_viral_yt, n_v, n_c = clean_yt()
    with open("outputs/cleaning_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sumber", "kunci", "aksi", "alasan"])
        w.writerows(sorted(LOG, key=lambda r: (r[0], r[1], r[2], r[3])))
    print(f"fb viral cut {cut_fb:.4f}, viral {n_viral_fb}")
    print(f"yt viral cut {cut_yt:.4f}, viral {n_viral_yt}, videos {n_v}, comments {n_c}")
    print(f"log rows {len(LOG)}")


if __name__ == "__main__":
    import sys
    main()
