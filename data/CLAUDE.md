# Répertoire Data

## Rôle
Stockage des données scrapées brutes et des chunks traités.

## Structure
```
data/
├── raw/             # Données brutes telles que scrapées (JSON)
│   └── vikidia/     # ✅ Articles Vikidia par matière (24 321 articles)
└── processed/       # ✅ Chunks prêts pour l'embedding (43 857 chunks JSON)
    ├── mathematiques_chunks.json
    ├── francais_chunks.json
    ├── histoire_geo_chunks.json
    ├── svt_chunks.json
    ├── physique_chimie_chunks.json
    ├── technologie_chunks.json
    ├── anglais_chunks.json
    └── espagnol_chunks.json
```

## Formats
- **raw/** : fichiers JSON avec le contenu brut + URL source + date de scraping
- **processed/** : fichiers JSON avec chunks découpés + métadonnées complètes

## Conventions
- Ne pas committer les données dans git (ajouté dans `.gitignore`)
- Les données brutes servent de cache : si déjà scrapé, ne pas re-scraper
- Noms de fichiers : `{source}_{matiere}_{date}.json`
