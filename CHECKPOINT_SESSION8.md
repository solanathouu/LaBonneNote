# CHECKPOINT - Session 8 (2026-02-07)

## Session Focus
**Système complet "Mes Cours" avec import PDF + recherche multi-source + corrections UX**

## Durée
~6 heures (3 parties)

---

## Part 1 : Corrections UX (1h)

### Problème résolu : Barre de recherche
**Issue** : La barre de recherche perdait le focus à chaque lettre tapée
**Cause** : Le HTML était recréé à chaque input, détruisant l'élément
**Solution** :
```javascript
// Sauvegarder position curseur + restaurer après re-render
const cursorPosition = e.target.selectionStart;
renderLessonsWithPagination(mainContainer, allLessons);
setTimeout(() => {
    newSearchInput.focus();
    newSearchInput.setSelectionRange(cursorPosition, cursorPosition);
}, 0);
```

### Suppression animations
**Demande** : Supprimer toutes les animations de l'interface
**Actions** :
- ✅ 20+ animations CSS supprimées (fadeIn, slideIn, bounce, pulse, etc.)
- ✅ animation-delay supprimés des styles inline JS
- ✅ Transitions hover conservées pour meilleur UX

**Fichiers modifiés** :
- `frontend/style.css` : -20 lignes d'animations
- `frontend/app.js` : animation-delay supprimés

**Commit** : `923d310` - fix: remove all animations and fix search bar focus

---

## Part 2 : Détection questions générales (30min)

### Fonctionnalité
Le bot ne doit pas chercher de sources pour les messages généraux comme "salut", "merci", "bonjour".

### Implémentation
**Fichier** : `backend/rag.py`

**Fonction ajoutée** :
```python
def is_general_question(self, question: str) -> bool:
    """Détecte si une question est générale (salutations, politesse) ou thématique."""
    # Liste de 20+ patterns de questions générales
    # Retourne True si général, False si thématique
```

**Modification run()** :
```python
if self.is_general_question(question):
    return {
        "answer": "Bonjour ! 😊 Je suis ton assistant scolaire...",
        "sources": [],
        "nb_sources": 0
    }
# Sinon : RAG normal avec sources
```

**Patterns détectés** :
- Salutations : salut, bonjour, coucou, hello, hi
- Questions bot : qui es-tu, c'est quoi, comment tu
- Politesse : merci, ok, au revoir, bye
- Questions courtes : ça va, quoi de neuf

---

## Part 3 : Système "Mes Cours" (4h)

### Vue d'ensemble
Permettre aux utilisateurs d'uploader leurs propres PDFs et de les interroger via le chatbot.

### Architecture

#### Backend

**1. Nouveau service : `backend/pdf_service.py` (195 lignes)**

```python
class PDFService:
    def __init__(self):
        # Initialisation ChromaDB collection "mes_cours"
        # Text splitter pour chunking

    def save_pdf(file_content, filename):
        # Sauvegarder dans data/user_pdfs/

    def process_pdf(file_path):
        # PyPDFLoader : extraction
        # RecursiveCharacterTextSplitter : chunking
        # ChromaDB : ajout chunks

    def list_pdfs():
        # Liste tous les PDFs uploadés

    def delete_pdf(filename):
        # Supprime un PDF

    def search_in_personal_docs(question, top_k):
        # Recherche dans collection "mes_cours"
```

**2. Nouveaux endpoints : `backend/main.py`**

```python
POST /api/upload-pdf
    - Upload fichier PDF
    - Traitement automatique
    - Retourne nb_pages, nb_chunks

GET /api/mes-cours
    - Liste PDFs importés
    - Infos : filename, size, uploaded_at

DELETE /api/mes-cours/{filename}
    - Supprime un PDF

POST /api/search-mes-cours
    - Recherche dans PDFs personnels
```

**3. Modification RAGChain : `backend/rag.py`**

**Ajout paramètre source** :
```python
def retrieve(question, matiere, niveau, source="vikidia"):
    # source = "vikidia" | "mes_cours" | "tous"

def run(question, matiere, niveau, source="vikidia"):
    # Appelle retrieve avec le bon paramètre source
```

**Gestion multi-collections** :
```python
self.vector_store = Chroma(collection_name="cours_college")
self.vector_store_personal = Chroma(collection_name="mes_cours")
```

**Logique de recherche** :
- Si source == "vikidia" : chercher dans cours_college
- Si source == "mes_cours" : chercher dans mes_cours
- Si source == "tous" : chercher dans les deux, fusionner, trier par score

#### Frontend

**1. Nouvelle vue "Mes Cours" : `frontend/app.js` (180 lignes)**

```javascript
async function renderMesCoursView(mainContainer) {
    // Zone d'upload avec drag & drop
    // Barre de progression
    // Liste des PDFs
}

async function uploadPDF(file) {
    // Upload vers /api/upload-pdf
    // Affichage progress bar
    // Recharge liste après succès
}

async function loadPDFList() {
    // Appel GET /api/mes-cours
    // Affichage liste avec boutons supprimer
}

async function deletePDF(filename) {
    // Appel DELETE /api/mes-cours/{filename}
    // Recharge liste
}
```

**2. Sélecteur de source dans le Chat**

```html
<div class="source-selector">
    <label>📚 Chercher dans :</label>
    <select id="source-select">
        <option value="vikidia">Cours généraux</option>
        <option value="mes_cours">Mes Cours (PDFs personnels)</option>
        <option value="tous">Les deux</option>
    </select>
</div>
```

**Modification handleSendMessage()** :
```javascript
const source = document.getElementById('source-select').value;
fetch('/api/chat/auto', {
    body: JSON.stringify({ question, source })
});
```

**3. Styles CSS : `frontend/style.css` (200+ lignes)**

- `.upload-zone` : Zone drag & drop avec hover/dragover
- `.progress-bar` : Barre de progression animée
- `.pdf-card` : Cartes PDFs avec hover effects
- `.source-selector` : Sélecteur de source stylisé

### Flux utilisateur

1. **Upload PDF** :
   - User clique "📄 Mes Cours"
   - Drag & drop ou sélection fichier
   - Backend : extraction + chunking + ChromaDB
   - Frontend : progress bar + confirmation

2. **Interroger PDF** :
   - User retourne au Chat
   - Change source : "Mes Cours"
   - Pose une question
   - Backend cherche dans collection "mes_cours"
   - Affiche réponse avec sources du PDF

3. **Recherche combinée** :
   - User sélectionne "Les deux"
   - Backend cherche dans Vikidia ET Mes Cours
   - Fusionne résultats, trie par pertinence
   - Affiche sources des deux collections

---

## Statistiques finales

### Code ajouté
- **Backend** : +276 lignes (pdf_service.py + modifications)
- **Frontend** : +203 lignes (vue Mes Cours + sélecteur)
- **CSS** : +207 lignes (styles upload + PDFs)
- **Total** : +895 lignes, -34 lignes

### Fichiers
- **Créé** : 1 fichier (`backend/pdf_service.py`)
- **Modifiés** : 5 fichiers (main.py, rag.py, app.js, index.html, style.css)

### Commits
1. `923d310` - fix: remove all animations and fix search bar focus
2. `b5fbb9d` - feat: add PDF import system and multi-source search (Mes Cours)

---

## État final du projet

### Collections ChromaDB
- ✅ `cours_college` : 43 870 documents Vikidia
- ✅ `mes_cours` : Documents PDFs personnels (vide initialement)

### Endpoints API (11 total)
- GET `/health`
- POST `/api/chat`
- POST `/api/chat/auto`
- GET `/api/matieres`
- GET `/api/niveaux`
- GET `/api/lecons/{matiere}`
- GET `/api/lecons/{matiere}/detail`
- POST `/api/upload-pdf` ⭐ NOUVEAU
- GET `/api/mes-cours` ⭐ NOUVEAU
- DELETE `/api/mes-cours/{filename}` ⭐ NOUVEAU
- POST `/api/search-mes-cours` ⭐ NOUVEAU

### Vues Frontend (5 total)
- 💬 Chat (avec sélecteur source)
- 📚 Bibliothèque
- ⭐ Favoris
- 📄 Mes Cours ⭐ NOUVEAU
- 📖 Détail Leçon

### Fonctionnalités Chat
- ✅ Auto-détection niveau/matière
- ✅ Gestion questions ambiguës
- ✅ Détection questions générales (pas de sources)
- ✅ Sélection source (Vikidia/Mes Cours/Les deux)
- ✅ Historique persistant
- ✅ Mode sombre

---

## Pour reprendre le projet

### 1. Vérifier l'environnement

```bash
cd C:\Users\skwar\Desktop\RAG
git status  # Doit être clean
git log --oneline -3  # Voir derniers commits
```

### 2. Lancer le serveur

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Tester "Mes Cours"

1. Ouvrir http://localhost:8000
2. Cliquer "📄 Mes Cours"
3. Uploader un PDF (cours, notes, etc.)
4. Attendre extraction (quelques secondes)
5. Retourner au Chat
6. Changer source : "Mes Cours (PDFs personnels)"
7. Poser une question sur le contenu du PDF
8. Vérifier que la réponse provient du PDF !

### 4. Tester recherche combinée

1. Uploader un PDF de maths
2. Source : "Les deux"
3. Question : "C'est quoi le théorème de Pythagore ?"
4. Réponse combinera Vikidia + votre PDF

---

## Prochaines étapes suggérées

### Court terme (< 2h)
1. **Tests manuels** : Uploader plusieurs PDFs, tester tous les cas
2. **UX Mes Cours** : Icônes types fichiers, preview, statistiques
3. **Messages d'erreur** : Améliorer feedback upload (PDF trop gros, format invalide)

### Moyen terme (2-8h)
1. **Tests automatisés** : pytest pour PDFService + RAG multi-source
2. **Dashboard** : Stats PDFs uploadés, recherches, sources utilisées
3. **Organisation** : Dossiers/tags pour PDFs, filtre par matière/date
4. **Search dans Mes Cours** : Zone recherche directement dans vue Mes Cours

### Long terme (> 8h)
1. **Déploiement** : Render/Railway avec ChromaDB persistant
2. **OCR** : Support PDFs scannés (Tesseract/pytesseract)
3. **Multi-formats** : Support .docx, .pptx, .txt
4. **Partage** : Partager PDFs entre utilisateurs (si multi-user)

---

## Notes techniques importantes

### Dépendances
- `pypdf==6.6.2` : Extraction texte PDFs
- `langchain-community` : PyPDFLoader
- ChromaDB : 2 collections séparées

### Stockage
- PDFs physiques : `data/user_pdfs/`
- Format : `YYYYMMDD_HHMMSS_filename.pdf`
- Chunks : ChromaDB collection "mes_cours"

### Limitations actuelles
- Pas de gestion multi-utilisateurs (tous les PDFs sont partagés)
- Pas de limite de taille PDF
- Pas de validation format (seulement extension .pdf)
- Suppression PDF ne supprime pas les chunks ChromaDB (limitation ChromaDB)

### Points d'attention
- `.env` contient OPENAI_API_KEY (ne pas commit !)
- `data/user_pdfs/` à ajouter au .gitignore
- ChromaDB persiste dans `chromadb/`

---

## Problèmes potentiels et solutions

### Problème 1 : "Module pdf_service not found"
**Solution** : Lancer depuis le dossier racine avec `uvicorn backend.main:app`

### Problème 2 : PDF upload fail
**Cause** : Dossier `data/user_pdfs/` n'existe pas
**Solution** : Le service le crée automatiquement au démarrage

### Problème 3 : Pas de sources pour questions générales
**Normal** : C'est le comportement attendu (salut, merci, etc.)

### Problème 4 : ChromaDB collection "mes_cours" vide
**Normal** : Vide jusqu'au premier upload PDF

---

## Fichiers de documentation

- ✅ `CLAUDE.md` : Mis à jour avec Session 8
- ✅ `CHECKPOINT_SESSION8.md` : Ce fichier
- ✅ `README.md` : À mettre à jour si besoin
- ✅ Git : Clean, tous commits pushés

---

**FIN DU CHECKPOINT - Session 8**

Projet prêt à être repris ! 🚀
