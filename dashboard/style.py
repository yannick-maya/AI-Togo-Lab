"""Systeme de design partage du dashboard."""

import streamlit as st

from config import COLORS


def inject_global_css() -> None:
    """Injecte la charte graphique commune dans l'application."""
    st.markdown(
        f"""
        <style>
        :root {{
            --color-electricity: {COLORS['electricity']};
            --color-electricity-light: {COLORS['electricity_light']};
            --color-cooking: {COLORS['cooking']};
            --color-forest: {COLORS['forest']};
            --color-forest-light: {COLORS['forest_light']};
            --color-emissions: {COLORS['emissions']};
            --color-temperature: {COLORS['temperature']};
            --color-neutral: {COLORS['neutral']};
            --color-background: {COLORS['background']};
        }}

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: var(--color-background);
        }}

        [data-testid="stSidebar"] {{
            background: #ffffff;
            border-right: 1px solid var(--color-neutral);
            box-shadow: 2px 0 12px rgba(16, 24, 40, 0.04);
        }}

        .sidebar-brand {{
            padding: 0.75rem 0.6rem 0.9rem;
            border-bottom: 1px solid var(--color-neutral);
        }}

        .sidebar-brand strong {{
            display: block;
            color: var(--color-forest);
            font-size: 1.05rem;
        }}

        .sidebar-brand span {{
            display: block;
            margin-top: 0.2rem;
            color: var(--color-neutral);
            font-size: 0.75rem;
        }}

        .sidebar-section-title {{
            margin: 0.85rem 0 0.5rem;
            color: var(--bleu);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        [data-testid="stSidebarNav"] {{
            padding: 0.75rem 0.35rem 0.9rem;
            border-bottom: 1px solid var(--color-neutral);
        }}

        [data-testid="stSidebarNav"] li {{
            margin: 0.2rem 0;
        }}

        [data-testid="stSidebarNav"] a {{
            padding: 0.55rem 0.7rem;
            border-radius: 6px;
            color: #344054;
            font-size: 0.95rem;
            font-weight: 500;
            transition: background-color 120ms ease, color 120ms ease;
        }}

        [data-testid="stSidebarNav"] a:not([aria-current="page"]):hover {{
            background: var(--color-electricity-light);
            color: var(--color-forest);
        }}

        [data-testid="stSidebarNav"] a:focus-visible {{
            outline: 2px solid var(--color-cooking);
            outline-offset: 2px;
        }}

        [data-testid="stSidebarNav"] a[aria-current="page"] {{
            background: var(--color-forest);
            box-shadow: inset 4px 0 0 var(--color-cooking);
            color: #ffffff;
            font-weight: 700;
        }}

        [data-testid="stSidebarNav"] li:nth-of-type(2) {{
            margin-top: 0.75rem;
            padding-top: 1.1rem;
            border-top: 1px solid var(--color-neutral);
        }}

        [data-testid="stSidebarNav"] li:nth-of-type(2)::before {{
            content: "Diagnostic thématique";
            display: block;
            margin-bottom: 0.55rem;
            color: var(--color-forest);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        [data-testid="stSidebarNav"] li:nth-of-type(6) {{
            margin-top: 0.75rem;
            padding-top: 1.1rem;
            border-top: 1px solid var(--color-neutral);
        }}

        [data-testid="stSidebarNav"] li:nth-of-type(6)::before {{
            content: "Territoire";
            display: block;
            margin-bottom: 0.55rem;
            color: var(--color-forest);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        [data-testid="stSidebarNav"] li:nth-of-type(7) {{
            margin-top: 0.75rem;
            padding-top: 1.1rem;
            border-top: 1px solid var(--color-neutral);
        }}

        [data-testid="stSidebarNav"] li:nth-of-type(7)::before {{
            content: "Synthèse";
            display: block;
            margin-bottom: 0.55rem;
            color: var(--color-forest);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        .app-header {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.5rem;
            background: white;
            border-left: 6px solid var(--color-forest);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.08);
        }}

        .app-header img {{
            width: 92px;
            max-height: 64px;
            object-fit: contain;
        }}

        .app-header h1 {{
            margin: 0;
            color: var(--color-forest);
            font-size: 1.8rem;
            line-height: 1.2;
        }}

        .app-header p {{
            margin: 0.35rem 0 0;
            color: var(--color-neutral);
            font-size: 0.95rem;
        }}

        .section-title {{
            margin: 1.5rem 0 0.75rem;
            color: var(--color-forest);
            font-size: 1.25rem;
            font-weight: 700;
        }}

        .filter-navbar__title {{
            margin: -0.25rem 0 0.4rem;
            color: var(--color-forest);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        .st-key-filter_navbar {{
            display: flex;
            flex-wrap: wrap;
            align-items: flex-end;
            gap: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            padding: 1rem 1.25rem;
            background: #ffffff;
            border: 1px solid var(--color-neutral);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.06);
        }}

        .st-key-filter_navbar [data-testid="stHorizontalBlock"] {{
            gap: 1.5rem;
        }}

        .st-key-filter_navbar label {{
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--color-neutral);
        }}

        .kpi-card {{
            min-height: 112px;
            padding: 1rem 1.1rem;
            background: white;
            border-top: 4px solid var(--color-electricity);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.08);
        }}

        .kpi-card.accent-cooking {{ border-top-color: var(--color-cooking); }}
        .kpi-card.accent-forest {{ border-top-color: var(--color-forest); }}
        .kpi-card.accent-emissions {{ border-top-color: var(--color-emissions); }}
        .kpi-card.accent-temperature {{ border-top-color: var(--color-temperature); }}

        .kpi-label {{
            color: var(--color-neutral);
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .kpi-value {{
            margin-top: 0.45rem;
            color: #101828;
            font-size: 1.65rem;
            font-weight: 700;
        }}

        .kpi-delta, .kpi-source {{
            color: var(--color-neutral);
            font-size: 0.75rem;
        }}

        .insight-box {{
            height: 100%;
            padding: 1rem;
            background: white;
            border-left: 4px solid var(--color-neutral);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.06);
            color: #344054;
            line-height: 1.55;
        }}

        .insight-box.warning {{
            border-left-color: var(--color-cooking);
            background: #fffaf5;
        }}

        .insight-box.alert {{
            border-left-color: var(--color-emissions);
            background: #fff7f6;
        }}

        .data-table {{
            margin: 1.25rem 0 1.5rem;
            overflow-x: auto;
            background: #ffffff;
            border: 1px solid var(--color-neutral);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.06);
        }}

        .data-table__caption {{
            padding: 0.7rem 1rem 0.4rem;
            color: var(--color-forest);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .data-table table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            color: #344054;
        }}

        .data-table thead th {{
            background: #eef2f6;
            color: #1b4332;
            font-weight: 700;
            text-align: left;
            padding: 0.6rem 0.9rem;
            border-bottom: 2px solid var(--color-neutral);
            white-space: nowrap;
        }}

        .data-table tbody td {{
            padding: 0.55rem 0.9rem;
            border-bottom: 1px solid #eef2f6;
        }}

        .data-table tbody tr:nth-child(even) {{
            background: #f8fafc;
        }}

        .data-table tbody tr:last-child td {{
            border-bottom: none;
        }}

        .data-table td.num {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}

        .recommendation-box {{
            margin-top: 2rem;
            padding: 1.1rem 1.3rem;
            background: #ffffff;
            border-left: 6px solid var(--color-forest);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.08);
        }}

        .recommendation-box .recommendation-title {{
            color: var(--color-forest);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }}

        .recommendation-box .recommendation-text {{
            color: #344054;
            line-height: 1.6;
            font-size: 0.95rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
