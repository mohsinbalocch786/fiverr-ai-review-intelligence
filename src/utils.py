"""Small, dependency-free helpers shared by the data and analytics layers."""

from __future__ import annotations

import ast
import json
from typing import Any


def parse_json_list(value: Any) -> list[str]:
    """Safely parse a value that should be a list of strings.

    The AI analysis CSV stores list fields (strengths, improvement_areas,
    topics) as JSON-encoded strings, e.g. '["Communication", "Delivery"]'.
    Some rows may be missing, empty, malformed, or already a Python list
    (e.g. when called on in-memory data). This function never raises -
    any unparseable value simply yields an empty list.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, float):
        # NaN from pandas
        return []

    if not isinstance(value, str):
        return []

    text = value.strip()
    if not text or text.lower() == "nan":
        return []

    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
        except (ValueError, SyntaxError, TypeError):
            continue
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]

    return []


def safe_mean(series, ndigits: int = 3) -> float | None:
    """Return the rounded mean of a numeric series, or None if empty/NaN."""
    if series is None or len(series) == 0:
        return None
    value = series.mean()
    if value is None or (isinstance(value, float) and value != value):  # NaN check
        return None
    return round(float(value), ndigits)


def to_percent(value: float | None, ndigits: int = 0) -> float | None:
    """Convert a 0-1 fraction into a rounded percentage. Passes None through."""
    if value is None:
        return None
    return round(value * 100, ndigits)


def format_percent(value: float | None, ndigits: int = 0) -> str:
    """Format a 0-1 fraction as a display-ready percentage string."""
    pct = to_percent(value, ndigits)
    if pct is None:
        return "N/A"
    return f"{pct:.{ndigits}f}%"
