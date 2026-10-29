"""Ekspor tabel agregat untuk dashboard. Dashboard hanya membaca outputs/dash_*.csv.

Input : data/clean/fb_posts.csv, outputs/*.csv hasil 03_analysis.py
Output: outputs/dash_fb_type.csv, dash_fb_weekday_hour.csv, dash_fb_hour_bucket.csv,
        dash_fb_summary.csv, dash_yt_keyword.csv, dash_answers.csv
"""
import pandas as pd

MIN_N = 5


def main():
    fb = pd.read_csv("data/clean/fb_posts.csv")
    fb["er"] = fb.total / fb.reach

    t = pd.read_csv("outputs/fb_type_er.csv")
    t.to_csv("outputs/dash_fb_type.csv", index=False)

    wh = pd.read_csv("outputs/fb_weekday_hour.csv")
    wh.to_csv("outputs/dash_fb_weekday_hour.csv", index=False)

    hb = fb.groupby("hour_bucket").er.agg(n="size", median_er="median").reset_index()
    hb = hb[hb.n >= MIN_N].sort_values("hour_bucket", kind="mergesort")
    hb.to_csv("outputs/dash_fb_hour_bucket.csv", index=False)

    summary = pd.DataFrame([{
        "n_post": len(fb),
        "median_er_semua": fb.er.median(),
        "mean_er_semua": fb.er.mean(),
        "reach_rata2": fb.reach.mean(),
        "reach_median": fb.reach.median(),
        "n_viral_fb": int(fb.viral.sum()),
        "n_paid": int((fb.paid_label == "berbayar").sum()),
    }])
    summary.to_csv("outputs/dash_fb_summary.csv", index=False)

    k = pd.read_csv("outputs/yt_keyword_er.csv")
    s = pd.read_csv("outputs/yt_keyword_sent.csv")
    yk = k.merge(s[["keyword", "neg_dataset", "pos_dataset", "neg_vader"]], on="keyword", how="left", validate="one_to_one")
    yk = yk.sort_values(["median_er", "keyword"], ascending=[False, True], kind="mergesort")
    yk.to_csv("outputs/dash_yt_keyword.csv", index=False)

    a = pd.read_csv("outputs/answers.csv")
    a.to_csv("outputs/dash_answers.csv", index=False)
    print("ekspor dashboard selesai")


if __name__ == "__main__":
    main()
