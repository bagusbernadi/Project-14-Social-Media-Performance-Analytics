[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 14: Social Media Performance Analytics

**Status: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

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

Belum dikerjakan. Rencana langkah (12 langkah, tahap A sampai D) ada di bagian 6 halaman rancangan. Semua angka nanti dihitung dari data dengan SQL dan dicek silang.

Hipotesis yang akan diuji (belum terbukti):
1. Status dan Video lebih tinggi engagement rate-nya daripada Photo dan Link.
2. Post di luar jam kerja lebih tinggi engagement rate-nya.
3. Post berbayar reach-nya besar tapi engagement rate tidak lebih tinggi.
4. Komentar lebih positif terkait engagement lebih tinggi.
5. VADER cukup akurat untuk bahasa Inggris, lemah untuk sarkasme.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: jadwal dan format posting.

## 5. Impact

Belum dikerjakan. Rumus yang akan dipakai (semua hasil diberi label `estimated`):

```
Tambahan interaksi = (ER format terbaik − ER rata-rata) × posting per bulan × reach rata-rata (label estimated)
```

## Batasan yang sudah diketahui

- Korelasi bukan sebab.
- Data Facebook dari 2014 dan satu brand.
- Sentimen otomatis tidak sempurna.

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
```

Folder `docs/`, `data/`, `scripts/`, `sql/`, `notebooks/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai.
