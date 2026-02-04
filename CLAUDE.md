# Chatbot Assistant Scolaire - Collège Français

## Objectif
Chatbot RAG qui répond **uniquement** à partir de cours et programmes scolaires du collège français (6ème-3ème). Le bot refuse de répondre si l'information n'existe pas dans la base de données.

## Stack technique
- **Backend** : Python 3.11+ / FastAPI / LangChain
- **Vector DB** : ChromaDB (persistance locale dans `chromadb/`)
- **LLM** : OpenAI GPT-4o-mini
- **Embeddings** : OpenAI text-embedding-3-small
- **Frontend** : HTML / CSS / JS vanilla
- **Scraping** : requests + BeautifulSoup + API MediaWiki

## Structure du projet
```
RAG/
├── scraper/        # Collecte et traitement des données scolaires
├── backend/        # API FastAPI + chaîne RAG LangChain
├── frontend/       # Interface chat HTML/CSS/JS
├── data/           # Données brutes et traitées
├── chromadb/       # Base vectorielle ChromaDB (persistée)
├── docs/           # Documentation et plans
├── .env            # Clés API (NE PAS COMMITTER)
└── requirements.txt
```

## Sources de données
- **Vikidia** : articles encyclopédiques adaptés aux collégiens (API MediaWiki)
- **Wikiversité** : cours structurés niveau collège (API MediaWiki)
- **Éduscol** : programmes officiels Éducation Nationale (scraping HTTP)

## Matières pilotes
- Mathématiques
- Français
- Histoire-Géographie

## Niveaux
- 6ème (cycle 3)
- 5ème, 4ème, 3ème (cycle 4)

## Contraintes critiques
1. **Réponse uniquement depuis la base** : le LLM ne doit JAMAIS utiliser ses connaissances propres
2. **Filtrage niveau/matière** : chaque chunk est tagué avec métadonnées
3. **Refus hors-périmètre** : si aucun chunk pertinent trouvé, le bot dit qu'il ne sait pas
4. **Pas de secrets dans le code** : utiliser `.env` pour les clés API

## Commandes utiles
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le scraping
python -m scraper.pipeline

# Lancer le backend
uvicorn backend.main:app --reload

# Le frontend se sert depuis le backend (static files)
```
