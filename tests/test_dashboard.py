"""Uji dashboard dengan Streamlit AppTest: setiap halaman dirender tanpa error, dan kolom yang dipakai ada di CSV."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "dashboard" / "app.py")
PAGES = ["Ringkasan", "Format & Waktu", "Topik & Sentimen", "Kalkulator Interaksi"]


def run_page(name):
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    at.sidebar.radio[0].set_value(name).run()
    assert not at.exception, at.exception
    return at


def test_each_page_renders_without_exception():
    for p in PAGES:
        at = run_page(p)
        assert len(at.main.children) > 0


def test_calculator_responds_to_slider():
    at = run_page("Kalkulator Interaksi")
    at.slider[0].set_value(20).run()
    assert not at.exception
    assert any("Tambahan interaksi" in m.label for m in at.metric)


def test_columns_used_by_dashboard_exist():
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from pathlib import Path as P
    import pandas as pd
    checks = {
        "dash_fb_type.csv": ["type", "median_er", "ci_low", "ci_high"],
        "dash_yt_keyword.csv": ["keyword", "median_er", "ci_low", "ci_high", "neg_dataset"],
        "dash_fb_summary.csv": ["mean_er_semua", "reach_rata2", "n_post", "median_er_semua"],
        "dash_fb_weekday_hour.csv": ["weekday", "hour", "median_er"],
    }
    for f, cols in checks.items():
        df = pd.read_csv(ROOT / "outputs" / f)
        for c in cols:
            assert c in df.columns, (f, c)
