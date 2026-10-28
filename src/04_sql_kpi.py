"""Muat data bersih ke DuckDB, jalankan sql/kpi.sql, dan cek silang dengan pandas (Q14).

Output: outputs/sql_vs_pandas.csv
Database: data/clean/p14.duckdb (tidak di-commit, dibuat ulang setiap run)
"""
import os

import duckdb
import pandas as pd

DB = "data/clean/p14.duckdb"
TOL = 1e-12


def main():
    if os.path.exists(DB):
        os.remove(DB)
    con = duckdb.connect(DB)
    con.execute("CREATE TABLE fb_posts AS SELECT * FROM read_csv_auto('data/clean/fb_posts.csv', header=true) ORDER BY post_id")
    con.execute("CREATE TABLE yt_videos AS SELECT * FROM read_csv_auto('data/clean/yt_videos.csv', header=true) ORDER BY video_id")
    con.execute("CREATE TABLE yt_comments AS SELECT * FROM read_csv_auto('data/clean/yt_comments.csv', header=true) ORDER BY video_id, comment_row")
    with open("sql/kpi.sql", encoding="utf-8") as f:
        con.execute(f.read())

    fb_sql = con.execute("SELECT type, n, median_er FROM v_fb_type_median ORDER BY type").df()
    yt_sql = con.execute("SELECT keyword, n, median_er FROM v_yt_keyword_median ORDER BY keyword").df()

    fb = pd.read_csv("data/clean/fb_posts.csv")
    yt = pd.read_csv("data/clean/yt_videos.csv")
    fb_pd = fb.assign(er=fb.total / fb.reach).groupby("type").agg(n=("er", "size"), median_er=("er", "median")).reset_index().sort_values("type")
    yt_pd = yt.assign(er=(yt.likes + yt.comments) / yt.views).groupby("keyword").agg(n=("er", "size"), median_er=("er", "median")).reset_index().sort_values("keyword")

    rows = []
    for name, s, p in [("fb_type", fb_sql.sort_values("type"), fb_pd), ("yt_keyword", yt_sql.sort_values("keyword"), yt_pd)]:
        s = s.reset_index(drop=True)
        p = p.reset_index(drop=True)
        key = s.columns[0]
        assert list(s[key]) == list(p[key]), f"{name}: kunci tidak sama"
        for i in range(len(s)):
            d_med = abs(float(s.median_er[i]) - float(p.median_er[i]))
            rows.append([name, s[key][i], int(s.n[i]), int(p.n[i]), float(s.median_er[i]), float(p.median_er[i]),
                         d_med, d_med <= TOL])
    out = pd.DataFrame(rows, columns=["grup", "kunci", "n_sql", "n_pandas", "median_sql", "median_pandas", "selisih", "sama"])
    out.to_csv("outputs/sql_vs_pandas.csv", index=False)
    con.close()
    print("baris dicek:", len(out), "| semua sama:", bool(out.sama.all()))


if __name__ == "__main__":
    main()
