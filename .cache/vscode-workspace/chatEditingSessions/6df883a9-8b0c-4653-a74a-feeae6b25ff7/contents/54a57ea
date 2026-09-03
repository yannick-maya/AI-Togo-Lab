# Togo Energie & Forets

Projet de data science pour le defi 2 de Togo AI Lab : electrification, biomasse et forets.

## Etat du projet

Le chargement, le nettoyage, l'extraction des indicateurs, les traitements geographiques et une version professionnelle navigable du dashboard sont en place. Les donnees sources sont regroupees dans `data/raw/`.

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
Elle peut aussi etre lancee depuis le dossier `dashboard` :

```powershell
cd dashboard
streamlit run app.py
```

Le point d'entree ajoute automatiquement la racine du projet au chemin Python;
les deux commandes sont donc equivalentes.

## Methodologie actuelle

- Les sources longues sont normalisees et les valeurs vides deviennent `NaN`.
- Les periodes de temperature comme `2013M1` sont converties en annee, mois et date mensuelle.
- Les geometries WKT sont lues en WGS84; les surfaces sont calculees en UTM 31N (EPSG:32631).
- Les indicateurs Banque mondiale sont regroupes en familles electrification, cuisson, forets et emissions.
- L'indice de priorisation combine trois composantes normalisees : ecart d'electrification (40 %), dependance bois/charbon (35 %) et pression forestiere (25 %).
- Le dashboard propose des filtres persistants par annee, ville et region lorsque la granularite de la source le permet, ainsi que des visualisations Plotly avec sources et interpretations.
- Le logo est optionnel : il sera automatiquement affiche depuis `dashboard/assets/logo.png` lorsqu'il sera fourni.

## Limites

Les indicateurs d'electrification et de cuisson ne sont pas disponibles par village ou par prefecture dans les fichiers fournis. L'indice utilise donc un proxy geographique pour la pression forestiere et ne constitue pas une decision d'investissement. Les valeurs manquantes sont conservees et exclues des agregations qui ne peuvent pas les estimer.

## Validation

```powershell
python -m pytest tests/test_data_loader.py
python -m compileall -q src dashboard tests
```

La suite actuelle contient 9 tests et couvre les chargeurs, le nettoyage, l'extraction et les fonctions analytiques principales. Le dashboard a aussi ete compile et demarre en mode headless pendant les validations.

### Procedure de test manuel

1. Lancer Streamlit avec l'une des commandes ci-dessus et ouvrir l'URL locale affichee, generalement `http://localhost:8501`.
2. Ouvrir la page `Electrification`, choisir successivement la derniere annee disponible, une annee intermediaire puis la premiere annee disponible. La courbe et l'aire de l'ecart doivent changer.
3. Ouvrir la page `Climat`, choisir `Toutes` puis deux villes differentes. La courbe et la heatmap doivent se filtrer sur la ville choisie.
4. Ouvrir `Zones protegees`, choisir `Toutes` puis deux regions differentes. Le nombre de points, la surface et l'histogramme regional doivent changer.
5. Ouvrir `Recommandations`, choisir `Toutes` puis une region. Le tableau et le nuage de points doivent afficher uniquement la selection.
6. Verifier qu'une selection sans observation affiche `Aucune donnée pour cette sélection` au lieu d'un graphique vide.
7. Verifier la sidebar : les filtres restent coherents en naviguant entre les pages. Le logo est affiche automatiquement lorsqu'il existe dans `dashboard/assets/logo.png`.

Pour un test de demarrage sans interaction navigateur :

```powershell
streamlit run dashboard/app.py --server.headless true --server.port 8511
```

Arreter ensuite le serveur avec `Ctrl+C`.
