# Chatbot Assistant Scolaire - College Francais

## Objectif
Chatbot RAG qui repond **uniquement** a partir de cours et programmes scolaires du college francais (6eme-3eme). Le bot refuse de repondre si l'information n'existe pas dans la base de donnees.

## Current Project State
| Aspect | Status |
|--------|--------|
| Scraper Vikidia | OK (maths/anglais/espagnol termines, francais/histoire-geo/svt/physique-chimie/technologie en cours) |
| Scraper Wikiversite | Pas encore implemente |
| Scraper Eduscol | Pas encore implemente |
| Backend FastAPI | Pas encore implemente (structure prete) |
| Frontend | Pas encore implemente (structure prete) |
| ChromaDB ingestion | Pas encore implemente |
| Tests | Aucun |

## Next Immediate Action
1. Attendre la fin des scrapers en cours (francais, histoire-geo, svt, physique-chimie, technologie)
2. Verifier les donnees scrapees dans `data/raw/vikidia/` et `data/processed/`
3. Implementer le script d'ingestion ChromaDB (embeddings OpenAI -> ChromaDB)
4. Implementer le backend FastAPI + chaine RAG LangChain

## Stack technique
- **Backend** : Python 3.11+ / FastAPI / LangChain
- **Vector DB** : ChromaDB (persistance locale dans `chromadb/`)
- **LLM** : OpenAI GPT-4o-mini
- **Embeddings** : OpenAI text-embedding-3-small
- **Frontend** : HTML / CSS / JS vanilla
- **Scraping** : cloudscraper + BeautifulSoup + API MediaWiki (Cloudflare bypass)

## Structure du projet
```
RAG/
├── scraper/        # Collecte et traitement des donnees scolaires
│   ├── vikidia.py      # Scraper Vikidia (API MediaWiki + cloudscraper)
│   ├── cleaner.py      # Nettoyage texte (LaTeX, HTML, sections inutiles)
│   ├── chunker.py      # Decoupage en chunks ~500 tokens avec overlap
│   ├── metadata.py     # Categories, matieres, niveaux
│   └── pipeline.py     # Orchestration scrape -> clean -> chunk -> save
├── backend/        # API FastAPI + chaine RAG LangChain
├── frontend/       # Interface chat HTML/CSS/JS
├── data/
│   ├── raw/vikidia/    # Articles bruts par matiere (JSON)
│   └── processed/      # Chunks prets pour embedding (JSON)
├── chromadb/       # Base vectorielle ChromaDB (persistee)
├── docs/plans/     # Plans d'implementation
├── .env            # Cles API (NE PAS COMMITTER)
└── requirements.txt
```

## Sources de donnees
- **Vikidia** : articles encyclopediques adaptes aux collegiens (API MediaWiki) - IMPLEMENTE
- **Wikiversite** : cours structures niveau college (API MediaWiki) - A FAIRE
- **Eduscol** : programmes officiels Education Nationale (scraping HTTP) - A FAIRE

## Matieres
| Matiere | Source Vikidia | Articles scrapes |
|---------|---------------|-----------------|
| Mathematiques | Categories:Mathematiques | 543 (967 chunks) |
| Francais | Categories:Francais,Grammaire,Litterature | En cours (~1600+) |
| Histoire-Geo | Categories:Histoire,Geographie | En cours (~1300+) |
| SVT | Categories:Biologie,Geologie | En cours |
| Physique-Chimie | Categories:Physique,Chimie | En cours |
| Technologie | Categories:Technologie | En cours |
| Anglais | Categories:Anglais | 6 (peu de contenu sur Vikidia) |
| Espagnol | Categories:Espagnol | 3 (peu de contenu sur Vikidia) |

## Niveaux
- 6eme (cycle 3)
- 5eme, 4eme, 3eme (cycle 4)

## Contraintes critiques
1. **Reponse uniquement depuis la base** : le LLM ne doit JAMAIS utiliser ses connaissances propres
2. **Filtrage niveau/matiere** : chaque chunk est tague avec metadonnees
3. **Refus hors-perimetre** : si aucun chunk pertinent trouve, le bot dit qu'il ne sait pas
4. **Pas de secrets dans le code** : utiliser `.env` pour les cles API

## Commandes utiles
```bash
# Installer les dependances
pip install -r requirements.txt

# Lancer le scraping (toutes matieres)
python -m scraper.pipeline

# Lancer le scraping (une matiere)
python -m scraper.pipeline --matiere mathematiques

# Lancer le backend
uvicorn backend.main:app --reload
```

## Notes techniques
- Vikidia est protege par Cloudflare -> utiliser `cloudscraper` (pas `requests` direct)
- Delai de 1s entre chaque requete API pour respecter le serveur
- Crawl recursif des sous-categories (profondeur max 3)
- Deduplication des articles vus dans plusieurs categories
- Logs avec indicateur [PROGRESSION] toutes les 10 secondes
