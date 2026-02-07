# Module Backend

## Rôle
API REST FastAPI qui reçoit les questions des élèves, interroge ChromaDB, et retourne des réponses générées par GPT-4o-mini à partir uniquement des cours stockés.

## État actuel
✅ **CRÉÉ** - Backend opérationnel avec 3 fichiers :
- `main.py` : App FastAPI avec endpoints /api/chat, /api/matieres, /api/niveaux, /health
- `rag.py` : Classe RAGChain avec retrieve(), generate(), run()
- `prompts.py` : Prompts adaptés par niveau (6ème, 5ème, 4ème, 3ème, college)

⏳ **À tester** une fois l'ingestion ChromaDB terminée (actuellement 90%)

## Architecture
```
backend/
├── __init__.py
├── main.py          # ✅ App FastAPI, routes, CORS, validation Pydantic
├── rag.py           # ✅ Chaîne RAG LangChain (retrieval + generation)
├── prompts.py       # ✅ Prompts système adaptés par niveau (6ème-3ème)
└── ingest_chromadb.py  # Script d'ingestion (à exécuter une fois)

## Endpoints API
```
POST /api/chat
  Body: { "question": str, "niveau": str?, "matiere": str? }
  Response: { "answer": str, "sources": list[dict] }

GET /api/matieres
  Response: liste des matières disponibles

GET /api/niveaux
  Response: liste des niveaux disponibles
```

## Chaîne RAG
1. Recevoir la question + filtres (niveau, matière)
2. Convertir la question en embedding via OpenAI
3. Rechercher les chunks similaires dans ChromaDB (top 5)
4. Filtrer par métadonnées si niveau/matière spécifiés
5. Construire le prompt avec les chunks comme contexte
6. Envoyer à GPT-4o-mini avec instruction stricte
7. Retourner la réponse + sources utilisées

## Contraintes critiques
- Le prompt système DOIT interdire au LLM d'utiliser ses connaissances propres
- Si aucun chunk pertinent (score de similarité trop bas), retourner un message de refus
- Seuil de similarité configurable via `.env`
- Le frontend est servi comme fichiers statiques depuis FastAPI

## Conventions
- Variables d'environnement via `python-dotenv` (fichier `.env`)
- Modèles Pydantic pour la validation des requêtes/réponses
- CORS activé pour le développement local
- Logging structuré, pas de `print`
