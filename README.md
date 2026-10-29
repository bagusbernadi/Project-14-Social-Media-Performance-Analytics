[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 14: Social Media Performance Analytics

**Status: Analisis dan dashboard selesai (WIP, branch `project-14-build`). Belum di-deploy. Notebook dan label manual belum.**

**Status awal: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

**Tujuan:** membangun analisis dan dashboard kinerja media sosial yang menunjukkan jenis konten, hari, dan jam posting dengan engagement rate tertinggi, serta topik dan sentimen komentar yang paling terkait dengan engagement.

| | |
|---|---|
| Kategori | Media / sosial |
| Tingkat | Mudah |
| Data | Dataset publik UCI Facebook Metrics + Kaggle YouTube Statistics |
| Tools | DuckDB + SQL, Python (pandas, SciPy), VADER (NLTK), Streamlit + Plotly |

## 1. Problem

**Pertanyaan utama:** Jenis konten, hari, dan jam posting apa yang menghasilkan engagement rate tertinggi, dan topik serta sentimen komentar apa yang paling terkait dengan engagement?

Rancangan memecahnya menjadi 14 pertanyaan (9 Utama, 4 Pendukung, 1 Tambahan) dalam tema format konten, waktu posting, topik dan sentimen, dampak, dan validitas data. Daftar lengkap ada di bagian 2 halaman rancangan.

## 2. Data

- Sumber data (Facebook): [here](https://archive.ics.uci.edu/dataset/368/facebook+metrics) (Versi: 1, Tanggal akses: 23 Oktober 2026)
- Sumber data (YouTube): [here](https://www.kaggle.com/datasets/advaypatil/youtube-statistics) (Versi: 1, Tanggal akses: 23 Oktober 2026)
- Ukuran (perkiraan, **belum diverifikasi**): ±500 post Facebook (2014), ±1.900 video dan ±18 ribu komentar YouTube.
- Kedua dataset dianalisis terpisah.
- Rencana tabel: `fb_posts`, `yt_videos`, `yt_comments`, `group_summary`.
- Lisensi: Facebook Metrics CC BY 4.0 (halaman UCI, dicek 28 Oktober 2026); YouTube Statistics CC0: Public Domain (label Kaggle, uploader Advay Patil, dicek 28 Oktober 2026). Sitasi Facebook Metrics: Moro, S., Rita, P., & Vala, B. (2016). Predicting social media performance metrics and evaluation of the impact on brand building: A data mining approach. Journal of Business Research. https://doi.org/10.1016/j.jbusres.2016.02.010
- Data mentah tidak di-commit ke repository.

## 3. Analysis

Angka dihitung dari `src/03_analysis.py` (pandas) dan dicek silang dengan DuckDB (`src/04_sql_kpi.py`, 45 nilai sama). Ringkasan di `outputs/answers.csv`. Asumsi di `docs/definitions.md`.

**Hasil (Facebook, 500 post, 2014):**

- Q1: median ER Photo 2,45% (CI 2,21–2,65%), Status 1,53%, Link 0,68%, Video 0,55% (n=7, CI lebar).
- Q2: Kruskal-Wallis p < 0,001. Photo lebih tinggi dari Link dan Status (Holm p < 0,001 dan 0,0002). Photo vs Video p = 0,010 (Holm). Link vs Video tidak berbeda.
- Hipotesis 1 (Status dan Video lebih tinggi dari Photo dan Link): **tidak didukung**. Status dan Video justru lebih rendah dari Photo.
- Q3: post berbayar punya reach lebih besar (p < 0,001), tetapi median ER tidak berbeda (p = 0,16). Sesuai hipotesis 3.
- Q4: Kruskal-Wallis antar kelompok jam p = 0,040 (kelompok jam sesuai rancangan: Pagi, Siang, Sore, Malam 20–04). Hasilnya marginal dan tidak seimbang: Sore 16–19 hanya 8 post. Malam 20–04 punya median tertinggi (2,46%). Sel hari × jam dengan n ≥ 5 hanya 9.
- H2 (di luar jam kerja lebih tinggi): selisih median +0,27 poin, p = 0,098 (satu sisi). Tidak signifikan. Arah sama pada tiga asumsi jam kerja.
- Q10: estimasi tambahan interaksi hanya sekitar 76 interaksi per bulan (estimated). Selisih ER format terbaik dengan rata-rata sangat kecil (0,04 poin).
- Q12: 0 post viral. 5 post dengan kolom kosong.

**Hasil (YouTube, 1.867 video, 41 keyword, 18.408 komentar):**

- Q6: median ER tertinggi keyword `crypto` 8,5% (CI 7,8–9,7%). Kruskal-Wallis p < 0,001.
- Q7 dan Q11: porsi komentar negatif tertinggi di keyword `cnn` (label dataset).
- Q8 dan H4 (komentar lebih positif, ER lebih tinggi): Spearman ρ = 0,045, p = 0,051 dengan VADER. Label dataset: ρ = -0,007, p = 0,76. **Tidak didukung**.
- Q9: akurasi VADER terhadap label dataset 71,6% (3 kelas, 18.408 komentar). Pembanding berbasis LLM pada 200 sampel: label dataset 74,5%, VADER 56,5%. Label LLM dibuat asisten AI dan belum diverifikasi manusia. Label manual belum ada.
- Q13: keyword teratas tetap `crypto` tanpa 23 video viral. Spearman H4 tanpa viral ρ = 0,052, p = 0,026. Pada pengujian ini sensitif terhadap viral, sehingga kesimpulan H4 belum bisa dipegang.

**Hipotesis 5** (VADER lemah untuk sarkasme dan bahasa campur): belum diuji. Perlu label manual 200 komentar.

Hipotesis yang akan diuji (belum terbukti):
1. Status dan Video lebih tinggi engagement rate-nya daripada Photo dan Link.
2. Post di luar jam kerja lebih tinggi engagement rate-nya.
3. Post berbayar reach-nya besar tapi engagement rate tidak lebih tinggi.
4. Komentar lebih positif terkait engagement lebih tinggi.
5. VADER cukup akurat untuk bahasa Inggris, lemah untuk sarkasme.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: jadwal dan format posting.

## 5. Impact

Q10 (estimated): ±76 tambahan interaksi per bulan. Asumsi di `docs/definitions.md`.

Belum dikerjakan. Rumus yang akan dipakai (semua hasil diberi label `estimated`):

```
Tambahan interaksi = (ER format terbaik − ER rata-rata) × posting per bulan × reach rata-rata (label estimated)
```

## Batasan yang sudah diketahui

- Korelasi bukan sebab.
- Data Facebook dari 2014 dan satu brand.
- Sentimen otomatis tidak sempurna.

## Status pengerjaan (WIP)

| Item | Status |
|---|---|
| Ingest dan verifikasi SHA-256 (`src/01_ingest.py`) | selesai |
| Cleaning dan skor VADER (`src/02_clean.py`) | selesai, log di `outputs/cleaning_log.csv` |
| Analisis Q1–Q13 (`src/03_analysis.py`) | selesai |
| Dashboard export (`src/08_dashboard_export.py`) | selesai |
| Uji dari nol dua kali (`run_all.sh`) | selesai, checksum identik |
| Cek silang SQL vs pandas Q14 (`src/04_sql_kpi.py`) | selesai, 45 nilai sama |
| Label manual 200 komentar (Q9, H5) | belum: sampel sudah dikirim; pembanding LLM ada di `labels/llm_label_200.csv` |
| Dashboard Streamlit 4 halaman (`dashboard/app.py`) + AppTest (`tests/test_dashboard.py`, 3 lulus) | selesai; belum di-deploy |
| Notebook analisis, one-sheet | belum |
| `report_lib.py`, `report.css` dari Project-4 | belum: repo Project-4 belum di-attach |
| `check_std` | belum dijalankan |

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
```

Folder `docs/`, `data/`, `scripts/`, `sql/`, `notebooks/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai.
