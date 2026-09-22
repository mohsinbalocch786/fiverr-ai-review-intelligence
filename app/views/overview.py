"""Overview page: top-line KPIs plus sentiment/gig distribution at a glance."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import analytics
from app.components import kpi_row, page_header, section_heading, empty_state
from app.styles import BRAND_PRIMARY, PLOTLY_TEMPLATE, SENTIMENT_COLORS
from src.utils import format_percent


def render(df) -> None:
    page_header(
        "Fiverr AI Review Intelligence",
        "AI-powered analysis of client feedback, satisfaction, strengths and improvement opportunities",
    )

    kpis = analytics.overall_kpis(df)

    kpi_row([
        ("Total Reviews", str(kpis["total_reviews"]), "Reviews in the analyzed dataset"),
        ("AI Analyzed", str(kpis["analyzed_reviews"]), f"{kpis['skipped_reviews']} skipped"),
        (
            "Average Rating",
            f"{kpis['avg_rating']:.1f} / 5" if kpis["avg_rating"] is not None else "N/A",
            "Client star rating",
        ),
        ("AI Satisfaction", format_percent(kpis["avg_satisfaction"]), "Model-estimated satisfaction"),
        ("Positive Sentiment", f"{kpis['positive_pct']:.0f}%" if kpis["positive_pct"] is not None else "N/A", "Share of analyzed reviews"),
    ])

    col_left, col_right = st.columns([1, 1])

    with col_left:
        section_heading("Sentiment Distribution")
        sentiment_df = analytics.sentiment_summary(df)
        if sentiment_df["count"].sum() == 0:
            empty_state("No analyzed reviews available yet.")
        else:
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=sentiment_df["sentiment"],
                        values=sentiment_df["count"],
                        hole=0.55,
                        marker=dict(colors=[SENTIMENT_COLORS[s] for s in sentiment_df["sentiment"]]),
                        sort=False,
                        textinfo="label+percent",
                        hovertemplate="%{label}: %{value} reviews (%{percent})<extra></extra>",
                    )
                ]
            )
            fig.update_layout(
                template=PLOTLY_TEMPLATE,
                showlegend=True,
                margin=dict(t=10, b=10, l=10, r=10),
                height=340,
            )
            st.plotly_chart(fig, width="stretch")

    with col_right:
        section_heading("Gig Distribution")
        gig_df = analytics.gig_performance(df)[["gig", "review_count"]].sort_values("review_count")
        if gig_df.empty:
            empty_state("No gig data available.")
        else:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=gig_df["review_count"],
                        y=gig_df["gig"],
                        orientation="h",
                        marker_color=BRAND_PRIMARY,
                        text=gig_df["review_count"],
                        textposition="outside",
                        hovertemplate="%{y}: %{x} reviews<extra></extra>",
                    )
                ]
            )
            fig.update_layout(
                template=PLOTLY_TEMPLATE,
                margin=dict(t=10, b=10, l=10, r=30),
                height=340,
                xaxis_title="Reviews",
                yaxis_title=None,
            )
            st.plotly_chart(fig, width="stretch")

    section_heading("AI Satisfaction")
    satisfaction_pct = kpis["avg_satisfaction"] * 100 if kpis["avg_satisfaction"] is not None else 0
    st.markdown(
        f"""
        <div class="info-card">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="color:#6B7280; font-size:0.9rem;">Average AI-estimated client satisfaction across {kpis['analyzed_reviews']} analyzed reviews</span>
                <span style="font-weight:800; font-size:1.1rem;">{format_percent(kpis['avg_satisfaction'])}</span>
            </div>
            <div style="background:#E5E7EB; border-radius:999px; height:10px; width:100%;">
                <div style="background:{BRAND_PRIMARY}; border-radius:999px; height:10px; width:{satisfaction_pct}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
