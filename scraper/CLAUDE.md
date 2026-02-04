# Module Scraper

## Rôle
Collecte, nettoyage et chunking des contenus scolaires depuis Vikidia, Wikiversité et Éduscol.

## Architecture
```
scraper/
├── __init__.py
├── vikidia.py       # Scraper Vikidia via API MediaWiki
├── wikiversite.py   # Scraper Wikiversité via API MediaWiki
├── eduscol.py       # Scraper Éduscol via requests + BeautifulSoup
├── cleaner.py       # Nettoyage HTML → texte propre
├── chunker.py       # Découpage en chunks (~500 tokens)
├── metadata.py      # Gestion des métadonnées (matière, niveau, source)
└── pipeline.py      # Orchestration : scrape → clean → chunk → embed → store
```

## Sources et APIs

### Vikidia (fr.vikidia.org)
- API MediaWiki : `https://fr.vikidia.org/w/api.php`
- Action `query` avec `prop=extracts` pour le contenu texte
- Navigation par catégories pour cibler les matières
- Contenu adapté aux 8-13 ans

### Wikiversité (fr.wikiversity.org)
- API MediaWiki : `https://fr.wikiversity.org/w/api.php`
- Cours structurés en leçons avec niveaux
- Navigation par catégories et départements

### Éduscol (eduscol.education.fr)
- Pas d'API publique → scraping HTTP avec BeautifulSoup
- Cibler les pages programmes cycle 3 et cycle 4
- Respecter les délais entre requêtes (1-2s)

## Format de sortie (chunk)
Chaque chunk produit doit contenir :
```python
{
    "text": "contenu du chunk",
    "metadata": {
        "source": "vikidia|wikiversite|eduscol",
        "matiere": "mathematiques|francais|histoire_geo",
        "niveau": "6eme|5eme|4eme|3eme|college",
        "titre": "titre de la page source",
        "url": "URL originale"
    }
}
```

## Conventions
- Un fichier par source (séparation des responsabilités)
- `pipeline.py` orchestre tout : ne pas appeler les scrapers directement
- Sauvegarder les données brutes dans `data/raw/` avant traitement
- Sauvegarder les chunks traités dans `data/processed/`
- Logs avec `logging` (pas de `print`)
- Respecter un délai entre les requêtes HTTP pour ne pas surcharger les serveurs
- Gestion d'erreurs : ne pas crasher si une page échoue, logger et continuer
