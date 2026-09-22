"""Review Explorer: filterable review table with a full AI-analysis detail view."""

from __future__ import annotations

import streamlit as st

from app.components import badge_list, empty_state, page_header, section_heading, sentiment_pill
from src.utils import format_percent


def _apply_filters(df, gig, sentiment, rating, min_satisfaction, country):
    filtered = df
    if gig != "All":
        filtered = filtered[filtered["gig"] == gig]
    if sentiment != "All":
        filtered = filtered[filtered["llm_sentiment"] == sentiment]
    if rating != "All":
        filtered = filtered[filtered["rating"] == float(rating)]
    if country != "All":
        filtered = filtered[filtered["country"] == country]
    filtered = filtered[
        filtered["satisfaction"].isna() | (filtered["satisfaction"] >= min_satisfaction)
    ]
    return filtered


def render(df) -> None:
    page_header("Review Explorer", "Filter, browse, and inspect individual AI-analyzed reviews")

    c1, c2, c3, c4, c5 = st.columns(5)
    gig_options = ["All"] + sorted(df["gig"].dropna().unique().tolist())
    gig = c1.selectbox("Gig", gig_options)
    sentiment_options = ["All", "Positive", "Neutral", "Negative", "Mixed"]
    sentiment = c2.selectbox("Sentiment", sentiment_options)
    rating_options = ["All"] + sorted(df["rating"].dropna().unique().tolist(), reverse=True)
    rating = c3.selectbox("Rating", rating_options)
    min_satisfaction = c4.slider("Min. Satisfaction", 0.0, 1.0, 0.0, step=0.05)
    country_options = ["All"] + sorted(df["country"].dropna().unique().tolist())
    country = c5.selectbox("Country", country_options)

    filtered = _apply_filters(df, gig, sentiment, rating, min_satisfaction, country)

    section_heading(f"Reviews ({len(filtered)})")
    if filtered.empty:
        empty_state("No reviews match the current filters.")
        return

    table = filtered.copy()
    table["Review"] = table["review_text"].fillna("").str.slice(0, 90) + table["review_text"].fillna("").str.len().gt(90).map({True: "...", False: ""})
    table["Confidence"] = table["llm_confidence"].map(lambda v: format_percent(v) if v == v else "N/A")
    table["Satisfaction"] = table["satisfaction"].map(lambda v: format_percent(v) if v == v else "N/A")
    table["Sentiment"] = table["llm_sentiment"].fillna("Not Analyzed")
    display = table.rename(columns={
        "review_id": "Review ID", "gig": "Gig", "rating": "Rating",
    })[["Review ID", "Gig", "Rating", "Sentiment", "Confidence", "Satisfaction", "Review"]]
    st.dataframe(display, width="stretch", hide_index=True)

    section_heading("Inspect a Review")
    review_ids = filtered["review_id"].tolist()
    selected_id = st.selectbox("Select a Review ID", review_ids)
    review = filtered[filtered["review_id"] == selected_id].iloc[0]

    with st.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)

        top1, top2 = st.columns([2, 1])
        with top1:
            st.markdown(f"**Gig:** {review['gig']}  \n**Country:** {review['country']}  \n**Designation:** {review['designation']}")
            st.markdown(f"> {review['review_text']}")
        with top2:
            st.markdown(f"**Rating:** {review['rating']:.1f} / 5" if review["rating"] == review["rating"] else "**Rating:** N/A")
            st.markdown(f"**Status:** {review['status']}")

        if review["status"] != "success":
            empty_state(f"This review was not analyzed by the AI. Reason: {review.get('error', 'unknown')}")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        st.markdown("#### AI Analysis")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("**Sentiment**")
            st.markdown(sentiment_pill(review["llm_sentiment"]), unsafe_allow_html=True)
        m2.metric("Confidence", format_percent(review["llm_confidence"]))
        m3.metric("Satisfaction", format_percent(review["satisfaction"]))

        st.markdown("**Strengths**")
        if review["strengths"]:
            st.markdown(badge_list(review["strengths"], "badge-strength"), unsafe_allow_html=True)
        else:
            empty_state("No strengths identified.")

        st.markdown("**Improvement Areas**")
        if review["improvement_areas"]:
            st.markdown(badge_list(review["improvement_areas"], "badge-improvement"), unsafe_allow_html=True)
        else:
            empty_state("No specific improvement area identified.")

        st.markdown("**Topics**")
        if review["topics"]:
            st.markdown(badge_list(review["topics"], "badge-topic"), unsafe_allow_html=True)
        else:
            empty_state("No topics identified.")

        st.markdown("**AI Explanation**")
        st.write(review["explanation"] if isinstance(review["explanation"], str) else "N/A")

        st.markdown("**Recommendation**")
        st.write(review["recommendation"] if isinstance(review["recommendation"], str) else "N/A")

        st.markdown("</div>", unsafe_allow_html=True)
