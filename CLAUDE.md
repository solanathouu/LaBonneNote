# Chatbot Assistant Scolaire - College Francais

## Objectif
Chatbot RAG qui repond **uniquement** a partir de cours et programmes scolaires du college francais (6eme-3eme). Le bot refuse de repondre si l'information n'existe pas dans la base de donnees.

## Current Project State
| Aspect | Status |
|--------|--------|
| Scraper Vikidia | ✅ TERMINE - 8 matieres scrapees (24 321 articles, 43 857 chunks) |
| Scraper Wikiversite | ❌ ABANDONNE - 0.4% pages exploitables (507 pages testees, 2 lessons) |
| Scraper Academie en Ligne | ❌ ABANDONNE - URLs obsoletes (8 pages irrelevantes) |
| ChromaDB ingestion | ✅ TERMINE - 43 870 documents ingeres dans 'cours_college' |
| Backend FastAPI | ✅ CREE - 3 fichiers (main.py, rag.py, prompts.py) |
| Frontend | ⏳ Pas encore implemente (structure prete) |
| Tests | ⏳ Aucun |

## Next Immediate Action
1. ✅ ~~Verifier les donnees scrapees dans `data/raw/vikidia/` et `data/processed/`~~
2. ✅ ~~Finaliser l'ingestion ChromaDB~~
3. ✅ ~~Implementer le backend FastAPI + chaine RAG LangChain~~
4. ⏳ **NEXT: Tester le backend RAG** (`uvicorn backend.main:app --reload`)
5. ⏳ Creer le frontend HTML/CSS/JS

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
- **Vikidia** : articles encyclopediques adaptes aux collegiens (API MediaWiki) - ✅ UTILISE (43 857 chunks)
- **Wikiversite** : cours structures niveau college (API MediaWiki) - ❌ ABANDONNE (99.6% pages vides)
- **Academie en Ligne (CNED)** : cours par niveau - ❌ ABANDONNE (site restructure, URLs obsoletes)

## Strategie d'adaptation par niveau
Comme les sources alternatives (Wikiversite, Academie en Ligne) n'ont pas de contenu exploitable, l'adaptation par niveau se fait via **prompts GPT personnalises** :
- Tous les chunks Vikidia sont tagges `niveau: "college"` (generique)
- Le backend utilise des prompts adaptes selon le niveau de l'eleve (6eme, 5eme, 4eme, 3eme)
- GPT-4o-mini adapte le langage et les explications au niveau specifie dans la requete

## Matieres
| Matiere | Source Vikidia | Articles | Chunks |
|---------|---------------|----------|--------|
| Histoire-Geo | Categories:Histoire,Geographie | 13 112 | 25 474 |
| SVT | Categories:Biologie,Geologie | 5 454 | 8 481 |
| Francais | Categories:Francais,Grammaire,Litterature | 3 040 | 4 835 |
| Physique-Chimie | Categories:Physique,Chimie | 1 439 | 2 751 |
| Technologie | Categories:Technologie | 724 | 1 349 |
| Mathematiques | Categories:Mathematiques | 543 | 967 |
| Anglais | Categories:Anglais | 6 | - |
| Espagnol | Categories:Espagnol | 3 | - |
| **TOTAL** | | **24 321** | **43 857** |

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
