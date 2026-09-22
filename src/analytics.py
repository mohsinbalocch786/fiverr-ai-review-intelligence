"""Deterministic, pandas-only analytics over the merged review + AI dataset.

No Streamlit, no Ollama calls, no invented numbers - every function here
derives its output strictly from the columns produced by
`src.data_loader.merge_data`. This module is safe to unit test on its own.
"""

from __future__ import annotations

import pandas as pd

from src.utils import safe_mean

SENTIMENT_ORDER = ["Positive", "Neutral", "Negative", "Mixed"]


def _analyzed(df: pd.DataFrame) -> pd.DataFrame:
    if "status" not in df.columns:
        return df.iloc[0:0]
    return df[df["status"] == "success"]


def overall_kpis(df: pd.DataFrame) -> dict:
    """Top-line KPI numbers for the Overview page."""
    total = len(df)
    analyzed_df = _analyzed(df)
    analyzed = len(analyzed_df)
    skipped = total - analyzed

    avg_rating = safe_mean(df["rating"].dropna()) if "rating" in df.columns else None
    avg_satisfaction = safe_mean(analyzed_df["satisfaction"].dropna()) if analyzed else None
    avg_confidence = safe_mean(analyzed_df["llm_confidence"].dropna()) if analyzed else None

    positive_pct = None
    if analyzed:
        positive_pct = round(
            (analyzed_df["llm_sentiment"] == "Positive").sum() / analyzed * 100, 1
        )

    return {
        "total_reviews": total,
        "analyzed_reviews": analyzed,
        "skipped_reviews": skipped,
        "avg_rating": avg_rating,
        "avg_satisfaction": avg_satisfaction,
        "avg_confidence": avg_confidence,
        "positive_pct": positive_pct,
    }


def sentiment_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Counts and percentages for each sentiment category among analyzed reviews.

    All four canonical categories (Positive/Neutral/Negative/Mixed) are
    always returned, with a count of 0 for any category absent from the
    data - this reflects the real, observed absence rather than inventing
    a number.
    """
    analyzed_df = _analyzed(df)
    total = len(analyzed_df)
    counts = analyzed_df["llm_sentiment"].value_counts()

    rows = []
    for sentiment in SENTIMENT_ORDER:
        count = int(counts.get(sentiment, 0))
        pct = round(count / total * 100, 1) if total else 0.0
        rows.append({"sentiment": sentiment, "count": count, "percentage": pct})

    return pd.DataFrame(rows)


def sentiment_by_gig(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab of sentiment counts per gig, for stacked bar charts."""
    analyzed_df = _analyzed(df)
    if analyzed_df.empty:
        return pd.DataFrame(columns=["gig", *SENTIMENT_ORDER])

    cross = pd.crosstab(analyzed_df["gig"], analyzed_df["llm_sentiment"])
    for sentiment in SENTIMENT_ORDER:
        if sentiment not in cross.columns:
            cross[sentiment] = 0
    cross = cross[SENTIMENT_ORDER].reset_index()
    return cross


def gig_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Per-gig metrics table. Deliberately unranked (no best/worst label)."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "gig", "review_count", "avg_rating", "avg_satisfaction",
                "positive_pct", "avg_confidence",
            ]
        )

    rows = []
    for gig, group in df.groupby("gig"):
        analyzed_group = group[group["status"] == "success"]
        n_analyzed = len(analyzed_group)

        positive_pct = None
        if n_analyzed:
            positive_pct = round(
                (analyzed_group["llm_sentiment"] == "Positive").sum() / n_analyzed * 100, 1
            )

        rows.append({
            "gig": gig,
            "review_count": len(group),
            "avg_rating": safe_mean(group["rating"].dropna()),
            "avg_satisfaction": safe_mean(analyzed_group["satisfaction"].dropna()) if n_analyzed else None,
            "positive_pct": positive_pct,
            "avg_confidence": safe_mean(analyzed_group["llm_confidence"].dropna()) if n_analyzed else None,
        })

    result = pd.DataFrame(rows).sort_values("review_count", ascending=False).reset_index(drop=True)
    return result


def _explode_list_column(df: pd.DataFrame, column: str) -> pd.Series:
    analyzed_df = _analyzed(df)
    if analyzed_df.empty or column not in analyzed_df.columns:
        return pd.Series(dtype=str)
    exploded = analyzed_df[column].explode().dropna()
    exploded = exploded[exploded.astype(str).str.strip() != ""]
    return exploded


def _list_frequency_table(df: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    """Shared frequency/percentage aggregation for strengths/improvement areas/topics.

    Items that are identical except for letter case (e.g. "Failed to deliver
    on time" vs "failed to deliver on time") are merged into a single row -
    this is case-normalization of the AI's own repeated phrase, not invented
    data. Distinct phrasings are never merged.
    """
    analyzed_total = len(_analyzed(df))
    exploded = _explode_list_column(df, column)

    if exploded.empty or analyzed_total == 0:
        return pd.DataFrame(columns=[label, "frequency", "percentage_of_reviews"])

    grouped = exploded.groupby(exploded.str.casefold())
    counts = grouped.size().rename("frequency")
    display_labels = grouped.agg(lambda values: values.value_counts().idxmax()).rename(label)

    result = pd.concat([display_labels, counts], axis=1).reset_index(drop=True)
    result["percentage_of_reviews"] = round(result["frequency"] / analyzed_total * 100, 1)
    return result.sort_values("frequency", ascending=False).reset_index(drop=True)


def strengths_analysis(df: pd.DataFrame, gig: str | None = None, sentiment: str | None = None) -> pd.DataFrame:
    """Aggregated strength frequency, with optional gig/sentiment filters."""
    filtered = df
    if gig and gig != "All":
        filtered = filtered[filtered["gig"] == gig]
    if sentiment and sentiment != "All":
        filtered = filtered[filtered["llm_sentiment"] == sentiment]
    return _list_frequency_table(filtered, "strengths", "strength")


def improvement_analysis(df: pd.DataFrame, gig: str | None = None, sentiment: str | None = None) -> pd.DataFrame:
    """Aggregated improvement-area frequency, with optional gig/sentiment filters.

    Reviews with an empty improvement_areas list simply contribute nothing
    to the aggregation - they are not treated as a negative signal.
    """
    filtered = df
    if gig and gig != "All":
        filtered = filtered[filtered["gig"] == gig]
    if sentiment and sentiment != "All":
        filtered = filtered[filtered["llm_sentiment"] == sentiment]
    return _list_frequency_table(filtered, "improvement_areas", "improvement_area")


def improvement_by_gig(df: pd.DataFrame) -> pd.DataFrame:
    """Improvement-area occurrence counts broken down by gig."""
    analyzed_df = _analyzed(df)
    if analyzed_df.empty:
        return pd.DataFrame(columns=["gig", "improvement_area", "frequency"])

    working = analyzed_df[["gig", "improvement_areas"]].explode("improvement_areas")
    working = working.dropna(subset=["improvement_areas"])
    working = working[working["improvement_areas"].astype(str).str.strip() != ""]

    if working.empty:
        return pd.DataFrame(columns=["gig", "improvement_area", "frequency"])

    working["improvement_area"] = working["improvement_areas"].str.casefold()
    display_labels = (
        working.groupby("improvement_area")["improvement_areas"]
        .agg(lambda values: values.value_counts().idxmax())
    )

    result = (
        working.groupby(["gig", "improvement_area"])
        .size()
        .reset_index(name="frequency")
    )
    result["improvement_area"] = result["improvement_area"].map(display_labels)
    return result


def topic_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated topic frequency across all analyzed reviews."""
    return _list_frequency_table(df, "topics", "topic")


def generate_ai_report(df: pd.DataFrame) -> dict:
    """Assemble the deterministic executive-style report shown on the AI Report page.

    Every figure is computed from the dataset via the functions above -
    nothing is generated by an LLM here.
    """
    kpis = overall_kpis(df)
    strengths = strengths_analysis(df)
    improvements = improvement_analysis(df)
    gigs = gig_performance(df)
    topics = topic_analysis(df)

    observations: list[str] = []

    if kpis["positive_pct"] is not None:
        observations.append(
            f"{kpis['positive_pct']:.0f}% of analyzed reviews were classified as Positive."
        )

    if not gigs.empty:
        top_gig = gigs.iloc[0]
        observations.append(
            f"{top_gig['gig']} accounts for {int(top_gig['review_count'])} reviews, "
            "the largest volume among all gigs."
        )

    if kpis["avg_satisfaction"] is not None:
        observations.append(
            f"Average AI satisfaction across analyzed reviews is "
            f"{kpis['avg_satisfaction'] * 100:.0f}%."
        )

    if not improvements.empty:
        top_area = improvements.iloc[0]
        observations.append(
            f"{top_area['improvement_area']} appeared in {int(top_area['frequency'])} "
            "reviews as an improvement area."
        )
    else:
        observations.append(
            "No recurring improvement areas were identified by the AI across the analyzed reviews."
        )

    if kpis["avg_confidence"] is not None:
        observations.append(
            f"The AI's average confidence in its sentiment classification is "
            f"{kpis['avg_confidence'] * 100:.0f}%."
        )

    if kpis["skipped_reviews"]:
        observations.append(
            f"{kpis['skipped_reviews']} review(s) were skipped by the AI analysis "
            "(e.g. empty review text) and are excluded from the metrics above."
        )

    return {
        "kpis": kpis,
        "strengths": strengths,
        "improvements": improvements,
        "gigs": gigs,
        "topics": topics,
        "observations": observations,
    }
