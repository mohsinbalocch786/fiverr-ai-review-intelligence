"""Strengths page: aggregated client-praised strengths, with search and filters."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import analytics
from app.components import empty_state, page_header, section_heading
from app.styles import PLOTLY_TEMPLATE

STRENGTH_COLOR = "#0CA30C"


def render(df) -> None:
    page_header("Strengths", "What the AI most frequently identifies as client-praised strengths")

    c1, c2 = st.columns(2)
    gig_options = ["All"] + sorted(df["gig"].dropna().unique().tolist())
    gig = c1.selectbox("Gig", gig_options, key="strengths_gig")
    sentiment_options = ["All"] + analytics.SENTIMENT_ORDER
    sentiment = c2.selectbox("Sentiment", sentiment_options, key="strengths_sentiment")

    table = analytics.strengths_analysis(df, gig=gig, sentiment=sentiment)

    if table.empty:
        empty_state("No strengths identified for the current filters.")
        return

    section_heading("Top Strengths")
    top = table.head(15).sort_values("frequency")
    fig = go.Figure(
        data=[
            go.Bar(
                x=top["frequency"],
                y=top["strength"],
                orientation="h",
                marker_color=STRENGTH_COLOR,
                text=top["frequency"],
                textposition="outside",
                hovertemplate="%{y}: mentioned in %{x} reviews<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        margin=dict(t=10, b=10, l=10, r=30),
        height=max(340, 24 * len(top)),
        xaxis_title="Mentions",
        yaxis_title=None,
    )
    st.plotly_chart(fig, width="stretch")

    section_heading("All Strengths")
    search = st.text_input("Search strengths", placeholder="e.g. communication")
    display = table.copy()
    if search:
        display = display[display["strength"].str.contains(search, case=False, na=False)]

    display = display.rename(columns={
        "strength": "Strength", "frequency": "Frequency", "percentage_of_reviews": "Percentage of Reviews",
    })
    display["Percentage of Reviews"] = display["Percentage of Reviews"].map(lambda v: f"{v:.1f}%")
    st.dataframe(display, width="stretch", hide_index=True)
