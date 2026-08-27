"""Composants visuels reutilisables du dashboard."""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from config import LOGO_PATH
from dashboard.style import inject_global_css


def kpi_card(
    label: str,
    value: str,
    delta: str = "",
    source: str = "",
    accent: str = "primary",
) -> None:
    """Affiche une carte KPI compacte et sourcee."""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    source_html = f'<div class="kpi-source">Source : {source}</div>' if source else ""
    st.markdown(
        f"""
        <div class="kpi-card accent-{accent}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            {source_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight(text: str, kind: str = "") -> None:
    """Affiche une interpretation associee a un visuel."""
    class_name = f"insight-box {kind}".strip()
    st.markdown(f'<div class="{class_name}">{text}</div>', unsafe_allow_html=True)


def render_main_header(
    title: str,
    subtitle: str,
    logo_path: Path = LOGO_PATH,
) -> None:
    """Affiche le bandeau principal avec logo optionnel."""
    logo_html = ""
    if logo_path.exists():
        logo_html = f'<img src="{logo_path.as_uri()}" alt="Logo institutionnel">'
    st.markdown(
        f"""
        <header class="app-header">
            {logo_html}
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def apply_layout(
    fig: go.Figure,
    title: str = "",
    height: int = 420,
    **kwargs: object,
) -> go.Figure:
    """Applique le layout graphique commun aux figures Plotly."""
    layout = {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#344054"},
        "hoverlabel": {
            "bgcolor": "white",
            "font": {"family": "Inter, sans-serif"},
        },
        "margin": {"l": 48, "r": 32, "t": 64 if title else 32, "b": 48},
    }
    if title:
        layout["title"] = {"text": title, "x": 0.02, "xanchor": "left"}
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig


def initialize_page() -> None:
    """Initialise la charte globale d'une page Streamlit."""
    inject_global_css()
