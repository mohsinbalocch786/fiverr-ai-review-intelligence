"""Gig Performance page: objective per-gig metrics table, charts, and detail drill-down.

Deliberately does not rank gigs as "best" or "worst" - metrics are presented
side by side so the reader can draw their own conclusions.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import analytics
from app.components import badge_list, empty_state, page_header, section_heading
from app.styles import BRAND_PRIMARY, PLOTLY_TEMPLATE, SENTIMENT_COLORS
from src.utils import format_percent


def render(df) -> None:
    page_header("Gig Performance", "Objective metrics for every gig, side by side")

    gig_table = analytics.gig_performance(df)

    if gig_table.empty:
        empty_state("No gig data available.")
        return

    # Fixed order (by review volume) reused across every chart on this page
    # so gigs are never re-sorted by a quality metric, which would read as ranking.
    gig_order = gig_table["gig"].tolist()

    section_heading("Gig Metrics")
    display_table = gig_table.copy()
    display_table["avg_rating"] = display_table["avg_rating"].map(lambda v: f"{v:.1f}" if v is not None else "N/A")
    display_table["avg_satisfaction"] = display_table["avg_satisfaction"].map(
        lambda v: format_percent(v) if v is not None else "N/A"
    )
    display_table["positive_pct"] = display_table["positive_pct"].map(
        lambda v: f"{v:.0f}%" if v is not None else "N/A"
    )
    display_table["avg_confidence"] = display_table["avg_confidence"].map(
        lambda v: format_percent(v) if v is not None else "N/A"
    )
    display_table.columns = [
        "Gig", "Review Count", "Average Rating", "AI Satisfaction", "Positive Sentiment %", "AI Confidence",
    ]
    st.dataframe(display_table, width="stretch", hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        section_heading("Reviews by Gig")
        ordered = gig_table.set_index("gig").loc[gig_order].reset_index()
        fig = go.Figure(
            data=[
                go.Bar(
                    x=ordered["gig"],
                    y=ordered["review_count"],
                    marker_color=BRAND_PRIMARY,
                    text=ordered["review_count"],
                    textposition="outside",
                    hovertemplate="%{x}: %{y} reviews<extra></extra>",
                )
            ]
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, margin=dict(t=10, b=10, l=10, r=10), height=340, xaxis_title=None, yaxis_title="Reviews")
        st.plotly_chart(fig, width="stretch")

    with col2:
        section_heading("Satisfaction by Gig")
        ordered = gig_table.set_index("gig").loc[gig_order].reset_index()
        ordered = ordered.dropna(subset=["avg_satisfaction"])
        if ordered.empty:
            empty_state("No satisfaction data available.")
        else:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=ordered["gig"],
                        y=(ordered["avg_satisfaction"] * 100).round(1),
                        marker_color=BRAND_PRIMARY,
                        text=(ordered["avg_satisfaction"] * 100).round(0).astype(int).astype(str) + "%",
                        textposition="outside",
                        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
                    )
                ]
            )
            fig.update_layout(
                template=PLOTLY_TEMPLATE, margin=dict(t=10, b=10, l=10, r=10), height=340,
                xaxis_title=None, yaxis_title="AI Satisfaction (%)", yaxis_range=[0, 105],
            )
            st.plotly_chart(fig, width="stretch")

    section_heading("Sentiment by Gig")
    stacked = analytics.sentiment_by_gig(df)
    if stacked.empty:
        empty_state("No analyzed reviews available.")
    else:
        stacked = stacked.set_index("gig").loc[[g for g in gig_order if g in stacked.set_index("gig").index]].reset_index()
        fig = go.Figure()
        for sentiment_name in analytics.SENTIMENT_ORDER:
            fig.add_trace(
                go.Bar(
                    name=sentiment_name,
                    x=stacked["gig"],
                    y=stacked[sentiment_name],
                    marker_color=SENTIMENT_COLORS[sentiment_name],
                    hovertemplate=f"%{{x}}<br>{sentiment_name}: %{{y}}<extra></extra>",
                )
            )
        fig.update_layout(
            barmode="stack", template=PLOTLY_TEMPLATE, margin=dict(t=10, b=10, l=10, r=10), height=360,
            legend=dict(orientation="h", yanchor="bottom", y=1.02), xaxis_title=None, yaxis_title="Reviews",
        )
        st.plotly_chart(fig, width="stretch")

    section_heading("Gig Details")
    for _, row in gig_table.iterrows():
        gig_name = row["gig"]
        with st.expander(f"{gig_name}  ·  {int(row['review_count'])} reviews"):
            m1, m2, m3 = st.columns(3)
            m1.metric("Average Rating", f"{row['avg_rating']:.1f}" if row["avg_rating"] is not None else "N/A")
            m2.metric("AI Satisfaction", format_percent(row["avg_satisfaction"]))
            m3.metric("Positive Sentiment", f"{row['positive_pct']:.0f}%" if row["positive_pct"] is not None else "N/A")

            gig_df = df[df["gig"] == gig_name]
            strengths = analytics.strengths_analysis(gig_df)
            improvements = analytics.improvement_analysis(gig_df)

            st.markdown("**Strengths**")
            if strengths.empty:
                empty_state("No strengths identified by the AI for this gig.")
            else:
                st.markdown(badge_list(strengths["strength"].head(8).tolist(), "badge-strength"), unsafe_allow_html=True)

            st.markdown("**Improvement Areas**")
            if improvements.empty:
                empty_state("No specific improvement area identified.")
            else:
                st.markdown(badge_list(improvements["improvement_area"].head(8).tolist(), "badge-improvement"), unsafe_allow_html=True)
