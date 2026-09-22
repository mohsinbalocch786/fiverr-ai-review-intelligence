"""Fiverr AI Review Intelligence - Streamlit dashboard entry point.

This file is intentionally focused on layout/navigation only. All data
loading lives in src/data_loader.py and all metrics/aggregation logic
lives in src/analytics.py. No Ollama calls are made from this app - it
only reads and visualizes the existing outputs/llm_review_analysis.csv.

Run with:
    streamlit run app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import merge_data, using_sample_data
from app.styles import CUSTOM_CSS
from app.components import sidebar_data_box
from app.views import ai_report, explorer, gig_performance, improvements, overview, sentiment, strengths

st.set_page_config(
    page_title="Fiverr AI Review Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PAGES = {
    "Overview": overview,
    "Sentiment Analysis": sentiment,
    "Gig Performance": gig_performance,
    "Strengths": strengths,
    "Improvement Areas": improvements,
    "Review Explorer": explorer,
    "AI Report": ai_report,
}


def main() -> None:
    df = merge_data()

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">Fiverr AI Review Intelligence</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-tagline">AI-powered analysis of client feedback, '
            'satisfaction, strengths and improvement opportunities</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
        page_name = st.radio(
            "Navigation", list(PAGES.keys()), label_visibility="collapsed",
        )

        total = len(df)
        analyzed = int((df["status"] == "success").sum()) if "status" in df.columns else 0
        skipped = total - analyzed
        sidebar_data_box(total, analyzed, skipped)

    if df.empty:
        st.error(
            "No AI analysis data found - not even the bundled sample dataset. "
            "Expected outputs/llm_review_analysis.csv (or outputs/sample_llm_review_analysis.csv) "
            "and data/raw/fiverr_reviews.csv (or data/raw/sample_fiverr_reviews.csv)."
        )
        return

    if using_sample_data():
        st.info(
            "Showing the bundled **sample dataset** - your real review data isn't present. "
            "Add your Fiverr export at `data/raw/fiverr_reviews.csv` and run the analysis "
            "notebook to see your own results here. See the README for setup steps.",
            icon="ℹ️",
        )

    PAGES[page_name].render(df)


if __name__ == "__main__":
    main()
