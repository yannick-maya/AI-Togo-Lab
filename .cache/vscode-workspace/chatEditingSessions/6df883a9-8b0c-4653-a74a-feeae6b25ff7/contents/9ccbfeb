"""Point d'entree de l'application Streamlit."""

import streamlit as st

from src.data_loader import load_world_bank_indicators
from src.analysis import analyze_electrification
from src.indicators import extract_key_indicators


@st.cache_data
def load_indicators() -> dict:
	"""Charge les indicateurs metier une seule fois par session."""
	return extract_key_indicators(load_world_bank_indicators())

st.set_page_config(page_title="Togo Energie & Forets", layout="wide")
st.title("Togo Energie & Forets")
st.caption("Tableau de bord d'analyse de l'electrification, de l'energie et des forets")

indicators = load_indicators()
years = sorted(
	indicators["electrification"]["year"].dropna().astype(int).unique().tolist()
)
if years:
	selected_year = st.sidebar.selectbox("Annee de reference", years, index=len(years) - 1)
else:
	selected_year = None

electrification = analyze_electrification(indicators["electrification"])
if selected_year is not None:
	electrification = electrification[electrification["year"] == selected_year]
coverage = electrification[
	[
		column
		for column in electrification.columns
		if str(column).strip() == "Access to electricity (% of population)"
	]
].stack().dropna()
gap = electrification["rural_urban_gap"].dropna()

col1, col2, col3 = st.columns(3)
col1.metric("Acces national a l'electricite", f"{coverage.iloc[0]:.1f} %" if not coverage.empty else "Donnee absente")
col2.metric("Ecart rural-urbain", f"{gap.iloc[0]:.1f} points" if not gap.empty else "Donnee absente")
col3.metric("Indicateurs disponibles", f"{sum(len(table) for table in indicators.values()):,}")

st.subheader("Perimetre des donnees")
st.write(
	"Utilisez les pages laterales pour explorer les axes d'analyse. Les valeurs absentes "
	"sont exclues des calculs et signalees lorsqu'elles ne permettent pas un KPI."
)
