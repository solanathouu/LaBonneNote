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
| Backend FastAPI | ✅ PRODUCTION-READY - RAG + Auto-détection + Bibliothèque |
| Backend Auto-Détection | ✅ TERMINE - Détection niveau/matière par mots-clés |
| Backend Bibliothèque | ✅ TERMINE - 3 nouveaux endpoints (chat/auto, lecons, detail) |
| Frontend SPA | ✅ PRODUCTION-READY - 3 vues (Chat, Bibliothèque, Détail) |
| Frontend Chat | ✅ TERMINE - Auto-détection + choix ambiguïté + history persistant |
| Frontend Bibliothèque | ✅ TERMINE - Liste leçons + navigation + scroll fix |
| Tests | ⏳ Non implementes (backend teste manuellement) |
| Deployment | ⏳ Local uniquement (port 8000) |
| Git status | 🔄 Nombreux fichiers modifiés/créés non committés |

## Last Session Summary (2026-02-07 - Session 2)
**TRANSFORMATION MAJEURE : Chatbot simple → Plateforme d'apprentissage hybride (SPA)**

**Backend (Phase 1) - Nouvelles fonctionnalités :**
1. ✅ `backend/detection.py` - Auto-détection niveau + matière par mots-clés (~180 lignes)
2. ✅ Extension `backend/rag.py` - Méthodes `get_all_lessons()` et `get_lesson_content()` (~150 lignes)
3. ✅ 3 nouveaux endpoints dans `backend/main.py` :
   - `POST /api/chat/auto` - Chat avec auto-détection (retourne niveau/matière détectés + ambiguïté)
   - `GET /api/lecons/{matiere}` - Liste des leçons d'une matière (avec filtrage niveau)
   - `GET /api/lecons/{matiere}/detail?titre=...` - Contenu complet d'une leçon

**Frontend (Phase 2) - Refonte complète en SPA :**
1. ✅ Nouveau `frontend/index.html` (85 lignes) - Navigation sticky + structure SPA
2. ✅ Refonte complète `frontend/app.js` (784 lignes) - Router SPA + 3 vues dynamiques
3. ✅ Extension `frontend/style.css` (+400 lignes, total ~1300) - Design system étendu

**3 Vues Implémentées :**
- **Vue Chat** : Auto-détection niveau/matière, badge visible, choix si ambiguïté, history persistant
- **Vue Bibliothèque** : Grille de leçons cliquables, skeleton loading, 2 boutons par leçon
- **Vue Détail Leçon** : Breadcrumbs, résumé + contenu complet, bouton "Poser une question"

**Bugs Corrigés :**
1. ✅ Scroll bloqué dans bibliothèque (ajout `.app-main` avec `overflow-y: auto`)
2. ✅ Erreur 404 sur leçons (fix syntaxe filtres ChromaDB avec `$and` + `$eq`)
3. ✅ Caractères spéciaux dans URLs (passage query parameter au lieu de path)

**Design "Cahier Numérique" maintenu :**
- Background papier blanc (#fefdfb) avec grille 8x8px + texture SVG
- Typography: Lexend (headings) + DM Sans (body)
- 8 couleurs par matière (bleu, violet, orange, vert, rose, indigo, cyan, rouge)
- Animations fluides entre vues (fadeIn, slideIn, shimmer skeletons)
- Responsive mobile-first, accessible

## Next Immediate Action

**ÉTAPE 1 : Commiter tous les changements SPA**

```bash
cd C:\Users\skwar\Desktop\RAG

# Ajouter tous les fichiers créés
git add backend/detection.py
git add CHECKPOINT.md README.md
git add docs/DEMO.md docs/FRONTEND_SUMMARY.md docs/wikiversite_scraper_guide.md

# Ajouter fichiers modifiés
git add backend/main.py backend/rag.py
git add frontend/index.html frontend/app.js frontend/style.css

# NE PAS AJOUTER (fichiers temporaires/config locale)
# .claude/, nul, *.log, test_*.py, data/raw/academie_en_ligne/, data/raw/wikiversite/

# Commit
git commit -m "Transform app to hybrid learning platform (SPA)

Backend (Phase 1):
- Add backend/detection.py: Auto-detect level + subject from question
- Extend backend/rag.py: Methods get_all_lessons() and get_lesson_content()
- Add 3 new endpoints: POST /api/chat/auto, GET /api/lecons/{matiere}, GET /api/lecons/{matiere}/detail

Frontend (Phase 2):
- Complete SPA refactor: Router + 3 dynamic views (Chat, Library, Lesson Detail)
- Vue Chat: Auto-detection with visible badge, ambiguity choice, persistent history
- Vue Library: Clickable lessons grid, skeleton loading, filters
- Vue Detail: Breadcrumbs, summary + full content, ask question button

Fixes:
- Fix scroll blocked in library (add .app-main overflow)
- Fix 404 on lessons (fix ChromaDB filters syntax with \$and + \$eq)
- Fix special chars in URLs (use query param instead of path)

Frontend extensions:
- frontend/index.html: 85 lines (sticky nav + SPA structure)
- frontend/app.js: 784 lines (complete rewrite)
- frontend/style.css: +400 lines (extended design system)

Status: App fully functional, 43,870 Vikidia lessons browsable
Next: Test all features then push to GitHub

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push vers GitHub
git push origin main
```

**ÉTAPE 2 : Tester toutes les fonctionnalités**

1. Lancer le backend :
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. Ouvrir http://localhost:8000

3. **Tester Vue Chat :**
   - Question : "C'est quoi le théorème de Pythagore ?"
   - Vérifier badge "🤖 Détecté : 5ème • Mathématiques"
   - Question ambiguë : "Parle-moi de la révolution" → Vérifier boutons de choix

4. **Tester Vue Bibliothèque :**
   - Cliquer sur "📚 Bibliothèque"
   - Cliquer sur "📐 Maths"
   - Vérifier liste des leçons (doit afficher ~543 leçons)
   - Vérifier scroll fonctionne

5. **Tester Vue Détail :**
   - Cliquer "📖 Lire" sur une leçon (ex: "Théorème de Pythagore")
   - Vérifier breadcrumbs cliquables
   - Cliquer "📖 Lire le contenu complet"
   - Cliquer "💬 Poser une question" → Retour au chat avec question pré-remplie

6. **Tester Navigation :**
   - Vérifier historique chat conservé quand on change de vue
   - Vérifier bouton retour navigateur fonctionne
   - Vérifier thème couleur change selon matière sélectionnée

**Prochaines étapes possibles :**
- Ajouter tests automatisés (pytest backend, playwright frontend)
- Déployer sur Render/Railway (nécessite: requirements.txt complet, Procfile)
- Ajouter fonctionnalités : export PDF, mode sombre, voice input
- Améliorer détection auto (ML model au lieu de mots-clés)

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
