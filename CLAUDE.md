# Chatbot Assistant Scolaire - College Francais

## Objectif
Chatbot RAG qui repond **uniquement** a partir de cours et programmes scolaires du college francais (6eme-3eme). Le bot refuse de repondre si l'information n'existe pas dans la base de donnees.

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
| Tests | ⏳ Non implementes (backend teste manuellement) |
| Deployment | ⏳ Local uniquement (port 8000) |
| Git status | ✅ Clean - Dernier commit: de7f560 (mascottes par matière) |

## Last Session Summary (2026-02-11 - Session 10)
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

**L'application est production-ready avec mascottes dynamiques par matière complètement intégrées !**

Pour reprendre le travail, choisir parmi ces options :

**Option 1 - Optimisation Images (1h)** :
```bash
# Réduire taille PNG : 50MB → 3-5MB cible
python scripts/optimize_mascot_images.py  # À créer
# Convertir en WebP pour performance web
```

**Option 3 - Tests Automatisés (8h)** :
```bash
# Tests backend pytest
cd backend && pytest tests/test_rag.py tests/test_pdf_service.py
```

**Option 4 - Dashboard Stats (4h)** :
```bash
# Nouvelle vue avec statistiques d'utilisation
# - Nombre de PDFs uploadés
# - Questions posées par matière
# - Sources les plus consultées
```

**Option 5 - Déploiement Production (6h)** :
```bash
# Containerisation Docker
# Configuration Nginx reverse proxy
# SSL/HTTPS avec Let's Encrypt
# Déploiement sur VPS/Cloud
```

**Commandes pour lancer l'app** :

```bash
cd C:\Users\skwar\Desktop\RAG

# Lancer le backend (dans un terminal)
cd backend
uvicorn main:app --reload --port 8000

# Ouvrir dans le navigateur
# http://localhost:8000

# Tester les nouvelles features mascottes :
# 1. Cliquer sur "📚 Bibliothèque" → Voir la grille de 8 cartes mascottes
# 2. Cliquer sur une carte matière → Voir la mascotte dans le header
# 3. Ouvrir une leçon → Voir la mascotte dans le header de détail
# 4. Retour au Chat → Poser une question de maths → Voir Math.png dans l'avatar bot
# 5. Tester le mode sombre 🌙 avec les nouvelles cartes
# 6. Tester sur mobile (responsive) → Tailles adaptées
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
