"""AI Report page: a deterministic, Pandas-computed executive summary.

No Ollama calls happen here - every figure is derived from the existing
AI analysis output via src.analytics.generate_ai_report.
"""

from __future__ import annotations

import streamlit as st

from src import analytics
from app.components import empty_state, kpi_row, page_header, section_heading
from src.utils import format_percent


def render(df) -> None:
    page_header("AI Report", "An executive-style summary computed deterministically from the AI analysis")
    st.caption("Generated locally with Pandas from outputs/llm_review_analysis.csv - no additional AI calls were made.")

    report = analytics.generate_ai_report(df)
    kpis = report["kpis"]

    section_heading("Executive Summary")
    kpi_row([
        ("Total Reviews", str(kpis["total_reviews"]), ""),
        ("AI Analyzed", str(kpis["analyzed_reviews"]), f"{kpis['skipped_reviews']} skipped"),
        ("Average Rating", f"{kpis['avg_rating']:.1f} / 5" if kpis["avg_rating"] is not None else "N/A", ""),
        ("Average Satisfaction", format_percent(kpis["avg_satisfaction"]), ""),
        ("Positive Sentiment %", f"{kpis['positive_pct']:.0f}%" if kpis["positive_pct"] is not None else "N/A", ""),
    ])

    col1, col2 = st.columns(2)

    with col1:
        section_heading("Client Strengths")
        strengths = report["strengths"]
        if strengths.empty:
            empty_state("No strengths identified.")
        else:
            top = strengths.head(10).rename(columns={
                "strength": "Strength", "frequency": "Frequency", "percentage_of_reviews": "% of Reviews",
            })
            top["% of Reviews"] = top["% of Reviews"].map(lambda v: f"{v:.1f}%")
            st.dataframe(top, width="stretch", hide_index=True)

    with col2:
        section_heading("Improvement Opportunities")
        improvements = report["improvements"]
        if improvements.empty:
            empty_state("No recurring improvement areas were identified by the AI.")
        else:
            top = improvements.head(10).rename(columns={
                "improvement_area": "Improvement Area", "frequency": "Frequency",
                "percentage_of_reviews": "% of Reviews",
            })
            top["% of Reviews"] = top["% of Reviews"].map(lambda v: f"{v:.1f}%")
            st.dataframe(top, width="stretch", hide_index=True)

    section_heading("Gig Insights")
    gigs = report["gigs"].copy()
    if gigs.empty:
        empty_state("No gig data available.")
    else:
        gigs["avg_rating"] = gigs["avg_rating"].map(lambda v: f"{v:.1f}" if v is not None else "N/A")
        gigs["avg_satisfaction"] = gigs["avg_satisfaction"].map(lambda v: format_percent(v) if v is not None else "N/A")
        gigs["positive_pct"] = gigs["positive_pct"].map(lambda v: f"{v:.0f}%" if v is not None else "N/A")
        gigs["avg_confidence"] = gigs["avg_confidence"].map(lambda v: format_percent(v) if v is not None else "N/A")
        gigs = gigs.rename(columns={
            "gig": "Gig", "review_count": "Review Count", "avg_rating": "Average Rating",
            "avg_satisfaction": "AI Satisfaction", "positive_pct": "Positive Sentiment %",
            "avg_confidence": "AI Confidence",
        })
        st.dataframe(gigs, width="stretch", hide_index=True)

    section_heading("Common Topics")
    topics = report["topics"]
    if topics.empty:
        empty_state("No topics identified.")
    else:
        top = topics.head(12).rename(columns={
            "topic": "Topic", "frequency": "Frequency", "percentage_of_reviews": "% of Reviews",
        })
        top["% of Reviews"] = top["% of Reviews"].map(lambda v: f"{v:.1f}%")
        st.dataframe(top, width="stretch", hide_index=True)

    section_heading("Key Observations")
    for observation in report["observations"]:
        st.markdown(f"- {observation}")
