"""Dashboard Social Media Performance Analytics (Project 14). 4 halaman.

Sumber: outputs/ (dihasilkan oleh src/). Angka ER dan uji dihitung di skrip, bukan di dashboard.
Jalankan: streamlit run dashboard/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PAGES = ["Ringkasan", "Format & Waktu", "Topik & Sentimen", "Kalkulator Interaksi"]

REQ = {
    "dash_answers.csv": ["pertanyaan", "metrik", "nilai", "ci_low", "ci_high", "p", "n", "catatan"],
    "dash_fb_type.csv": ["type", "n", "median_er", "ci_low", "ci_high", "mean_er"],
    "dash_fb_weekday_hour.csv": ["weekday", "hour", "n", "median_er"],
    "dash_fb_hour_bucket.csv": ["hour_bucket", "n", "median_er"],
    "fb_pairwise.csv": ["tipe_a", "tipe_b", "n_a", "n_b", "p_raw", "p_holm"],
    "dash_fb_summary.csv": ["n_post", "median_er_semua", "mean_er_semua", "reach_rata2", "n_viral_fb", "n_paid"],
    "dash_yt_keyword.csv": ["keyword", "n", "median_er", "ci_low", "ci_high", "neg_dataset", "pos_dataset", "neg_vader"],
    "llm_ref_eval.csv": ["pembanding", "n", "akurasi_vs_llm_ref"],
    "sql_vs_pandas.csv": ["grup", "kunci", "sama"],
}


@st.cache_data
def load(name):
    df = pd.read_csv(OUT / name)
    missing = [c for c in REQ[name] if c not in df.columns]
    if missing:
        raise ValueError(f"{name} tidak punya kolom: {missing}")
    return df


def page_summary():
    st.header("Ringkasan")
    fb = load("dash_fb_summary.csv").iloc[0]
    fbt = load("dash_fb_type.csv")
    yk = load("dash_yt_keyword.csv")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Post Facebook", f"{int(fb.n_post)}")
    c2.metric("Median ER Facebook", f"{fb.median_er_semua:.2%}")
    c3.metric("Keyword YouTube", f"{len(yk)}")
    c4.metric("Median ER tertinggi keyword", f"{yk.median_er.max():.2%}")
    st.caption("ER Facebook = total interaksi ÷ reach. ER YouTube = (likes + comments) ÷ views. Data publik, 2014 (FB) dan 2007–2022 (YouTube).")
    st.subheader("Jawaban per pertanyaan")
    ans = load("dash_answers.csv")
    st.dataframe(ans, hide_index=True, use_container_width=True)
    st.subheader("Cek silang SQL vs pandas")
    chk = load("sql_vs_pandas.csv")
    st.write(f"{int(chk.sama.sum())} dari {len(chk)} nilai sama.")


def page_format():
    st.header("Format & Waktu (Facebook)")
    t = load("dash_fb_type.csv").sort_values("median_er", ascending=False)
    fig = px.bar(t, x="type", y="median_er", error_y=t.ci_high - t.median_er,
                 error_y_minus=t.median_er - t.ci_low, labels={"median_er": "median ER", "type": "tipe"})
    fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Bar = median ER per tipe, garis = CI 95% bootstrap. Video n=7, CI lebar.")
    st.dataframe(t, hide_index=True, use_container_width=True)

    st.subheader("Perbandingan antar tipe (Mann-Whitney, Holm)")
    st.dataframe(load("fb_pairwise.csv"), hide_index=True, use_container_width=True)

    st.subheader("Kelompok jam")
    hb = load("dash_fb_hour_bucket.csv")
    fig2 = px.bar(hb, x="hour_bucket", y="median_er", labels={"median_er": "median ER", "hour_bucket": "kelompok jam"})
    fig2.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Sore 16–19 hanya 8 post. Perbedaan antar kelompok jam marginal (lihat Ringkasan).")

    st.subheader("Heatmap hari × jam (kode hari, sel n ≥ 5)")
    wh = load("dash_fb_weekday_hour.csv")
    pivot = wh.pivot(index="weekday", columns="hour", values="median_er")
    fig3 = px.imshow(pivot, labels=dict(x="jam", y="kode hari", color="median ER"), aspect="auto")
    fig3.update_coloraxes(colorbar_tickformat=".1%")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Kode hari dari sumber (1–7) belum diberi nama hari. Sel kosong = n < 5.")


def page_topic():
    st.header("Topik & Sentimen (YouTube)")
    yk = load("dash_yt_keyword.csv").sort_values("median_er", ascending=False)
    top = yk.head(15)
    fig = px.bar(top, x="keyword", y="median_er", error_y=top.ci_high - top.median_er,
                 error_y_minus=top.median_er - top.ci_low, labels={"median_er": "median ER", "keyword": "keyword"})
    fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("15 keyword teratas. Bar = median ER, garis = CI 95%.")

    st.subheader("Porsi komentar negatif per keyword (label dataset)")
    neg = yk.sort_values("neg_dataset", ascending=False)
    fig2 = px.bar(neg, x="keyword", y="neg_dataset", labels={"neg_dataset": "porsi negatif", "keyword": "keyword"})
    fig2.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Akurasi VADER dan label dataset terhadap pembanding LLM (200 sampel)")
    st.dataframe(load("llm_ref_eval.csv"), hide_index=True, use_container_width=True)
    st.caption("Pembanding berbasis LLM, BUKAN label manual. Label manual belum ada, sehingga Q9 dan H5 belum final.")


def page_calc():
    st.header("Kalkulator Interaksi (estimated)")
    st.caption("Estimasi tambahan interaksi per bulan = (ER tipe − ER rata-rata) × posting per bulan × reach rata-rata. Semua hasil label estimated.")
    fbt = load("dash_fb_type.csv")
    s = load("dash_fb_summary.csv").iloc[0]
    tipe = st.selectbox("Tipe konten", fbt.sort_values("median_er", ascending=False).type.tolist())
    posts = st.slider("Posting per bulan", 1, 30, 12)
    er_tipe = float(fbt.loc[fbt.type == tipe, "median_er"].iloc[0])
    er_avg = float(s.mean_er_semua)
    reach = float(s.reach_rata2)
    est = (er_tipe - er_avg) * posts * reach
    c1, c2, c3 = st.columns(3)
    c1.metric("ER median tipe (estimated)", f"{er_tipe:.2%}")
    c2.metric("ER rata-rata post", f"{er_avg:.2%}")
    c3.metric("Tambahan interaksi/bulan (estimated)", f"{est:,.0f}")
    st.caption(f"Reach rata-rata {reach:,.0f} per post (dari data). Negatif berarti di bawah rata-rata.")


def main():
    st.set_page_config(page_title="Social Media Performance", layout="wide")
    page = st.sidebar.radio("Halaman", PAGES)
    if page == "Ringkasan":
        page_summary()
    elif page == "Format & Waktu":
        page_format()
    elif page == "Topik & Sentimen":
        page_topic()
    else:
        page_calc()


main()
