# Definisi dan asumsi Project 14

## Definisi (sesuai rancangan)

- ER Facebook = total interaksi ÷ reach (`total / reach`, per post).
- ER YouTube = (likes + comments) ÷ views (per video).
- Viral = ER di atas Q3 + 3 × IQR, dihitung per platform. Post viral ditinjau terpisah dan tidak dibuang dari data.
- Median dan CI 95% dengan bootstrap percentile (5.000 resample, seed 20261028).
- Uji: Kruskal-Wallis, Mann-Whitney (dua sisi, atau satu sisi jika arah hipotesis ditetapkan), Spearman. Koreksi Holm untuk pasangan tipe.
- Kelompok dengan n < 5 tidak dipakai untuk kesimpulan.

## Asumsi (label ASUMSI, diuji di outputs/sensitivity.csv)

| No | Asumsi | Alasan | Uji sensitivitas |
|---|---|---|---|
| A1 | Kode `Sentiment` YouTube: 2 = positive, 1 = neutral, 0 = negative | Tidak tertulis di sumber. Pola tabel kontingensi VADER vs label (positive↔positive 10.346) mendukung, tetapi bukan bukti | Belum diuji ulang dengan kode lain; hasil Q8/Q9 bergantung pada asumsi ini |
| A2 | Jam kerja = 08 sampai 17 | Rancangan tidak mendefinisikan jam kerja | 09-17, 08-18: arah sama, p tidak signifikan (outputs/sensitivity.csv) |
| A3 | Kode hari (`weekday` 1 sampai 7) tidak dipakai untuk label nama hari | Sumber tidak menjelaskan kode | Q4 ditulis sebagai kode hari, bukan nama hari |
| A4 | Batas VADER compound: ≥ 0,05 positive, ≤ -0,05 negative | Konvensi VADER | Belum diuji |
| A5 | Reach rata-rata untuk Q10 = rata-rata reach 500 post | Rancangan: reach rata-rata dari data | Median reach dipakai sebagai pembanding (outputs/sensitivity.csv) |
| A6 | Q10 memakai ER median tipe terbaik dikurangi ER rata-rata | Rancangan tidak merinci | Versi mean tipe terbaik ditambahkan sebagai pembanding |
| A7 | Video dengan `Video ID` ganda: baris pertama dipertahankan | 12 ID ganda, isi berbeda | Belum diuji (kecil) |
| A8 | Label VADER dipakai sebagai pengganti LLM untuk sentimen | Sandbox tidak punya akses LLM API. Rancangan mengizinkan leksikon | Akurasi dilaporkan terhadap label dataset, bukan label manual |
| A9 | Paket `vaderSentiment` (lexicon VADER yang sama) dipakai, bukan NLTK | Unduhan data NLTK tidak tersedia di sandbox | Skor identik secara lexicon; belum diverifikasi terhadap NLTK |

## Penyimpangan dari rancangan

- Q9 belum memakai 200 label manual. Yang dibandingkan: label dataset dan label manual belum ada. Akurasi di answers.csv adalah VADER vs label dataset (18.408 komentar).
- Data YouTube dari Kaggle, bukan dari YouTube Data API v3 yang ditulis di rancangan awal. Keputusan Anda: sesuaikan dengan dataset yang ada.
- Facebook: 500 post dari 2014 sebuah brand kosmetik (UCI). Hasil tidak bisa digeneralisasi.
