# Palstream - Analyse des Pals de Palworld

Analyse exploratoire de Palworld avec Paldex visuel, stats de combat et production de campement.

## Lancement

```bash
# 1. Installer les dependances (une seule fois)
pip install -r app/requirements.txt

# 2. Lancer depuis le dossier pals-analysis/
streamlit run app/app.py
```

L application s ouvre sur http://localhost:8501

## Structure

```
pals-analysis/
├── README.md
├── data/                    <- 6 CSV + description
├── sql/                     <- Scripts MariaDB
├── app/
│   ├── app.py               <- Application Streamlit
│   ├── import_data.py       <- Import MariaDB (optionnel, mdp: r3dgh0st!)
│   ├── requirements.txt
│   └── assets/
│       ├── pals/            <- 138 icones PNG des Pals
│       └── elements/        <- 9 icones PNG des elements
└── notebooks/
    └── analyse_pals.ipynb
```

## Pages

| Page | Description |
|---|---|
| Accueil | KPIs, Top 5 avec images, distributions |
| Paldex | Grille visuelle de tous les Pals avec filtres |
| Fiche Pal | Stats completes, barres, radar comparatif |
| Combat | Top 10, correlations, equipe equilibree |
| Campement | Ranch, competences, travail de nuit |
| Zones | Niveaux et zones d apparition |
| Boss | Tower Boss et Ordinary Boss |
| Explorateur | Filtres multi-criteres |
