"""Composants visuels reutilisables du dashboard."""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from config import LOGO_PATH
from dashboard.style import inject_global_css


def render_sidebar_brand() -> None:
    """Affiche la marque textuelle au-dessus de la navigation."""
    st.sidebar.markdown(
        '<div class="sidebar-brand"><strong>Togo AI Lab</strong><span>Défi 2 · Énergie et forêts</span></div>',
        unsafe_allow_html=True,
    )


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
    card_html = f"""
        <div class="kpi-card accent-{accent}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            {source_html}
        </div>
        """
    if hasattr(st, "html"):
        st.html(card_html)
    else:
        st.markdown(card_html, unsafe_allow_html=True)


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
    logo_column, text_column = st.columns([0.8, 5], vertical_alignment="center")
    with logo_column:
        if logo_path.exists():
            st.image(str(logo_path), width=92)
    with text_column:
        st.markdown(f"# {title}")
        st.caption(subtitle)


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
