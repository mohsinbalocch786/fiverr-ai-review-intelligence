"""Shared visual constants and CSS for the Streamlit dashboard.

Kept separate from the view modules so color/spacing choices live in one
place. This module has no analytics logic in it.
"""

SENTIMENT_COLORS = {
    "Positive": "#0CA30C",
    "Neutral": "#6B7280",
    "Negative": "#D03B3B",
    "Mixed": "#E08A2C",
}

SENTIMENT_CHIP_STYLES = {
    "Positive": {"bg": "#ECFDF3", "text": "#067647", "border": "#ABEFC6"},
    "Neutral": {"bg": "#F3F4F6", "text": "#374151", "border": "#D1D5DB"},
    "Negative": {"bg": "#FEF3F2", "text": "#B42318", "border": "#FECDCA"},
    "Mixed": {"bg": "#FFF4EB", "text": "#B54708", "border": "#FEC84B"},
    "Not Analyzed": {"bg": "#F3F4F6", "text": "#6B7280", "border": "#D1D5DB"},
}

BRAND_PRIMARY = "#4F46E5"
BRAND_PRIMARY_SOFT = "#EEF2FF"
INK = "#111827"
MUTED_INK = "#6B7280"
BORDER = "#E5E7EB"
SURFACE = "#FFFFFF"
SURFACE_SUBTLE = "#F8FAFC"

PLOTLY_TEMPLATE = "plotly_white"

# Single-hue sequential ramp (light -> dark blue) for magnitude encodings
# such as the improvement-areas-by-gig heatmap.
SEQUENTIAL_BLUE = [
    [0.0, "#EEF2FF"],
    [0.25, "#B7D3F6"],
    [0.5, "#5598E7"],
    [0.75, "#2A78D6"],
    [1.0, "#104281"],
]

CUSTOM_CSS = f"""
<style>
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    [data-testid="stSidebar"] {{
        background-color: {SURFACE_SUBTLE};
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] .sidebar-brand {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {INK};
        margin-bottom: 0.1rem;
    }}

    [data-testid="stSidebar"] .sidebar-tagline {{
        font-size: 0.8rem;
        color: {MUTED_INK};
        margin-bottom: 1.25rem;
        line-height: 1.35;
    }}

    [data-testid="stSidebar"] .sidebar-section-label {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        color: {MUTED_INK};
        text-transform: uppercase;
        margin: 1.1rem 0 0.4rem 0;
    }}

    [data-testid="stSidebar"] .sidebar-data-box {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        margin-top: 0.4rem;
    }}

    [data-testid="stSidebar"] .sidebar-data-row {{
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        padding: 0.15rem 0;
        color: {INK};
    }}

    [data-testid="stSidebar"] .sidebar-data-row span.value {{
        font-weight: 700;
    }}

    .page-title {{
        font-size: 1.9rem;
        font-weight: 800;
        color: {INK};
        margin-bottom: 0.15rem;
        letter-spacing: -0.02em;
    }}

    .page-subtitle {{
        font-size: 0.98rem;
        color: {MUTED_INK};
        margin-bottom: 1.6rem;
    }}

    .section-heading {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {INK};
        margin: 1.75rem 0 0.75rem 0;
    }}

    .kpi-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        height: 100%;
    }}

    .kpi-label {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {MUTED_INK};
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.35rem;
    }}

    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: {INK};
        line-height: 1.1;
    }}

    .kpi-caption {{
        font-size: 0.78rem;
        color: {MUTED_INK};
        margin-top: 0.3rem;
    }}

    .info-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
    }}

    .badge {{
        display: inline-block;
        padding: 0.28rem 0.7rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.15rem 0.3rem 0.15rem 0;
    }}

    .badge-strength {{
        background-color: #ECFDF3;
        color: #067647;
        border: 1px solid #ABEFC6;
    }}

    .badge-improvement {{
        background-color: #FFF4EB;
        color: #B54708;
        border: 1px solid #FEC84B;
    }}

    .badge-topic {{
        background-color: {BRAND_PRIMARY_SOFT};
        color: {BRAND_PRIMARY};
        border: 1px solid #C7D2FE;
    }}

    .sentiment-pill {{
        display: inline-block;
        padding: 0.22rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid transparent;
    }}

    .empty-state {{
        background-color: {SURFACE_SUBTLE};
        border: 1px dashed {BORDER};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: {MUTED_INK};
        font-size: 0.9rem;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        background-color: {SURFACE};
    }}
</style>
"""
