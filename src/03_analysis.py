"""Analisis Q1-Q13 dari data/clean/. Semua angka dihitung di sini dan ditulis ke outputs/.

Output:
  outputs/answers.csv          ringkasan per pertanyaan (nilai, CI, p, n, catatan)
  outputs/fb_type_er.csv       median ER per tipe (Q1) + CI bootstrap
  outputs/fb_pairwise.csv      Mann-Whitney antar tipe, koreksi Holm (Q2)
  outputs/fb_weekday_hour.csv  median ER hari x jam, n >= 5 saja (Q4)
  outputs/fb_type_time.csv     median ER tipe x kelompok jam (Q5)
  outputs/yt_keyword_er.csv    median ER per keyword + CI (Q6)
  outputs/yt_keyword_sent.csv  porsi sentimen per keyword (Q7, Q11)
  outputs/yt_vader_confusion.csv  VADER vs label dataset (Q9)
  outputs/sensitivity.csv      uji sensitivitas (Q13, asumsi jam kerja, mean vs median)
"""
import os

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20261028
B = 5000
MIN_N = 5
rng = np.random.default_rng(SEED)
ANS = []


def boot_ci(x, stat=np.median):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return np.nan, np.nan
    idx = rng.integers(0, len(x), size=(B, len(x)))
    s = stat(x[idx], axis=1)
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def holm(pvals):
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p, kind="mergesort")
    adj = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj


def add(q, metrik, nilai, lo=np.nan, hi=np.nan, p=np.nan, n=np.nan, catatan=""):
    ANS.append([q, metrik, nilai, lo, hi, p, n, catatan])


def fmt(x):
    return "" if pd.isna(x) else round(float(x), 6)


os.makedirs("outputs", exist_ok=True)
fb = pd.read_csv("data/clean/fb_posts.csv")
yt = pd.read_csv("data/clean/yt_videos.csv")
yc = pd.read_csv("data/clean/yt_comments.csv")

# ---------- Facebook: Q1, Q2 ----------
rows = []
for t, g in fb.groupby("type"):
    lo, hi = boot_ci(g.er)
    rows.append([t, len(g), g.er.median(), lo, hi, g.er.mean()])
tt = pd.DataFrame(rows, columns=["type", "n", "median_er", "ci_low", "ci_high", "mean_er"])
tt = tt.sort_values(["median_er", "type"], ascending=[False, True], kind="mergesort")
tt.to_csv("outputs/fb_type_er.csv", index=False)
for _, r in tt.iterrows():
    add("Q1", f"median ER {r.type}", fmt(r.median_er), fmt(r.ci_low), fmt(r.ci_high), n=r.n,
        catatan="bootstrap percentile 95%, 5000 resample")
groups = [g.er.values for _, g in fb.groupby("type")]
H, p_kw = stats.kruskal(*groups)
add("Q2", "Kruskal-Wallis ER antar tipe", fmt(H), p=fmt(p_kw), n=len(fb))

pairs = []
types = sorted(fb.type.unique())
for i in range(len(types)):
    for j in range(i + 1, len(types)):
        a = fb[fb.type == types[i]].er
        b = fb[fb.type == types[j]].er
        if len(a) < MIN_N or len(b) < MIN_N:
            pairs.append([types[i], types[j], len(a), len(b), np.nan, np.nan])
            continue
        u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        pairs.append([types[i], types[j], len(a), len(b), u, p])
pw = pd.DataFrame(pairs, columns=["tipe_a", "tipe_b", "n_a", "n_b", "U", "p_raw"])
ok = pw.p_raw.notna()
pw["p_holm"] = np.nan
pw.loc[ok, "p_holm"] = holm(pw.loc[ok, "p_raw"])
pw.to_csv("outputs/fb_pairwise.csv", index=False)
for _, r in pw[ok].iterrows():
    add("Q2", f"MWU {r.tipe_a} vs {r.tipe_b}", "", p=fmt(r.p_holm), n=f"{r.n_a}/{r.n_b}",
        catatan="p disesuaikan Holm (6 pasang)")

# H1: Status + Video vs Photo + Link
hi_grp = fb[fb.type.isin(["Status", "Video"])].er
lo_grp = fb[fb.type.isin(["Photo", "Link"])].er
u, p = stats.mannwhitneyu(hi_grp, lo_grp, alternative="greater")
add("H1", "Status+Video > Photo+Link (one-sided MWU)", fmt(hi_grp.median() - lo_grp.median()),
    p=fmt(p), n=f"{len(hi_grp)}/{len(lo_grp)}",
    catatan="selisih median ER (Status+Video) - (Photo+Link); arah hipotesis diuji")

# ---------- Facebook: Q3 paid vs organic ----------
pd_ = fb[fb.paid_label == "berbayar"]
og = fb[fb.paid_label == "organik"]
u, p_er = stats.mannwhitneyu(pd_.er, og.er, alternative="two-sided")
u2, p_rc = stats.mannwhitneyu(pd_.reach, og.reach, alternative="greater")
add("Q3", "median ER berbayar - organik", fmt(pd_.er.median() - og.er.median()), p=fmt(p_er),
    n=f"{len(pd_)}/{len(og)}", catatan="MWU dua sisi; missing paid dikeluarkan")
add("Q3", "reach berbayar > organik (MWU satu sisi)", fmt(pd_.reach.median() - og.reach.median()),
    p=fmt(p_rc), n=f"{len(pd_)}/{len(og)}", catatan="H3 bagian reach")

# ---------- Facebook: Q4, Q5, H2 ----------
fb["weekday"] = fb.weekday.astype(int)
fb["hour"] = fb.hour.astype(int)
wh = fb.groupby(["weekday", "hour"]).er.agg(["size", "median"]).reset_index()
wh = wh[wh["size"] >= MIN_N].rename(columns={"size": "n", "median": "median_er"})
wh.to_csv("outputs/fb_weekday_hour.csv", index=False)
best = wh.sort_values(["median_er", "weekday", "hour"], ascending=[False, True, True], kind="mergesort").head(3)
for _, r in best.iterrows():
    add("Q4", f"median ER tertinggi hari {r.weekday} jam {r.hour}", fmt(r.median_er), n=r.n,
        catatan=f"hanya sel n>=5; {len(wh)} sel dari {fb.groupby(['weekday','hour']).ngroups} sel")
kelompok = fb.groupby("hour_bucket").er.agg(["size", "median"]).reset_index()
kelompok.to_csv("outputs/fb_hour_bucket.csv", index=False)
H, p_hb = stats.kruskal(*[g.er.values for _, g in fb.groupby("hour_bucket")])
add("Q4", "Kruskal-Wallis ER antar kelompok jam", fmt(H), p=fmt(p_hb), n=len(fb))

tt_time = fb.groupby(["type", "hour_bucket"]).er.agg(["size", "median"]).reset_index()
tt_time = tt_time[tt_time["size"] >= MIN_N].rename(columns={"size": "n", "median": "median_er"})
tt_time.to_csv("outputs/fb_type_time.csv", index=False)
add("Q5", "sel tipe x kelompok jam dengan n>=5", len(tt_time), n=len(fb),
    catatan="sel kecil; tidak dipakai untuk kesimpulan kuat")

# H2: jam kerja (asumsi 08-17) vs di luar; ASUMSI, diuji sensitivitasnya di bawah
jk = fb[fb.jam_kerja_08_17].er
lk = fb[~fb.jam_kerja_08_17].er
u, p_h2 = stats.mannwhitneyu(lk, jk, alternative="greater")
add("H2", "di luar jam kerja > jam kerja (median selisih)", fmt(lk.median() - jk.median()),
    p=fmt(p_h2), n=f"{len(lk)}/{len(jk)}", catatan="asumsi jam kerja 08-17; lihat sensitivity.csv")

# ---------- YouTube: Q6, Q7, Q8, Q11 ----------
kw = []
for k, g in yt.groupby("keyword"):
    lo, hi = boot_ci(g.er)
    kw.append([k, len(g), g.er.median(), lo, hi])
kw = pd.DataFrame(kw, columns=["keyword", "n", "median_er", "ci_low", "ci_high"])
kw = kw.sort_values(["median_er", "keyword"], ascending=[False, True], kind="mergesort")
kw.to_csv("outputs/yt_keyword_er.csv", index=False)
for _, r in kw.head(3).iterrows():
    add("Q6", f"median ER keyword {r.keyword}", fmt(r.median_er), fmt(r.ci_low), fmt(r.ci_high), n=r.n,
        catatan="3 teratas; ER = (likes+comments)/views")
H, p_kwy = stats.kruskal(*[g.er.values for _, g in yt.groupby("keyword")])
add("Q6", "Kruskal-Wallis ER antar keyword", fmt(H), p=fmt(p_kwy), n=len(yt))

sent = yc.groupby(["video_id"]).agg(n_c=("text", "size")).reset_index()
ks = yc.merge(yt[["video_id", "keyword"]], on="video_id", how="inner")
dist = (ks.groupby(["keyword", "label_dataset"]).size().unstack(fill_value=0))
dist_pct = dist.div(dist.sum(axis=1), axis=0)
vdist = (ks.groupby(["keyword", "vader_label"]).size().unstack(fill_value=0))
vdist_pct = vdist.div(vdist.sum(axis=1), axis=0)
out = pd.DataFrame({
    "n_komentar": dist.sum(axis=1),
    "pos_dataset": dist_pct.get("positive", 0), "neu_dataset": dist_pct.get("neutral", 0),
    "neg_dataset": dist_pct.get("negative", 0),
    "neg_vader": vdist_pct.get("negative", 0),
}).reset_index()
out["rank_neg_dataset"] = out.neg_dataset.rank(ascending=False, method="first").astype(int)
out = out.sort_values(["neg_dataset", "keyword"], ascending=[False, True], kind="mergesort")
out.to_csv("outputs/yt_keyword_sent.csv", index=False)
top_neg = out.iloc[0]
add("Q7", "keyword dengan porsi negatif tertinggi (label dataset)", top_neg.keyword,
    p="", n=top_neg.n_komentar, catatan=f"porsi negatif {top_neg.neg_dataset:.3f}; kode 0 diasumsikan negative")
add("Q11", "peringkat negatif tertinggi (sama dengan Q7)", top_neg.keyword, n=top_neg.n_komentar,
    catatan="Tambahan; lihat yt_keyword_sent.csv")

vid_sent = yc.groupby("video_id").agg(vader_mean=("vader_compound", "mean"),
                                      label_mean=("label_dataset_code", "mean"),
                                      n_c=("text", "size")).reset_index()
vy = yt.merge(vid_sent, on="video_id", how="inner")
rho, p_rho = stats.spearmanr(vy.vader_mean, vy.er)
add("Q8", "Spearman VADER mean x ER video", fmt(rho), p=fmt(p_rho), n=len(vy),
    catatan="H4; video dengan komentar")
rho2, p_rho2 = stats.spearmanr(vy.label_mean, vy.er)
add("Q8", "Spearman label dataset mean x ER video", fmt(rho2), p=fmt(p_rho2), n=len(vy),
    catatan="pembanding; kode label diasumsikan")

# ---------- YouTube: Q9 VADER vs label dataset ----------
conf = pd.crosstab(yc.label_dataset, yc.vader_label, dropna=False)
conf.to_csv("outputs/yt_vader_confusion.csv")
acc = float((yc.label_dataset == yc.vader_label).mean())
lo, hi = boot_ci((yc.label_dataset == yc.vader_label).astype(float).values, stat=np.mean)
add("Q9", "akurasi VADER vs label dataset (3 kelas)", fmt(acc), fmt(lo), fmt(hi), n=len(yc),
    catatan="label dataset dianggap referensi; belum ada label manual 200 komentar")

# ---------- Q10 impact (label estimated) ----------
best_type = tt.iloc[0]
mean_er = fb.er.mean()
reach_avg = fb.reach.mean()
posts_per_month = 12
impact = (best_type.median_er - mean_er) * posts_per_month * reach_avg
add("Q10", "estimasi tambahan interaksi per bulan (estimated)", fmt(impact), n=posts_per_month,
    catatan=f"(ER {best_type.type} median - ER rata-rata post) x 12 x reach rata-rata {reach_avg:.0f}; label estimated")

# ---------- Q12 audit ----------
add("Q12", "post FB dengan kolom kosong", int(fb[["paid", "like", "share"]].isna().any(axis=1).sum()),
    n=len(fb), catatan="dipertahankan; lihat cleaning_log.csv")
add("Q12", "video YT viral (> Q3+3IQR)", int(yt.viral.sum()), n=len(yt),
    catatan="ditinjau terpisah (Q13)")
add("Q12", "post FB viral", int(fb.viral.sum()), n=len(fb))

# ---------- Q13 sensitivity ----------
sens = []
def sens_add(name, value, lo=np.nan, hi=np.nan, p=np.nan, n=np.nan):
    sens.append([name, value, lo, hi, p, n])

# viral dikeluarkan (YT): ranking keyword teratas & Spearman H4
yt_nv = yt[~yt.viral]
kw_nv = yt_nv.groupby("keyword").er.median().sort_values(ascending=False, kind="mergesort")
sens_add("top keyword tanpa viral", kw_nv.index[0], n=len(yt_nv))
sens_add("top keyword dengan viral", kw.iloc[0].keyword, n=len(yt))
same_top = kw_nv.index[0] == kw.iloc[0].keyword
vy_nv = vy[~vy.video_id.isin(yt[yt.viral].video_id)]
rho_nv, p_nv = stats.spearmanr(vy_nv.vader_mean, vy_nv.er)
sens_add("Spearman H4 tanpa viral", fmt(rho_nv), p=fmt(p_nv), n=len(vy_nv))
sens_add("Spearman H4 dengan viral", fmt(rho), p=fmt(p_rho), n=len(vy))
# Q1 tanpa viral (FB tidak ada viral, sehingga sama)
H_nv, p_nv_kw = stats.kruskal(*[g.er.values for _, g in yt_nv.groupby("keyword")])
sens_add("Kruskal keyword tanpa viral", fmt(H_nv), p=fmt(p_nv_kw), n=len(yt_nv))

# asumsi jam kerja
for lo_h, hi_h in [(8, 17), (9, 17), (8, 18)]:
    jk_mask = fb.hour.between(lo_h, hi_h)
    u, p = stats.mannwhitneyu(fb[~jk_mask].er, fb[jk_mask].er, alternative="greater")
    sens_add(f"H2 jam kerja {lo_h:02d}-{hi_h:02d}: selisih median",
             fmt(fb[~jk_mask].er.median() - fb[jk_mask].er.median()), p=fmt(p),
             n=f"{(~jk_mask).sum()}/{jk_mask.sum()}")

# mean vs median pada Q10
impact_mean = (tt.iloc[0].mean_er - mean_er) * posts_per_month * reach_avg
sens_add("Q10 impact pakai ER mean tipe terbaik", fmt(impact_mean), n=posts_per_month)
sens_add("Q10 impact dengan reach median", fmt((best_type.median_er - mean_er) * posts_per_month * fb.reach.median()),
         n=posts_per_month)

pd.DataFrame(sens, columns=["uji", "nilai", "ci_low", "ci_high", "p", "n"]).to_csv(
    "outputs/sensitivity.csv", index=False)
add("Q13", "top keyword sama tanpa viral", str(same_top), n=len(yt_nv),
    catatan=f"tanpa viral: {kw_nv.index[0]}; dengan viral: {kw.iloc[0].keyword}")
add("Q13", "Spearman H4 tanpa viral", fmt(rho_nv), p=fmt(p_nv), n=len(vy_nv))

pd.DataFrame(ANS, columns=["pertanyaan", "metrik", "nilai", "ci_low", "ci_high", "p", "n", "catatan"]).to_csv(
    "outputs/answers.csv", index=False)
print("answers rows:", len(ANS))
