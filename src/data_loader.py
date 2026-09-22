"""Loading and merging of the raw Fiverr review export and the existing
Ollama Cloud AI analysis output.

This module is intentionally free of any UI/rendering logic. It only reads
CSV files, normalizes columns, and merges the two datasets into a single
tidy DataFrame that the analytics layer and the Streamlit app can consume.

Nothing here calls Ollama. The AI analysis is treated as a static,
already-computed artifact (outputs/llm_review_analysis.csv).

If the real data files aren't present (they're gitignored - see
data/raw/.gitignore-relevant entries), every loader transparently falls
back to the bundled sample dataset (data/raw/sample_fiverr_reviews.csv,
outputs/sample_llm_review_analysis.csv) so the app still runs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.utils import parse_json_list

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_REVIEWS_PATH = PROJECT_ROOT / "data" / "raw" / "fiverr_reviews.csv"
AI_RESULTS_PATH = PROJECT_ROOT / "outputs" / "llm_review_analysis.csv"

# Real review data is gitignored (see .gitignore) so it never leaves this
# machine. These small, synthetic datasets ship with the repo so the
# dashboard is fully functional immediately after a fresh clone.
SAMPLE_RAW_REVIEWS_PATH = PROJECT_ROOT / "data" / "raw" / "sample_fiverr_reviews.csv"
SAMPLE_AI_RESULTS_PATH = PROJECT_ROOT / "outputs" / "sample_llm_review_analysis.csv"

RAW_COLUMN_MAP = {
    "DESIGNATION": "designation",
    "COUNTRY": "country",
    "STARS": "rating",
    "DURATION": "duration",
    "AGE": "review_age",
    "REVIEW": "review_text",
    "GIG": "gig",
    "SCREENSHOTS": "screenshot",
}

AI_LIST_COLUMNS = ["strengths", "improvement_areas", "topics"]

SENTIMENT_ORDER = ["Positive", "Neutral", "Negative", "Mixed"]


def _resolve_path(path: str | Path, sample_path: Path) -> Path:
    """Fall back to the bundled sample dataset if the real file is absent."""
    path = Path(path)
    if path.exists():
        return path
    return sample_path


def using_sample_data(reviews_path: str | Path = RAW_REVIEWS_PATH) -> bool:
    """True when the dashboard is serving the bundled sample dataset
    because no real review export was found at `reviews_path`."""
    return not Path(reviews_path).exists()


@st.cache_data(show_spinner=False)
def load_reviews(path: str | Path = RAW_REVIEWS_PATH) -> pd.DataFrame:
    """Load and clean the original Fiverr review export.

    The source CSV also carries a stray pivot-table (Country/Gig count
    columns) tacked onto the right side of the sheet, plus a handful of
    fully-blank spacer rows. Both are dropped here. A stable `review_id`
    is assigned by row position, which is how the existing AI analysis
    output keyed its own `review_id` column.
    """
    path = _resolve_path(path, SAMPLE_RAW_REVIEWS_PATH)
    if not path.exists():
        return pd.DataFrame(columns=["review_id", *RAW_COLUMN_MAP.values()])

    df = pd.read_csv(path)

    for source_col in RAW_COLUMN_MAP:
        if source_col not in df.columns:
            df[source_col] = pd.NA

    df = df[list(RAW_COLUMN_MAP.keys())].rename(columns=RAW_COLUMN_MAP)
    df = df.dropna(subset=["review_text"]).reset_index(drop=True)
    df.insert(0, "review_id", df.index + 1)

    df["gig"] = df["gig"].fillna("Not Specified").replace("", "Not Specified")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["country"] = df["country"].fillna("Unknown")
    df["designation"] = df["designation"].fillna("Unknown")

    return df


@st.cache_data(show_spinner=False)
def load_ai_results(path: str | Path = AI_RESULTS_PATH) -> pd.DataFrame:
    """Load the existing AI analysis output produced offline via Ollama Cloud.

    List-like fields (strengths, improvement_areas, topics) are parsed
    from their JSON-string form into real Python lists. Rows with
    malformed JSON simply yield empty lists rather than raising.
    """
    path = _resolve_path(path, SAMPLE_AI_RESULTS_PATH)
    expected_cols = [
        "review_id", "llm_sentiment", "llm_confidence", "satisfaction",
        "strengths", "improvement_areas", "topics", "explanation",
        "recommendation", "status", "error", "processed_at",
    ]
    if not path.exists():
        return pd.DataFrame(columns=expected_cols)

    df = pd.read_csv(path)

    for col in expected_cols:
        if col not in df.columns:
            df[col] = pd.NA

    df["review_id"] = pd.to_numeric(df["review_id"], errors="coerce")
    df = df.dropna(subset=["review_id"])
    df["review_id"] = df["review_id"].astype(int)

    for col in AI_LIST_COLUMNS:
        df[col] = df[col].apply(parse_json_list)

    df["llm_confidence"] = pd.to_numeric(df["llm_confidence"], errors="coerce")
    df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")
    df["status"] = df["status"].fillna("unknown")
    df["analyzed"] = df["status"] == "success"

    return df


@st.cache_data(show_spinner=False)
def merge_data(
    reviews_path: str | Path = RAW_REVIEWS_PATH,
    ai_path: str | Path = AI_RESULTS_PATH,
) -> pd.DataFrame:
    """Merge review metadata onto the AI analysis output.

    The AI results file defines the universe of reviews the dashboard
    reports on (e.g. 99 total, 98 analyzed, 1 skipped). Review metadata
    (gig, rating, country, review text, ...) is attached via a left join
    on `review_id` so every AI-analyzed row - including the skipped one -
    is preserved even if metadata is imperfect.
    """
    reviews = load_reviews(reviews_path)
    ai_results = load_ai_results(ai_path)

    if ai_results.empty:
        return ai_results

    merged = ai_results.merge(reviews, on="review_id", how="left")

    merged["gig"] = merged["gig"].fillna("Not Specified")
    merged["country"] = merged["country"].fillna("Unknown")

    return merged
