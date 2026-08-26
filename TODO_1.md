# TODO — Défi 2 : Électrification, Biomasse & Forêts (Togo AI Lab)

> Objectif : livrer un dashboard Python professionnel + un rapport PowerPoint (≤10 slides) qui maximisent les 5 critères de notation, avant le **31 août 2026**.

---

## 0. Cadrage du défi (rappel)

| Élément | Détail |
|---|---|
| Question centrale | Comment identifier/prioriser les zones rurales non-électrifiées sans aggraver la pression sur les forêts (bois-énergie) ? |
| Livrable 1 | Dashboard interactif (.zip) — Power BI **ou Python** (notre choix) |
| Livrable 2 | Rapport PowerPoint, **10 slides max**, méthodo + résultats + recommandations |
| Format de soumission | ZIP + PPTX, 20 Mo max par fichier |
| Deadline candidature | 31 août 2026 |
| Résultats | 4 septembre 2026 |
| Limite | 3 soumissions max par candidat → traiter la 1ère comme la version quasi-finale |

### Grille de notation (barème /20, ramené /100)
- **C1 — Ergonomie & clarté visuelle du dashboard** → 4 pts
- **C2 — Pertinence des analyses & qualité des conclusions** → 8 pts *(le plus gros poste : soigner l'interprétation, pas juste les graphiques)*
- **C3 — Richesse des interactions / filtres / fluidité** → 4 pts
- **C4 — Structure, méthodologie & qualité rédactionnelle du rapport** → 4 pts
- **C5 — non capturé dans le document source** (le texte annonce "5 critères" mais seuls 4 totalisant 20 pts apparaissent dans le fichier extrait) → **⚠️ vérifier sur datalab.gouv.tg avant la soumission finale**, probablement lié à la qualité des recommandations/impact.

**Conséquence stratégique** : C2 pèse 40% de la note → l'essentiel de l'effort doit aller dans la *profondeur analytique* (croisements entre jeux de données, pas juste des graphiques isolés) et dans des **recommandations chiffrées et actionnables**, pas seulement dans le style visuel.

---

## 1. Jeux de données fournis (déjà inspectés)

| Fichier | Contenu | Granularité | Usage principal |
|---|---|---|---|
| `indicators-tgo.csv` (81k lignes) | ~3400 indicateurs Banque Mondiale pour le Togo | National, annuel | **Pivot central** : accès électricité (rural/urbain), combustibles de cuisson, forêts, émissions par secteur/gaz |
| `emissions-...-co2-...mt-co2e-.csv` | CO2 secteur énergie/production électrique | National, annuel 1970–2023 | Séries longues émissions électricité |
| `energies-renouvelables-...-.csv` | Part renouvelables/biomasse dans énergie totale | National, annuel | Mix énergétique, dépendance biomasse |
| `observationdata-xorttne.csv` | Émissions GES par secteur (Énergie, PIUP, AFAT, Déchets) et par gaz | National, 2018 (coupe transversale) | Bilan comparatif sectoriel (camembert/waterfall) |
| `observationdata-yvlucze.csv` (1681 lignes) | Températures min/max mensuelles, 10 villes | Ville × mois, 2013→ | Analyse climatique Nord/Sud |
| `file-zones-protegees-forets-classees-*.csv` | 53 zones protégées/forêts classées + géométrie (WKT MultiPolygon) | Zone (région/préfecture/commune/canton) | Cartographie + score de vulnérabilité |
| `zones-protegees-forets-classees.csv` | Dictionnaire de données du fichier géo ci-dessus | — | Référence uniquement (pas de données) |

⚠️ **Limite majeure à anticiper** : aucun jeu de données ne géolocalise les villages non-électrifiés eux-mêmes. Le taux d'électrification rural/urbain n'est disponible qu'au niveau **national**. La "priorisation géographique" devra donc s'appuyer sur un **indice composite par région/préfecture** croisant forêts classées (pression biomasse potentielle) + indicateurs nationaux désagrégés quand ils existent dans `indicators-tgo.csv` (vérifier s'il y a des séries régionales, sinon le dire explicitement dans le rapport comme hypothèse/limite assumée).

---

## 2. Architecture du projet Python (à faire scaffolder)

```
togo-energie-forets/
├── README.md
├── TODO.md
├── requirements.txt
├── .gitignore
├── config.py                    # chemins, palette couleurs, constantes
├── data/
│   ├── raw/                     # CSV originaux, jamais modifiés
│   └── processed/               # parquet/csv nettoyés, prêts à l'emploi
├── src/
│   ├── __init__.py
│   ├── data_loader.py           # lecture + typage de chaque source
│   ├── cleaning.py              # nettoyage, harmonisation des dates/valeurs
│   ├── indicators.py            # extraction des indicateurs clés depuis indicators-tgo.csv
│   ├── geo.py                   # parsing WKT, GeoDataFrame, calcul de centroïdes/surfaces
│   ├── analysis.py              # calculs métier (écarts urbain/rural, corrélations, index composite)
│   └── viz.py                   # fonctions de graphiques réutilisables (Plotly)
├── dashboard/
│   ├── app.py                   # point d'entrée Streamlit
│   └── pages/
│       ├── 1_Vue_generale.py
│       ├── 2_Electrification.py
│       ├── 3_Energie_menages_deforestation.py
│       ├── 4_Emissions.py
│       ├── 5_Climat.py
│       ├── 6_Carte_zones_protegees.py
│       └── 7_Recommandations.py
├── notebooks/
│   └── 00_exploration.ipynb     # brouillon EDA, non livré tel quel
├── reports/
│   └── build_slides.py          # (optionnel) génération assistée du PPTX
└── tests/
    └── test_data_loader.py
```

---

## 3. Plan de travail (5 jours restants avant le 31/08)

### Jour 1 (aujourd'hui, 26/08) — Fondations
- [ ] Créer le repo/venv, `requirements.txt` (pandas, geopandas/shapely, plotly, streamlit, folium/pydeck, pyarrow)
- [ ] Copier les 6 CSV dans `data/raw/`
- [ ] Écrire `src/data_loader.py` : un loader dédié par fichier, avec typage explicite (dates, floats), gestion des valeurs manquantes (`value` vide dans les fichiers émissions/renouvelables)
- [ ] Écrire `src/geo.py` : parser les `MULTIPOLYGON(...)` en géométries Shapely → GeoDataFrame avec centroïde (lat/lon) par zone
- [ ] Notebook d'exploration rapide : lister les indicateurs utiles dans `indicators-tgo.csv` (électricité, cuisson, forêt, émissions) et sortir un sous-CSV propre

### Jour 2 (27/08) — Nettoyage & analyse cœur
- [ ] `src/cleaning.py` : harmoniser les formats (World Bank long format vs colonnes larges), unités, années
- [ ] `src/analysis.py` :
  - [ ] Écart accès électricité urbain vs rural dans le temps (+ vitesse de convergence, projection simple vers 2030)
  - [ ] Dépendance bois/charbon pour la cuisson (tendance + comparaison rural/urbain si dispo) vs évolution surface forestière
  - [ ] Bilan sectoriel des émissions (Énergie vs PIUP vs AFAT vs Déchets) — part de l'énergie dans le total
  - [ ] Séries CO2 électricité 1970–2023 et lien avec part de renouvelables
  - [ ] Températures : tendance par ville, gradient Sud→Nord, anomalies
  - [ ] Indice composite de priorisation par région (forêts classées à proximité + poids démographique si dispo) — **documenter la méthode et ses limites**
- [ ] Exporter tous les tableaux finaux en `data/processed/*.parquet`

### Jour 3 (28/08) — Dashboard Streamlit (v1 complète)
- [ ] `dashboard/app.py` + pages listées ci-dessus, avec filtres transverses (période, ville/région)
- [ ] Carte interactive des 53 zones protégées (Plotly/Folium), couleur = score de vulnérabilité, popup avec métadonnées (région, préfecture, année de création)
- [ ] KPIs en en-tête de chaque page (grands chiffres : % électrification, écart urbain/rural, Mt CO2, etc.)
- [ ] Vérifier la fluidité (C3) : sélecteurs, tooltips, pas de temps de chargement excessif sur `indicators-tgo.csv` (filtrer tôt, mettre en cache `@st.cache_data`)

### Jour 4 (29/08) — Finition dashboard + design (C1)
- [ ] Charte graphique cohérente (palette : vert forêt / bleu énergie / ocre alerte — cf. section 4)
- [ ] Textes d'interprétation sous chaque graphique (pas seulement des chiffres bruts — c'est ce qui rapporte des points sur C2)
- [ ] Page "Recommandations" avec actions concrètes chiffrées (ex. nb de kits solaires, foyers améliorés à cibler, zones prioritaires)
- [ ] Tests manuels multi-résolution (le jury regardera probablement sur laptop standard)
- [ ] Rédiger `README.md` (installation, lancement `streamlit run dashboard/app.py`, structure)

### Jour 5 (30/08) — Rapport PowerPoint + packaging
- [ ] Construire les 10 slides (plan proposé en section 5)
- [ ] Exporter captures d'écran soignées du dashboard pour illustrer le PPTX
- [ ] Relire pour C4 : structure claire, méthodologie explicite, orthographe
- [ ] Zipper le projet (code + data/processed, exclure `.venv`, `__pycache__`) en respectant 20 Mo max
- [ ] Test à froid : cloner/dézipper dans un dossier neuf et vérifier que tout tourne avec juste `pip install -r requirements.txt`

### 31/08 — Marge de sécurité
- [ ] Soumission finale avant la deadline (ne pas attendre la dernière heure)
- [ ] Vérifier le critère C5 manquant sur la plateforme officielle avant l'envoi

---

## 4. Direction artistique du dashboard (pour gagner sur C1)

- **Palette** : vert forêt `#1B4332` / `#40916C` (forêts, durabilité), bleu énergie `#1D3557` / `#457B9D` (électricité), ocre/orange `#E76F51` (alerte, déficit, biomasse), gris neutre pour le fond.
- **Typographie** : une seule police sans-serif (Inter, Lato ou la police par défaut Streamlit), tailles cohérentes de titres.
- **Layout** : `st.set_page_config(layout="wide")`, sidebar pour les filtres globaux, colonnes pour aligner KPI + graphique.
- **Un message clé par slide/page**, pas de surcharge de graphiques.

## 5. Plan de rapport PowerPoint (10 slides)

1. Titre + équipe + défi
2. Contexte & problématique (fracture électrique / bois-énergie / forêts)
3. Données & méthodologie (les 6 sources, limites assumées)
4. Résultat 1 — Fracture d'électrification urbain/rural
5. Résultat 2 — Dépendance biomasse & pression sur les forêts
6. Résultat 3 — Bilan des émissions du secteur énergie vs autres secteurs
7. Résultat 4 — Climat : évolution des températures (10 villes)
8. Résultat 5 — Carte des zones protégées & score de vulnérabilité
9. Recommandations concrètes et priorisation
10. Aperçu du dashboard + prochaines étapes

---

## 6. Checklist qualité avant soumission

- [ ] Le dashboard se lance sans erreur sur une machine "propre"
- [ ] Aucune donnée manquante affichée sans explication (NaN visibles = mauvais point)
- [ ] Chaque graphique a un titre, des axes légendés, une source
- [ ] Les recommandations sont chiffrées et actionnables (pas génériques)
- [ ] Le fichier ZIP < 20 Mo, le PPTX < 20 Mo, ≤ 10 slides
- [ ] Relecture orthographe/français sur le PPTX et les labels du dashboard
