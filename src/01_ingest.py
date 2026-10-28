"""Ekstrak dua dataset dari data/raw/ dan verifikasi SHA-256 terhadap DataCenter.

Input : data/raw/facebook+metrics.zip, data/raw/yt_archive.zip (salinan dari DataCenter)
Output: data/raw/fb/, data/raw/yt/, outputs/ingest_manifest.csv
"""
import csv
import hashlib
import os
import sys
import zipfile

EXPECTED = {
    "data/raw/facebook+metrics.zip": "48e4739b4acbbcca8f03cbcfe145d82c2e665cdd5bb9e20618690d454ce93fd3",
    "data/raw/yt_archive.zip": "70a1dfe71915bcbaf18e05887f0bdda28fab284a9b146ee8417f9a283a14a586",
}
EXTRACT = {"data/raw/facebook+metrics.zip": "data/raw/fb", "data/raw/yt_archive.zip": "data/raw/yt"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs("outputs", exist_ok=True)
    rows = []
    for zpath, want in EXPECTED.items():
        if not os.path.exists(zpath):
            sys.exit(f"Tidak ada {zpath}. Salin dari DataCenter dulu.")
        got = sha256(zpath)
        if got != want:
            sys.exit(f"SHA-256 tidak cocok untuk {zpath}: {got}")
        out = EXTRACT[zpath]
        os.makedirs(out, exist_ok=True)
        with zipfile.ZipFile(zpath) as z:
            names = sorted(z.namelist())
            z.extractall(out)
        for n in names:
            p = os.path.join(out, n)
            if os.path.isfile(p):
                rows.append([zpath, n, os.path.getsize(p), sha256(p)])
    with open("outputs/ingest_manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["zip", "berkas", "bytes", "sha256"])
        w.writerows(sorted(rows, key=lambda r: (r[0], r[1])))
    print("ingest ok:", len(rows), "berkas")


if __name__ == "__main__":
    main()
