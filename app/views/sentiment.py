"""Sentiment Analysis page: distribution, sentiment-by-gig, confidence, filters."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import analytics
from app.components import empty_state, kpi_row, page_header, section_heading
from app.styles import PLOTLY_TEMPLATE, SENTIMENT_COLORS
from src.utils import format_percent


def _apply_filters(df, sentiment, gig, rating_range, satisfaction_range):
    filtered = df
    if sentiment != "All":
        filtered = filtered[filtered["llm_sentiment"] == sentiment]
    if gig != "All":
        filtered = filtered[filtered["gig"] == gig]
    filtered = filtered[
        filtered["rating"].isna() | filtered["rating"].between(rating_range[0], rating_range[1])
    ]
    filtered = filtered[
        filtered["satisfaction"].isna()
        | filtered["satisfaction"].between(satisfaction_range[0], satisfaction_range[1])
    ]
    return filtered


def render(df) -> None:
    page_header("Sentiment Analysis", "How AI-classified sentiment breaks down across the review set")

    with st.expander("Filters", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        sentiment_options = ["All"] + [s for s in analytics.SENTIMENT_ORDER]
        sentiment = c1.selectbox("Sentiment", sentiment_options)
        gig_options = ["All"] + sorted(df["gig"].dropna().unique().tolist())
        gig = c2.selectbox("Gig", gig_options)
        rating_range = c3.slider("Rating", 1.0, 5.0, (1.0, 5.0), step=0.1)
        satisfaction_range = c4.slider("Satisfaction range", 0.0, 1.0, (0.0, 1.0), step=0.05)

    filtered = _apply_filters(df, sentiment, gig, rating_range, satisfaction_range)
    analyzed = filtered[filtered["status"] == "success"]

    avg_confidence = analyzed["llm_confidence"].mean() if len(analyzed) else None

    kpi_row([
        ("Filtered Reviews", str(len(filtered)), ""),
        ("Analyzed", str(len(analyzed)), ""),
        ("AI Confidence", format_percent(avg_confidence) if avg_confidence == avg_confidence else "N/A", "Average model confidence"),
    ])

    col_left, col_right = st.columns([1, 1.4])

    with col_left:
        section_heading("Sentiment Distribution")
        sentiment_df = analytics.sentiment_summary(filtered)
        if sentiment_df["count"].sum() == 0:
            empty_state("No reviews match the current filters.")
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
            fig.update_layout(template=PLOTLY_TEMPLATE, margin=dict(t=10, b=10, l=10, r=10), height=360)
            st.plotly_chart(fig, width="stretch")

    with col_right:
        section_heading("Sentiment by Gig")
        stacked = analytics.sentiment_by_gig(filtered)
        if stacked.empty:
            empty_state("No reviews match the current filters.")
        else:
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
                barmode="stack",
                template=PLOTLY_TEMPLATE,
                margin=dict(t=10, b=10, l=10, r=10),
                height=360,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                xaxis_title=None,
                yaxis_title="Reviews",
            )
            st.plotly_chart(fig, width="stretch")
