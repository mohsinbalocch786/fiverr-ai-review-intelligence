"""Improvement Areas page: what the AI flags as opportunities, by gig.

Reviews with no improvement areas returned by the AI are simply excluded
from the aggregation - an empty list is not treated as a negative signal.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src import analytics
from app.components import empty_state, page_header, section_heading
from app.styles import PLOTLY_TEMPLATE, SEQUENTIAL_BLUE

IMPROVEMENT_COLOR = "#E08A2C"


def render(df) -> None:
    page_header("Improvement Areas", "What the AI most frequently flags as opportunities for improvement")

    c1, c2 = st.columns(2)
    gig_options = ["All"] + sorted(df["gig"].dropna().unique().tolist())
    gig = c1.selectbox("Gig", gig_options, key="improvement_gig")
    sentiment_options = ["All"] + analytics.SENTIMENT_ORDER
    sentiment = c2.selectbox("Sentiment", sentiment_options, key="improvement_sentiment")

    table = analytics.improvement_analysis(df, gig=gig, sentiment=sentiment)

    if table.empty:
        empty_state(
            "No improvement areas were identified by the AI for the current filters. "
            "This reflects the data - an empty result is not an error."
        )
    else:
        section_heading("Top Improvement Areas")
        top = table.head(15).sort_values("frequency")
        fig = go.Figure(
            data=[
                go.Bar(
                    x=top["frequency"],
                    y=top["improvement_area"],
                    orientation="h",
                    marker_color=IMPROVEMENT_COLOR,
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

        section_heading("All Improvement Areas")
        display = table.rename(columns={
            "improvement_area": "Improvement Area", "frequency": "Frequency",
            "percentage_of_reviews": "Percentage of Reviews",
        })
        display["Percentage of Reviews"] = display["Percentage of Reviews"].map(lambda v: f"{v:.1f}%")
        st.dataframe(display, width="stretch", hide_index=True)

    section_heading("Improvement Areas by Gig")
    by_gig = analytics.improvement_by_gig(df)
    if by_gig.empty:
        empty_state("No improvement areas were identified by the AI for any gig.")
        return

    pivot = by_gig.pivot_table(
        index="gig", columns="improvement_area", values="frequency", fill_value=0
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=SEQUENTIAL_BLUE,
            hovertemplate="%{y}<br>%{x}: %{z} mentions<extra></extra>",
            colorbar=dict(title="Mentions"),
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        margin=dict(t=10, b=10, l=10, r=10),
        height=max(320, 40 * len(pivot.index)),
        xaxis_title=None,
        yaxis_title=None,
    )
    st.plotly_chart(fig, width="stretch")
