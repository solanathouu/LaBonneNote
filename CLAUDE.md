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
| Backend FastAPI | ✅ PRODUCTION-READY - RAG + Auto-détection + Bibliothèque (limite 50k leçons) |
| Backend Auto-Détection | ✅ TERMINE - Détection niveau/matière par mots-clés |
| Backend Bibliothèque | ✅ TERMINE - 3 endpoints (chat/auto, lecons, detail) |
| Frontend SPA | ✅ PRODUCTION-READY - 4 vues (Chat, Bibliothèque, Favoris, Détail) |
| Frontend Chat | ✅ TERMINE - Auto-détection + choix ambiguïté + history persistant |
| Frontend Bibliothèque | ✅ TERMINE - Pagination (50/fois) + Recherche full-text + Cache intelligent |
| Frontend Favoris | ✅ TERMINE - Système complet avec localStorage + animations |
| Frontend Mode Sombre | ✅ TERMINE - Toggle dark/light avec localStorage + auto-detect OS |
| Frontend Optimisations | ✅ TERMINE - Pagination, animations optimisées, cartes cliquables |
| Tests | ⏳ Non implementes (backend teste manuellement) |
| Deployment | ⏳ Local uniquement (port 8000) |
| Git status | ✅ Clean - Dernier commit: a42a184 (search + pagination + favorites) |

## Last Session Summary (2026-02-07 - Session 4)
**RECHERCHE + PAGINATION + FAVORIS - Bibliothèque complète**

**Phase 1 : Suppression limite backend** :
1. ✅ `backend/rag.py` - Limite passée de 100 à 50 000 leçons
2. ✅ `backend/main.py` - Limite endpoint passée de 100 à 50 000
3. ✅ Toutes les leçons accessibles dans la bibliothèque

**Phase 2 : Pagination intelligente** :
1. ✅ Chargement progressif : 50 leçons à la fois
2. ✅ Bouton "Charger 50 leçons de plus" avec compteur
3. ✅ Animations optimisées (délai max 1.5s au lieu de 5s)
4. ✅ Reset pagination lors changement de matière
5. ✅ Performance : 13k+ leçons gérées sans ralentissement

**Phase 3 : Recherche full-text** :
1. ✅ Barre de recherche en temps réel dans bibliothèque
2. ✅ Recherche insensible aux accents (`normalizeString()`)
3. ✅ Recherche insensible à la casse
4. ✅ Filtre par titre ET résumé/contenu
5. ✅ Bouton "✕" pour effacer la recherche
6. ✅ Message "Aucun résultat" avec suggestions
7. ✅ Compteur de résultats dynamique

**Phase 4 : Système de favoris** :
1. ✅ Bouton étoile ☆/⭐ sur chaque carte de leçon
2. ✅ Toggle favori avec animation (rotation + pulse)
3. ✅ localStorage pour persistence (survit au refresh)
4. ✅ Nouvelle vue "⭐ Favoris" dans navigation
5. ✅ Tri par date d'ajout (plus récents en premier)
6. ✅ État vide stylisé avec icône animée et CTA
7. ✅ Bordure colorée sur cartes favorites
8. ✅ Fonctions: `loadFavorites()`, `saveFavorites()`, `isFavorite()`, `toggleFavorite()`

**Fichiers modifiés** :
- `backend/rag.py` : +2 lignes (limite 50k)
- `backend/main.py` : +1 ligne (limite 50k)
- `frontend/app.js` : +250 lignes (recherche, pagination, favoris)
- `frontend/index.html` : +3 lignes (bouton Favoris nav)
- `frontend/style.css` : +120 lignes (styles recherche, favoris, animations)

**Commits créés** :
- `a42a184` - Add search, pagination, and favorites features
- `92c8376` - Merge feature/dark-mode into main
- `2a2d4f5` - Fix library animations and improve lesson content formatting

**Résultat** : Bibliothèque optimisée, searchable, avec favoris persistants

## Next Immediate Action

**Option 1 : Continuer les améliorations UX**

Prochaines features recommandées (voir `docs/PLAN_AMELIORATIONS.md`) :
1. 🧪 **Tests automatisés** (14h) - pytest backend + playwright frontend
2. 🎓 **Classification par niveau** (8h) - Script déjà prêt (`backend/classify_levels.py`)
3. 📊 **Statistiques utilisateur** (4h) - Tracker recherches, favoris, temps
4. 🔔 **Notifications** (3h) - Toast messages pour actions (favori ajouté, etc.)

**Option 2 : Déploiement**

Déployer sur Render/Railway :
1. Créer `requirements.txt` complet
2. Créer `Procfile` pour backend
3. Configurer variables d'environnement
4. Setup ChromaDB persistence cloud

**Option 3 : Features avancées**

1. 📝 **Export PDF** - Générer PDF des leçons
2. 🎤 **Voice input** - Dictée vocale pour questions
3. 🌐 **i18n** - Support multi-langues
4. 📱 **PWA** - Application installable

**Commandes pour lancer l'app** :

```bash
cd C:\Users\skwar\Desktop\RAG

# Lancer le backend (dans un terminal)
cd backend
uvicorn main:app --reload --port 8000

# Ouvrir dans le navigateur
# http://localhost:8000

# Tester les nouvelles features :
# 1. Cliquer sur "📚 Bibliothèque" puis une matière (ex: Histoire-Géo)
# 2. Utiliser la barre de recherche 🔍 (ex: "révolution")
# 3. Cliquer sur "Charger 50 leçons de plus" pour pagination
# 4. Cliquer sur ⭐ pour ajouter aux favoris
# 5. Cliquer sur "⭐ Favoris" dans la navigation
# 6. Tester le mode sombre 🌙
```

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
│   ├── main.py         # Endpoints API (chat, lecons, detail)
│   ├── rag.py          # Chaîne RAG (retrieve + generate)
│   ├── prompts.py      # Prompts adaptés par niveau
│   ├── detection.py    # Auto-détection niveau/matière
│   └── ingest_chromadb.py  # Script ingestion
├── frontend/       # Interface SPA HTML/CSS/JS
│   ├── index.html      # Structure + navigation
│   ├── app.js          # Router SPA + 4 vues + favoris
│   └── style.css       # Design system "Cahier Numérique"
├── data/
│   ├── raw/vikidia/    # Articles bruts par matiere (JSON)
│   └── processed/      # Chunks prets pour embedding (JSON)
├── chromadb/       # Base vectorielle ChromaDB (persistee)
├── docs/           # Documentation et plans
├── .env            # Cles API (NE PAS COMMITTER)
└── requirements.txt
```

## Sources de donnees
- **Vikidia** : articles encyclopediques adaptes aux collegiens (API MediaWiki) - ✅ UTILISE (43 857 chunks)
- **Wikiversite** : cours structures niveau college (API MediaWiki) - ❌ ABANDONNE (99.6% pages vides)
- **Academie en Ligne (CNED)** : cours par niveau - ❌ ABANDONNE (site restructure, URLs obsoletes)

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

## Features principales

### 💬 Chat intelligent
- Auto-détection niveau et matière par mots-clés
- Gestion des questions ambiguës (choix manuel)
- Historique de conversation persistant
- Badge de détection visible
- Prompts adaptés par niveau (6ème, 5ème, 4ème, 3ème)

### 📚 Bibliothèque
- 43 870 leçons Vikidia organisées par matière
- **Pagination intelligente** : 50 leçons/page, chargement progressif
- **Recherche full-text** : temps réel, insensible accents/casse
- Cartes de leçons cliquables (titre, résumé, métadonnées)
- Navigation : Bibliothèque → Matière → Leçon → Détail
- Cache intelligent (pas de re-fetch)

### ⭐ Favoris
- Bouton étoile sur chaque leçon
- Stockage localStorage (persistant)
- Vue dédiée "Mes Favoris"
- Tri par date d'ajout
- Animations fluides (pulse, rotation)

### 🌙 Mode sombre
- Toggle light/dark avec bouton 🌙/☀️
- 30+ variables CSS pour cohérence
- Auto-détection préférence OS
- Persistance localStorage
- Transitions fluides

### 🎨 Design "Cahier Numérique"
- Background papier avec grille 8x8px
- Typography: Lexend (headings) + DM Sans (body)
- 8 couleurs par matière
- Animations CSS fluides
- Responsive mobile-first

## Contraintes critiques
1. **Reponse uniquement depuis la base** : le LLM ne doit JAMAIS utiliser ses connaissances propres
2. **Filtrage niveau/matiere** : chaque chunk est tague avec metadonnees
3. **Refus hors-perimetre** : si aucun chunk pertinent trouve, le bot dit qu'il ne sait pas
4. **Pas de secrets dans le code** : utiliser `.env` pour les cles API

## Commandes utiles
```bash
# Installer les dependances
pip install -r requirements.txt

# Lancer le backend
cd backend
uvicorn main:app --reload --port 8000

# Ouvrir l'app
# http://localhost:8000

# Lancer le scraping (toutes matieres)
python -m scraper.pipeline

# Lancer le scraping (une matiere)
python -m scraper.pipeline --matiere mathematiques

# Ingestion ChromaDB
cd backend
python ingest_chromadb.py
```
