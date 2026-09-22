"""Small reusable Streamlit UI building blocks shared across dashboard pages."""

from __future__ import annotations

import streamlit as st

from app.styles import SENTIMENT_CHIP_STYLES


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_heading(text: str) -> None:
    st.markdown(f'<div class="section-heading">{text}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, caption: str = "") -> None:
    caption_html = f'<div class="kpi-caption">{caption}</div>' if caption else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(cards: list[tuple[str, str, str]]) -> None:
    """Render a row of KPI cards. Each item is (label, value, caption)."""
    cols = st.columns(len(cards))
    for col, (label, value, caption) in zip(cols, cards):
        with col:
            kpi_card(label, value, caption)


def sentiment_pill(sentiment: str) -> str:
    label = sentiment if isinstance(sentiment, str) and sentiment.strip() else "Not Analyzed"
    style = SENTIMENT_CHIP_STYLES.get(label, SENTIMENT_CHIP_STYLES["Not Analyzed"])
    return (
        f'<span class="sentiment-pill" '
        f'style="background-color:{style["bg"]};color:{style["text"]};border-color:{style["border"]}">'
        f"{label}</span>"
    )

def badge_list(items: list[str], css_class: str) -> str:
    if not items:
        return ""
    return "".join(f'<span class="badge {css_class}">{item}</span>' for item in items)


def empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def sidebar_data_box(total: int, analyzed: int, skipped: int) -> None:
    st.markdown('<div class="sidebar-section-label">Data</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sidebar-data-box">
            <div class="sidebar-data-row"><span>Total Reviews</span><span class="value">{total}</span></div>
            <div class="sidebar-data-row"><span>AI Analyzed</span><span class="value">{analyzed}</span></div>
            <div class="sidebar-data-row"><span>Skipped</span><span class="value">{skipped}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
