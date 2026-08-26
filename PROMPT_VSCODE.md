Tu es un ingénieur data / développeur Python senior. Tu m'aides à construire, de A à Z, un projet de data science professionnel pour un concours (Togo AI Lab — Défi 2 "Électrification, biomasse et forêts"). Le livrable final est un dashboard interactif Python + un rapport. Le code doit être irréprochable : propre, modulaire, documenté, testé, prêt à être jugé par un jury technique.

## Contexte métier
Le Togo veut l'accès universel à l'électricité d'ici 2030, mais les campagnes restent en retard sur les villes, et une grande majorité des ménages dépend encore du bois/charbon de bois pour cuisiner, ce qui aggrave la déforestation. Le projet doit :
1. Analyser l'écart d'électrification villes vs campagnes (et la fiabilité du réseau).
2. Évaluer la dépendance au bois/charbon et son lien avec le recul des forêts.
3. Dresser le bilan des émissions du secteur énergie vs les autres secteurs (industrie, agriculture, déchets).
4. Analyser l'évolution des températures sur 10 villes togolaises (Sud → Nord).
5. Cartographier les 53 zones protégées / forêts classées pour identifier les zones les plus vulnérables.
6. Formuler des recommandations concrètes et chiffrées (ex. priorisation de villages/zones pour l'électrification solaire, foyers de cuisson améliorés).

## Données disponibles (déjà fournies, dans `data/raw/`)
- `indicators-tgo.csv` : ~81 000 lignes, format long (`Country Name, Country ISO3, Year, Indicator Name, Indicator Code, Value`), ~3400 indicateurs Banque Mondiale pour le Togo. Contient notamment : `Access to electricity (% of population)` + variantes `rural`/`urban`, `Access to clean fuels and technologies for cooking` (+ rural/urban), `Main cooking fuel: wood/charcoal/LPG...`, `Forest area (% of land area)` / `(sq. km)`, les émissions CO2/CH4/N2O par secteur énergie (Building, Power Industry, Transport, Fugitive, Industrial Combustion), `Firms experiencing electrical outages`, etc.
- `emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv` : format long (`indicator, country, countryiso3code, date, value, unit, obs_status, decimal`) — CO2 du secteur électrique, 1970–2023, certaines valeurs `value` vides à traiter comme NaN.
- `energies-renouvelables-combustibles-et-dechets-de-lenergie-totale-.csv` : même format long, part des renouvelables/biomasse dans l'énergie totale.
- `observationdata-xorttne.csv` : colonnes `indicateur, secteur, type, Unit, Date, Value` — bilan GES 2018 par secteur (`Total`, `Energie`, `Procédés Industriels et Utilisation des Produits (PIUP)`, `Agriculture, Foresterie et autres Affectations des Terres (AFAT)`, `Déchets`) et par gaz (CO2, CH4, N2O). Encodage à vérifier (accents).
- `observationdata-yvlucze.csv` : colonnes `indicateur, libellés, villes, Unit, Date, Value` — températures min/max mensuelles pour 10 villes togolaises, `Date` au format `AAAAMMM` (ex. `2013M1`), ~1680 lignes.
- `file-zones-protegees-forets-classees-*.csv` : 53 lignes, colonnes `region_nom_bdd, prefecture_nom_bdd, commune_nom_bdd, canton_nom_bdd, nom_localite, etab_nom, etab_creation_date, geometry` où `geometry` est un `MULTIPOLYGON(...)` en WKT (lon/lat, WGS84).
- `zones-protegees-forets-classees.csv` : dictionnaire de données du fichier géo ci-dessus (référence seulement, pas de données à charger).

## Stack technique imposée
- Python 3.11+, gestion de dépendances via `requirements.txt`
- `pandas` + `pyarrow` pour le stockage intermédiaire en `.parquet`
- `shapely` + `geopandas` pour le parsing WKT et les calculs géo (centroïdes, jointures spatiales si besoin)
- `plotly` pour tous les graphiques (cohérence visuelle, interactivité) — pas de matplotlib sauf besoin ponctuel en notebook
- `streamlit` (multi-page, `st.cache_data`) pour le dashboard — layout `wide`, sidebar de filtres globaux
- `folium` ou `pydeck` via Streamlit pour la carte des zones protégées
- `pytest` pour quelques tests unitaires sur les fonctions de chargement/nettoyage
- `black` + `ruff` pour le formatage/lint

## Ce que je veux que tu fasses, étape par étape (ne saute pas d'étape, confirme avec moi avant de passer à la suivante si un choix de conception n'est pas évident)

1. **Scaffolding** : crée l'arborescence complète du projet (voir structure ci-dessous), avec des fichiers `__init__.py`, un `.gitignore` adapté (venv, `__pycache__`, `data/processed/*.parquet` si volumineux), et un `config.py` centralisant les chemins et la palette de couleurs.

```
togo-energie-forets/
├── README.md
├── requirements.txt
├── .gitignore
├── config.py
├── data/{raw,processed}/
├── src/{__init__.py, data_loader.py, cleaning.py, indicators.py, geo.py, analysis.py, viz.py}
├── dashboard/app.py + dashboard/pages/*.py
├── notebooks/00_exploration.ipynb
├── reports/build_slides.py
└── tests/test_data_loader.py
```

2. **Chargement des données** (`src/data_loader.py`) : une fonction par fichier source, avec typage explicite, gestion propre des NaN, et docstrings Google-style. Retourne des `DataFrame` normalisés (colonnes en `snake_case`, dates en `int`/`datetime` selon le cas).

3. **Nettoyage & harmonisation** (`src/cleaning.py`) : harmonise les formats "long" issus de la Banque Mondiale, gère l'encodage (accents dans les fichiers `observationdata-*`), parse `2013M1` → `(annee=2013, mois=1)` pour les températures.

4. **Extraction des indicateurs clés** (`src/indicators.py`) : depuis `indicators-tgo.csv`, isole et structure dans des tables dédiées : électrification (national/rural/urbain + fiabilité réseau), cuisson (combustibles + lieu de cuisson), forêt (surface, rents), émissions par type de gaz/secteur énergie.

5. **Géo** (`src/geo.py`) : parse les `MULTIPOLYGON` WKT avec `shapely.wkt.loads`, construit un `GeoDataFrame`, calcule centroïdes (lat/lon) et surfaces approximatives (projeter en un CRS métrique adapté au Togo, ex. EPSG:32631, avant de calculer une surface en km²).

6. **Analyse** (`src/analysis.py`) : implémente les 5 axes d'analyse listés dans le contexte métier, plus un **indice composite de priorisation par région/préfecture** (documente clairement la méthode et ses hypothèses/limites — il n'y a pas de données village par village, donc sois honnête sur le niveau de granularité réellement atteignable).

7. **Dashboard Streamlit** : une page = un axe d'analyse + une page carte + une page recommandations. KPIs en haut de page, filtres globaux dans la sidebar (période, région/ville), interprétation textuelle sous chaque visuel (pas seulement des graphiques nus — le critère principal du jury porte sur la pertinence analytique).

8. **Tests** : au moins un test par fonction de chargement/nettoyage critique (cas nominal + valeurs manquantes).

9. **README professionnel** : contexte, installation, lancement, structure du repo, choix méthodologiques, limites des données.

10. À la fin, propose-moi une checklist de vérification avant zippage (taille du zip < 20 Mo, absence d'erreurs au lancement à froid, absence de chemins codés en dur).

## Exigences de qualité non négociables
- Code modulaire, aucune logique métier dans les fichiers `dashboard/pages/*.py` (ils doivent seulement appeler `src/`)
- Pas de chemins absolus codés en dur — tout passe par `config.py`
- Docstrings + type hints partout
- Gestion explicite des valeurs manquantes (jamais un NaN affiché sans explication dans le dashboard)
- Tout le texte visible par le jury est en français correct
- Commits atomiques si tu utilises git (un commit par étape du scaffolding)

Commence par l'étape 1 (scaffolding) et montre-moi l'arborescence + le contenu de `config.py` avant de continuer.ajoute aussi le projet sur git dans ce repository :https://github.com/yannick-maya/AI-Togo-Lab.git 
