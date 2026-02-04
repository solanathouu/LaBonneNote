# Répertoire Data

## Rôle
Stockage des données scrapées brutes et des chunks traités.

## Structure
```
data/
├── raw/             # Données brutes telles que scrapées (JSON)
│   ├── vikidia/     # Articles Vikidia par matière
│   ├── wikiversite/ # Cours Wikiversité par matière
│   └── eduscol/     # Pages Éduscol par cycle
└── processed/       # Chunks prêts pour l'embedding (JSON)
    ├── mathematiques/
    ├── francais/
    └── histoire_geo/
```

## Formats
- **raw/** : fichiers JSON avec le contenu brut + URL source + date de scraping
- **processed/** : fichiers JSON avec chunks découpés + métadonnées complètes

## Conventions
- Ne pas committer les données dans git (ajouté dans `.gitignore`)
- Les données brutes servent de cache : si déjà scrapé, ne pas re-scraper
- Noms de fichiers : `{source}_{matiere}_{date}.json`
