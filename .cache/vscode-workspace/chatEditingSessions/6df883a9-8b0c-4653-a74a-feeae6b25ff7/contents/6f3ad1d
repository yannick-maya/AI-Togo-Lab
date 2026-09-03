# Togo Energie & Forets

Projet de data science pour le defi 2 de Togo AI Lab : electrification, biomasse et forets.

## Etat du projet

Le chargement, le nettoyage, l'extraction des indicateurs, les traitements geographiques et une premiere version navigable du dashboard sont en place. Les donnees sources sont regroupees dans `data/raw/`.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Structure

- `config.py` : chemins relatifs et palette du projet
- `data/raw/` : donnees sources
- `data/processed/` : sorties Parquet generees
- `src/` : chargement, nettoyage, analyse, geographie et visualisation
- `dashboard/` : application Streamlit et pages d'analyse
- `tests/` : tests unitaires
- `reports/` : generation du rapport

## Lancement

L'application sera lancable avec :

```powershell
streamlit run dashboard/app.py
```

## Methodologie actuelle

- Les sources longues sont normalisees et les valeurs vides deviennent `NaN`.
- Les periodes de temperature comme `2013M1` sont converties en annee, mois et date mensuelle.
- Les geometries WKT sont lues en WGS84; les surfaces sont calculees en UTM 31N (EPSG:32631).
- Les indicateurs Banque mondiale sont regroupes en familles electrification, cuisson, forets et emissions.
- L'indice de priorisation combine trois composantes normalisees : ecart d'electrification (40 %), dependance bois/charbon (35 %) et pression forestiere (25 %).

## Limites

Les indicateurs d'electrification et de cuisson ne sont pas disponibles par village ou par prefecture dans les fichiers fournis. L'indice utilise donc un proxy geographique pour la pression forestiere et ne constitue pas une decision d'investissement. Les valeurs manquantes sont conservees et exclues des agregations qui ne peuvent pas les estimer.

## Validation

```powershell
python -m pytest tests/test_data_loader.py
python -m compileall -q src dashboard tests
```

La suite actuelle contient 9 tests et couvre les chargeurs, le nettoyage, l'extraction et les fonctions analytiques principales.
