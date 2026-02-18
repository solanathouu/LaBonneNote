# LaBonneNote - Assistant Scolaire College Francais

## Objectif
**LaBonneNote** est un chatbot RAG qui repond **uniquement** a partir de cours et programmes scolaires du college francais (6eme-3eme). Le bot refuse de repondre si l'information n'existe pas dans la base de donnees.

## Current Project State
| Aspect | Status |
|--------|--------|
| Scraper Vikidia | ✅ TERMINE - 8 matieres scrapees (24 321 articles, 43 857 chunks) |
| Scraper Wikiversite | ❌ ABANDONNE - 0.4% pages exploitables (507 pages testees, 2 lessons) |
| Scraper Academie en Ligne | ❌ ABANDONNE - URLs obsoletes (8 pages irrelevantes) |
| ChromaDB ingestion | ✅ TERMINE - 2 collections ('cours_college' + 'mes_cours' pour PDFs) |
| Backend FastAPI | ✅ PRODUCTION-READY - RAG multi-source + PDF service + 11 endpoints |
| Backend RAG | ✅ TERMINE - Multi-source (Vikidia/Mes Cours/Les deux) + détection questions générales |
| Backend PDF Service | ✅ TERMINE - Upload, extraction PyPDFLoader, chunking, ChromaDB |
| Frontend SPA | ✅ PRODUCTION-READY - 5 vues (Chat, Bibliothèque, Favoris, Mes Cours, Détail) |
| Frontend Chat | ✅ TERMINE - Sélecteur source + auto-détection + réponses sans sources (salut, merci) |
| Frontend Bibliothèque | ✅ TERMINE - Pagination + Recherche + Cache + animations désactivées |
| Frontend Favoris | ✅ TERMINE - Système complet avec localStorage |
| Frontend Mes Cours | ✅ TERMINE - Upload drag&drop + liste PDFs + suppression + progress bar |
| Frontend Mode Sombre | ✅ TERMINE - Toggle dark/light avec localStorage |
| Frontend Animations | ✅ SUPPRIMEES - Toutes animations désactivées (bibliothèque, chat, favoris) |
| Frontend Mascotte | ✅ TERMINE - Système complet avec 15/21 images (8 matières + contextes) |
| Frontend Mascotte par Matière | ✅ TERMINE - Bibliothèque + Détails leçons avec mascottes dynamiques |
| Backend Quiz Service | ✅ TERMINE - Génération automatique QCM avec LLM + validation + scoring |
| Backend Quiz Endpoints | ✅ TERMINE - 2 endpoints (/generate, /validate) + 6 modèles Pydantic |
| Frontend Quiz | ✅ TERMINE - 3 vues (Setup, Active, Results) + navigation + persistance |
| Frontend Quiz Integration | ✅ TERMINE - Boutons quiz bibliothèque + détail leçon + mascottes contextuelles |
| Branding LaBonneNote | ✅ TERMINE - Nom, titre, header, welcome message, meta |
| Recherche par pertinence | ✅ TERMINE - Tri titre d'abord, puis résumé |
| Déduplication sources | ✅ TERMINE - 1 lien par article dans le chat |
| Boutons leçons avec labels | ✅ TERMINE - Quiz/Lire/Discuter au lieu d'emojis seuls |
| Presentation HTML | ✅ TERMINE - 15 slides navigables, theme Cahier Numerique, mascottes |
| Guide Technique Oral | ✅ TERMINE - Doc complet pour expliquer chaque fonction Python/LangChain |
| Tests | ⏳ Non implementes (backend teste manuellement) |
| Deployment | ⏳ Local uniquement (port 8000) |
| Git status | ✅ A jour |

## Last Session Summary (2026-02-18 - Session 14)
**GUIDE TECHNIQUE POUR ORAL**

**Fichier cree** : `GUIDE_TECHNIQUE_ORAL.md` (racine du projet)

**Contenu** : Document complet de preparation a la soutenance technique :
- 11 sections detaillees couvrant chaque fichier Python du projet
- Explication fonction par fonction avec schemas ASCII du pipeline
- Glossaire des concepts cles (embedding, RAG, token, temperature, cosine similarity, ChromaDB, LangChain)
- 13 questions/reponses probables du jury avec arguments

**Sections** :
1. Vue d'ensemble pipeline RAG (Phase 1 preparation + Phase 2 utilisation)
2. Scraping Vikidia (API MediaWiki, cloudscraper, recursion categories)
3. Nettoyage (4 etapes regex : sections, LaTeX, wiki, espaces)
4. Chunking (500 tokens, overlap 50, decoupe paragraphes/phrases)
5. Ingestion ChromaDB (embeddings 1536 dim, batch 100)
6. Chaine RAG - retrieve() + generate() (le coeur du projet)
7. Prompts (contrainte stricte + adaptation niveau)
8. Detection automatique (mots-cles matiere, heuristique niveau)
9. Service PDF (PyPDFLoader, RecursiveCharacterTextSplitter)
10. Service Quiz (asyncio.gather, generation JSON parallele)
11. API FastAPI (11 endpoints, Pydantic, CORS)

---

## Previous Session Summary (2026-02-17 - Session 13)
**PRESENTATION HTML POUR ORAL**

**Fichier cree** : `presentation.html` (racine du projet, auto-contenu)

**15 slides** :
1. Titre LaBonneNote + mascotte accueil
2. Le probleme - 4 pain points
3. La solution - 3 piliers (RAG, Adaptatif, Quiz)
4. Architecture RAG - Pipeline visuel 2 lignes
5. Les donnees - 43857 chunks, 8 matieres
6. Stack technique - 9 technos
7. Features Chat - Liste + mascotte thinking
8. Features Bibliotheque & Quiz
9. Features Mes Cours & Plus - 7 cartes
10. DEMO LIVE - Fond sombre + pulse
11. Defis techniques - 4 defis
12. Le marche - Chiffres EdTech
13. Vision future - Roadmap 7 etapes
14. Chiffres cles - 6 stats
15. Merci + Questions

**Navigation** : Fleches clavier + Espace + Click + Swipe tactile + Escape + barre progression

**Bug fix** : `classList.add('')` crashait la navigation arriere (DOMException)

**Design** : Theme Cahier Numerique (fond papier, grille, Lexend + DM Sans, couleurs matieres, mascottes)

---

## Previous Session Summary (2026-02-11 - Session 12)
**BRANDING LABONNENOTE + AMÉLIORATIONS UX**

**Part 1 : Labels boutons leçons (15min)** :
1. ✅ Ajout texte aux boutons d'action des cartes leçons
   - 📝 → "📝 Quiz"
   - 📖 → "📖 Lire"
   - 💬 → "💬 Discuter"
2. ✅ CSS `.btn-quiz` harmonisé avec `.btn-read` et `.btn-ask` (flex:1, font-weight:600)

**Part 2 : Recherche triée par pertinence (20min)** :
1. ✅ Système de scoring dans `renderLessonsWithPagination()`
   - Score 1000 : titre commence par le terme recherché
   - Score 100 : titre contient le terme
   - Score 1 : résumé contient le terme
2. ✅ Tri décroissant par score (plus pertinent en premier)

**Part 3 : Déduplication des sources chat (10min)** :
1. ✅ `seen_titles = set()` dans `backend/rag.py`
2. ✅ Skip des chunks dont le titre a déjà été ajouté aux sources
3. ✅ Résultat : 1 lien par article au lieu de 5x le même

**Part 4 : Branding LaBonneNote (15min)** :
1. ✅ `<title>` HTML : "LaBonneNote - Assistant Scolaire"
2. ✅ Header H1 : "LaBonneNote"
3. ✅ Sous-titre : "Ton assistant scolaire intelligent"
4. ✅ Welcome message : "Bienvenue sur LaBonneNote !"
5. ✅ Introduction Marianne : "Je suis Marianne, ton assistante..."
6. ✅ Console logs, alt images, commentaires JS
7. ✅ CLAUDE.md titre et objectif

**Fichiers modifiés** :
- `frontend/index.html` : titre + header + alt
- `frontend/app.js` : welcome + recherche pertinence + labels boutons + logs
- `frontend/style.css` : btn-quiz harmonisé
- `backend/rag.py` : déduplication sources
- `CLAUDE.md` : branding + session summary

**Commit créé** :
- `cf560cf` - feat: rename project to LaBonneNote, improve search relevance, deduplicate sources

---

## Previous Session Summary (2026-02-11 - Session 11)
**SYSTÈME DE QUIZ AUTOMATIQUE - IMPLÉMENTATION COMPLÈTE**

**Part 1 : Backend Quiz Service (4h)** :
1. ✅ Création `backend/quiz_service.py` (337 lignes)
   - Classe QuizService avec génération LLM asynchrone
   - `generate_quiz()` : génère 3-10 questions QCM depuis une leçon
   - `_generate_question()` : appel LLM parallèle avec parsing JSON
   - `_select_diverse_chunks()` : sélection espacée pour diversité
   - `validate_answers()` : scoring + feedback détaillé par question
   - Fallback questions si parsing échoue
2. ✅ Ajout `QUIZ_GENERATION_PROMPT` dans `backend/prompts.py`
   - Format JSON strict (4 options, 1 correcte)
   - Adaptation niveau (6ème-3ème)
   - Explications pour chaque réponse
3. ✅ Endpoints API dans `backend/main.py`
   - `POST /api/quiz/generate` - génère quiz depuis leçon
   - `POST /api/quiz/validate` - valide réponses et calcule score
   - 6 nouveaux modèles Pydantic (Request/Response/Question/Result)
   - Initialisation QuizService dans startup_event()
4. ✅ Commit: `ce16ecf` - feat: add quiz generation system backend (+468 lignes)

**Part 2 : Frontend Quiz Interface (5h)** :
1. ✅ Extension état global dans `frontend/app.js`
   - Propriétés quiz : currentQuiz, quizAnswers, quizResults, quizHistory
   - Fonctions persistence : loadQuizHistory(), saveQuizToHistory()
   - Router : buildURL() + renderView() avec 3 cas quiz
2. ✅ Vue Quiz Setup (`renderQuizSetupView()`)
   - Mascotte par matière (120px)
   - Sélecteur nb questions (3-10)
   - Loading state avec mascotte animée
   - Navigation retour leçon
3. ✅ Vue Quiz Active (`renderQuizActiveView()`)
   - Navigation questions (Précédent/Suivant)
   - Progress bar + compteur (Question X/Total)
   - Options QCM (A/B/C/D) avec sélection
   - Persistance réponses entre navigation
   - Validation avant submit (toutes réponses obligatoires)
   - Abandon avec confirmation
4. ✅ Vue Quiz Results (`renderQuizResultsView()`)
   - Score + pourcentage affiché
   - Badge performance (Excellent/Bien/Moyen/À revoir)
   - Mascotte contextuelle selon score (celebrating/base/confused)
   - Review détaillée question par question (✓/✗)
   - Explications pour chaque réponse
   - Actions : Refaire quiz + Retour leçon
5. ✅ Intégration vues existantes
   - Bouton "📝 Faire un quiz" dans détail leçon
   - Icône quiz (📝) dans cartes bibliothèque
   - Event listeners dans attachLessonCardListeners()
6. ✅ Helper : `getPerformanceMessage()` - feedback selon score
7. ✅ Commit: `4449ce2` - feat: add quiz frontend (+860 lignes)

**Part 3 : CSS Styling (2h)** :
1. ✅ Styles Quiz Setup (~80 lignes)
   - Container centré avec mascotte
   - Badges leçon/matière
   - Sélecteur questions stylisé
   - Loading message avec animation spin
2. ✅ Styles Quiz Active (~120 lignes)
   - Header avec mascotte medium (80px)
   - Progress bar animée
   - Question card avec shadow
   - Options grid avec hover effects
   - Option buttons avec states (normal/selected)
   - Letters badges (A/B/C/D)
3. ✅ Styles Quiz Results (~120 lignes)
   - Score display large (4rem)
   - Performance badges colorés
   - Result cards (correct=vert, incorrect=rouge)
   - Review détaillée avec explications
   - Actions buttons
4. ✅ Responsive mobile (<768px)
   - Mascottes réduites (120→80px)
   - Options stacked verticalement
   - Navigation full-width
5. ✅ Dark mode support
   - Result cards avec transparence
   - Couleurs texte adaptées

**Fichiers créés** :
- `backend/quiz_service.py` (337 lignes)

**Fichiers modifiés** :
- `backend/prompts.py` : +28 lignes (prompt quiz)
- `backend/main.py` : +137 lignes (endpoints + modèles)
- `frontend/app.js` : +463 lignes (3 vues + integration)
- `frontend/style.css` : +397 lignes (styles complets)

**Total changements** : +1328 lignes (468 backend + 860 frontend)

**Commits créés** :
1. `ce16ecf` - feat: add quiz generation system backend
2. `4449ce2` - feat: add quiz frontend with complete interactive interface

**Résultat** : Système de quiz automatique production-ready ! Génère des QCM depuis n'importe quelle leçon avec validation intelligente et feedback détaillé. 🎯✨

---

## Previous Session Summary (2026-02-11 - Session 10)
**MASCOTTES DYNAMIQUES PAR MATIÈRE - PHASE 2 COMPLÈTE**

**Part 1 : Système mascotte dynamique (2h)** :
1. ✅ Fonction `getMascotImage(context, matiere)` créée
   - Mapping intelligent matière → fichier PNG
   - 8 variations matières + 5 contextes + accueil + logo
2. ✅ Messages bot utilisent mascotte selon matière détectée
3. ✅ Fix débordements d'images avec overflow:hidden + max-width/height
4. ✅ Commit: `2b94eea` - feat: add dynamic mascot system

**Part 2 : Intégration bibliothèque (2h30)** :
1. ✅ Page d'accueil Bibliothèque redesignée
   - Grille de 8 cartes mascottes cliquables (au lieu de texte simple)
   - Chaque matière a sa Marianne avec bonnet coloré + accessoires
   - Hover effects avec lévitation + zoom
2. ✅ Header Bibliothèque avec mascotte
   - Mascotte 80px à côté du titre quand on navigue dans une matière
   - Remplace l'emoji par l'illustration complète
3. ✅ Détail leçon avec mascotte
   - Mascotte 90px dans le header de leçon
   - Badge matière ajouté aux métadonnées
4. ✅ CSS responsive complet
   - 3 breakpoints (desktop, tablet 768px, mobile 480px)
   - Tailles adaptatives des mascottes (100→64px)
   - Dark mode compatible
5. ✅ Commit: `de7f560` - feat: implement subject-specific mascots throughout library

**Fichiers modifiés** :
- `frontend/app.js` : +64 lignes (3 nouvelles vues avec mascottes)
- `frontend/style.css` : +235 lignes (grilles, cartes, layouts responsive)

**Total changements** : +299 lignes, -27 lignes

**Mascottes utilisées** :
- 8 variations matières : Math.png, francais.png, histoire_geo.png, svt.png, physique_chimie.png, techno.png, anglais.png, espagnol.png
- 5 contextes : mascot-base, mascot-loading, mascot-thinking, mascot-confused, mascot-reading
- 2 spéciales : accueil.png (page d'accueil biblio), mascot-logo.png (header)
- **Total : 15/21 images utilisées**

**Résultat** : Interface immersive avec Marianne qui change selon la matière ! Grille de sélection de matière visuellement riche, cohérence totale bibliothèque/chat/leçons. 🇫🇷✨

---

## Previous Session Summary (2026-02-11 - Session 9)
**INTÉGRATION MASCOTTE "MARIANNE ÉDUCATIVE"**

**Part 1 : Implémentation plan mascotte (2h)** :
1. ✅ Création dossier `frontend/assets/mascot/` avec structure
2. ✅ Ajout 60+ lignes CSS pour styles mascotte + animations
3. ✅ Modification HTML : logo header (📖 → mascot-logo.png)
4. ✅ Modification JS : 6 emplacements d'avatars remplacés
   - Welcome message → mascot-base.png
   - Bot messages → mascot-base.png
   - Loading state → mascot-loading.png (avec animation bounce)
   - Questions ambiguës → mascot-thinking.png
   - Favoris vide → mascot-confused.png
   - Upload zone → mascot-reading.png
5. ✅ Commit: `ffb4aa9` - feat: add Marianne mascot (21 images PNG, ~70MB)

**Part 2 : Suppression arrière-plans (1h)** :
1. ✅ Script `scripts/remove_bg.py` créé (utilise rembg 2.0.72)
2. ✅ Traitement 20 images PNG avec transparence alpha
3. ✅ Réduction taille : 70MB → 50MB (30% gain)
4. ✅ Backups automatiques dans `backup_with_bg/` (gitignored)
5. ✅ Commit: `f76a850` - feat: remove background transparency

**Part 3 : Ajustement UX (15min)** :
1. ✅ Feedback utilisateur : mascotte trop grande en empty states
2. ✅ Réduction taille : 120px → 80px (desktop), 100px → 70px (mobile)
3. ✅ Margin ajusté pour meilleur équilibre visuel
4. ✅ Commit: `1788930` - fix: reduce mascot size

**Fichiers créés** :
- `frontend/assets/mascot/` (21 PNG + .gitignore)
- `scripts/remove_bg.py` (63 lignes)

**Fichiers modifiés** :
- `frontend/index.html` : logo header
- `frontend/app.js` : 6 emplacements avatars
- `frontend/style.css` : +65 lignes (styles + animations mascotte)

**Assets** :
- 7 variations utilisées : base, thinking, loading, celebrating, confused, reading, logo
- 13 variations matières (bonus Phase 2) : Math, français, histoire, SVT, etc.
- Format : PNG transparents, 2.1-2.7 MB chacun
- Total : ~50 MB

**Résultat** : Interface avec identité visuelle française renforcée, mascotte "Marianne" remplace tous les emojis génériques ! 🇫🇷✨

---

## Previous Session Summary (2026-02-07 - Session 8)
**SYSTÈME COMPLET "MES COURS" + MULTI-SOURCE SEARCH + UX FIXES**

**Part 1 : Fix animations + recherche bibliothèque (1h)** :
1. ✅ Fix barre de recherche qui perdait le focus à chaque lettre
2. ✅ Suppression de TOUTES les animations (20+ animations CSS/JS)
3. ✅ Conservation des transitions hover uniquement
4. ✅ Commit: `923d310` - fix: remove all animations and fix search bar focus

**Part 2 : Détection questions générales (30min)** :
1. ✅ Fonction `is_general_question()` dans `backend/rag.py`
2. ✅ Détection salutations, politesse, questions sur le bot
3. ✅ Réponses amicales sans sources pour messages généraux
4. ✅ RAG normal avec sources pour questions thématiques

**Part 3 : Système PDF "Mes Cours" (4h)** :

**Backend** :
1. ✅ `backend/pdf_service.py` créé (195 lignes) :
   - Upload et sauvegarde PDFs dans `data/user_pdfs/`
   - Extraction avec PyPDFLoader de langchain_community
   - Chunking automatique (RecursiveCharacterTextSplitter)
   - Ajout à ChromaDB (collection "mes_cours")
2. ✅ 4 nouveaux endpoints dans `backend/main.py` :
   - `POST /api/upload-pdf` - Upload et traite un PDF
   - `GET /api/mes-cours` - Liste des PDFs importés
   - `DELETE /api/mes-cours/{filename}` - Supprime un PDF
   - `POST /api/search-mes-cours` - Recherche dans PDFs personnels
3. ✅ Modification `backend/rag.py` :
   - 2 collections ChromaDB (Vikidia + Mes Cours)
   - Paramètre `source` dans retrieve() et run()
   - Recherche dans "vikidia", "mes_cours", ou "tous"
   - Fusion et tri des résultats multi-sources

**Frontend** :
4. ✅ Nouvelle vue "📄 Mes Cours" dans `frontend/app.js` (180 lignes) :
   - Zone upload drag & drop
   - Barre de progression
   - Liste des PDFs avec infos (nom, taille, date)
   - Bouton supprimer par PDF
5. ✅ Sélecteur de source dans le chat :
   - Menu déroulant : "Cours généraux" / "Mes Cours" / "Les deux"
   - Envoi paramètre `source` à l'API
   - État persistant dans `state.selectedSource`
6. ✅ Styles CSS complets (200+ lignes) :
   - Upload zone avec hover/dragover
   - Progress bar animée
   - PDF cards avec hover effects
   - Source selector styling

**Fichiers créés/modifiés** :
- CRÉÉ: `backend/pdf_service.py` (195 lignes)
- MODIFIÉ: `backend/main.py` (+157 lignes, 11 endpoints maintenant)
- MODIFIÉ: `backend/rag.py` (+119 lignes, multi-source)
- MODIFIÉ: `frontend/app.js` (+203 lignes, vue Mes Cours + source selector)
- MODIFIÉ: `frontend/index.html` (+5 lignes, bouton nav)
- MODIFIÉ: `frontend/style.css` (+207 lignes, styles PDF)

**Commit créé** :
- `b5fbb9d` - feat: add PDF import system and multi-source search (Mes Cours)
  - +895 lignes, -34 lignes
  - 1 nouveau fichier créé

**Résultat** : Système complet permettant d'uploader ses propres PDFs et de les interroger via le chatbot, seuls ou combinés avec Vikidia ! 🚀

---

## Previous Session Summary (2026-02-07 - Session 4)
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

**Oral pret ! Presentation + Guide technique disponibles.**

**Pour reviser la technique** :
- Lire `GUIDE_TECHNIQUE_ORAL.md` (13 questions/reponses du jury incluses)

**Pour presenter** :
```bash
# Ouvrir la presentation dans le navigateur
# Double-clic sur presentation.html ou Ctrl+O dans Chrome
# Navigation : fleches ← → ou Espace, Escape = retour slide 1
```

**Pour la demo live (slide 10)** :
```bash
cd backend && uvicorn main:app --reload --port 8000
# Ouvrir http://localhost:8000
```

**Apres l'oral, options suivantes** :
- Tests automatises (pytest + Playwright)
- Optimisation images mascottes (50MB → 3-5MB)
- Dashboard statistiques
- Deploiement Docker

**Commandes pour lancer l'app** :

```bash
cd C:\Users\skwar\Desktop\RAG

# Lancer le backend (dans un terminal)
cd backend
uvicorn main:app --reload --port 8000

# Ouvrir dans le navigateur
# http://localhost:8000

# Tester les features principales :
# 1. Chat → Poser une question → Vérifier réponse avec sources
# 2. Bibliothèque → Grille mascottes → Sélectionner matière → Liste leçons
# 3. Leçon → "📝 Faire un quiz" → Attendre génération (10-15s)
# 4. Quiz → Répondre aux questions → Naviguer → Soumettre
# 5. Résultats → Voir score + mascotte contextuelle → Review détaillée
# 6. Tester bouton 📝 rapide sur cartes bibliothèque
# 7. Vérifier localStorage : F12 → Application → Local Storage → quiz_history
# 8. Tester mode sombre 🌙 avec quiz
# 9. Tester responsive mobile (F12 → Device toolbar)
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
