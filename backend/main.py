"""API FastAPI pour le chatbot scolaire."""

import logging
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from rag import RAGChain
from detection import auto_detect
from pdf_service import PDFService

# Charger les variables d'environnement
load_dotenv()

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(
            open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
        ),
    ],
)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="Chatbot Assistant Scolaire",
    description="API RAG pour assistance scolaire niveau collège",
    version="1.0.0"
)

# CORS (pour développement local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production: restreindre aux domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser la chaîne RAG et le service PDF au démarrage
rag_chain: Optional[RAGChain] = None
pdf_service: Optional[PDFService] = None


@app.on_event("startup")
async def startup_event():
    """Initialise la chaîne RAG et le service PDF au démarrage de l'application."""
    global rag_chain, pdf_service
    logger.info("Démarrage de l'application...")
    try:
        rag_chain = RAGChain()
        logger.info("✅ RAG Chain initialisée avec succès")

        pdf_service = PDFService()
        logger.info("✅ PDF Service initialisé avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise


# Modèles Pydantic pour validation des requêtes/réponses
class ChatRequest(BaseModel):
    """Requête de chat."""
    question: str = Field(..., min_length=1, description="Question de l'élève")
    niveau: Optional[str] = Field("college", description="Niveau scolaire (6eme, 5eme, 4eme, 3eme, college)")
    matiere: Optional[str] = Field(None, description="Matière optionnelle pour filtrer")
    source: Optional[str] = Field("vikidia", description="Source des documents (vikidia, mes_cours, tous)")


class ChatResponse(BaseModel):
    """Réponse du chatbot."""
    answer: str = Field(..., description="Réponse générée")
    sources: list = Field(default=[], description="Sources utilisées")
    nb_sources: int = Field(..., description="Nombre de sources")


class HealthResponse(BaseModel):
    """Réponse du health check."""
    status: str
    message: str


# Routes API
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérifie que l'API fonctionne."""
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG Chain non initialisée")

    return {
        "status": "healthy",
        "message": "API opérationnelle"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint principal pour poser une question au chatbot.

    Args:
        request: Requête avec question, niveau et matière optionnelle.

    Returns:
        Réponse avec answer, sources et métadonnées.
    """
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG Chain non initialisée")

    try:
        logger.info(f"Question reçue: '{request.question}' (niveau={request.niveau}, matiere={request.matiere}, source={request.source})")

        # Exécuter la chaîne RAG
        result = rag_chain.run(
            question=request.question,
            matiere=request.matiere,
            niveau=request.niveau or "college",
            source=request.source or "vikidia"
        )

        logger.info(f"Réponse générée avec {result['nb_sources']} sources")
        return result

    except Exception as e:
        logger.error(f"Erreur lors du traitement: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/api/matieres")
async def get_matieres():
    """Retourne la liste des matières disponibles."""
    return {
        "matieres": [
            {"id": "mathematiques", "nom": "Mathématiques"},
            {"id": "francais", "nom": "Français"},
            {"id": "histoire_geo", "nom": "Histoire-Géographie"},
            {"id": "svt", "nom": "SVT"},
            {"id": "physique_chimie", "nom": "Physique-Chimie"},
            {"id": "technologie", "nom": "Technologie"},
            {"id": "anglais", "nom": "Anglais"},
            {"id": "espagnol", "nom": "Espagnol"},
        ]
    }


@app.get("/api/niveaux")
async def get_niveaux():
    """Retourne la liste des niveaux disponibles."""
    return {
        "niveaux": [
            {"id": "6eme", "nom": "6ème"},
            {"id": "5eme", "nom": "5ème"},
            {"id": "4eme", "nom": "4ème"},
            {"id": "3eme", "nom": "3ème"},
            {"id": "college", "nom": "Collège (tous niveaux)"},
        ]
    }


@app.post("/api/chat/auto", response_model=ChatResponse)
async def chat_auto(request: ChatRequest):
    """Endpoint chat avec auto-détection du niveau et de la matière.

    Args:
        request: Requête avec question (niveau/matiere sont optionnels et overridés si détectés).

    Returns:
        Réponse avec answer, sources, + niveau_detecte, matiere_detectee, matieres_possibles si ambiguïté.
    """
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG Chain non initialisée")

    try:
        question = request.question
        logger.info(f"Question reçue (auto-detect): '{question}'")

        # Auto-détection
        detection = auto_detect(question)
        niveau_final = request.niveau or detection["niveau_detecte"]
        matiere_finale = request.matiere or detection["matiere_detectee"]

        logger.info(f"Auto-détection: niveau={detection['niveau_detecte']}, "
                   f"matiere={detection['matiere_detectee']}, "
                   f"ambigue={detection['ambigue']}")

        # Exécuter la chaîne RAG
        result = rag_chain.run(
            question=question,
            matiere=matiere_finale,
            niveau=niveau_final,
            source=request.source or "vikidia"
        )

        # Ajouter les infos de détection à la réponse
        result["niveau_detecte"] = detection["niveau_detecte"]
        result["matiere_detectee"] = detection["matiere_detectee"]
        result["matieres_possibles"] = detection["matieres_possibles"]
        result["ambigue"] = detection["ambigue"]

        logger.info(f"Réponse générée avec {result['nb_sources']} sources")
        return result

    except Exception as e:
        logger.error(f"Erreur lors du traitement (auto): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/api/lecons/{matiere}")
async def get_lecons(matiere: str, niveau: Optional[str] = None, limit: int = 50000):
    """Retourne la liste des leçons disponibles pour une matière.

    Args:
        matiere: ID de la matière (mathematiques, francais, etc.).
        niveau: Niveau optionnel pour filtrer (6eme, 5eme, 4eme, 3eme).
        limit: Nombre maximum de leçons (défaut: 50000 pour tout récupérer).

    Returns:
        Liste de leçons avec titre, resume, url, niveau, nb_chunks.
    """
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG Chain non initialisée")

    try:
        logger.info(f"Récupération leçons: matiere={matiere}, niveau={niveau}")
        lessons = rag_chain.get_all_lessons(matiere, niveau, limit)

        return {
            "matiere": matiere,
            "niveau": niveau or "college",
            "nb_lecons": len(lessons),
            "lecons": lessons
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des leçons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/api/lecons/{matiere}/detail")
async def get_lecon_content(matiere: str, titre: str):
    """Retourne le contenu complet d'une leçon spécifique.

    Args:
        matiere: ID de la matière.
        titre: Titre exact de la leçon (query parameter).

    Returns:
        Contenu complet de la leçon avec metadata.
    """
    if rag_chain is None:
        raise HTTPException(status_code=503, detail="RAG Chain non initialisée")

    try:
        logger.info(f"Récupération contenu leçon: {titre} (matiere={matiere})")
        lesson = rag_chain.get_lesson_content(matiere, titre)

        if not lesson:
            raise HTTPException(status_code=404, detail="Leçon non trouvée")

        return lesson

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


# ===== ENDPOINTS PDF / MES COURS =====

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload et traite un PDF personnel.

    Args:
        file: Fichier PDF uploadé.

    Returns:
        Infos sur le PDF traité (nb_pages, nb_chunks, etc.).
    """
    if pdf_service is None:
        raise HTTPException(status_code=503, detail="PDF Service non initialisé")

    try:
        # Vérifier que c'est bien un PDF
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")

        logger.info(f"Upload PDF: {file.filename}")

        # Lire le contenu du fichier
        content = await file.read()

        # Sauvegarder le PDF
        file_path = pdf_service.save_pdf(content, file.filename)

        # Traiter le PDF (extraction + chunking + ChromaDB)
        result = pdf_service.process_pdf(file_path)

        logger.info(f"PDF traité avec succès: {result}")
        return {
            "status": "success",
            "message": f"PDF '{file.filename}' importé avec succès",
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload du PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/api/mes-cours")
async def get_mes_cours():
    """Retourne la liste des PDFs importés.

    Returns:
        Liste de PDFs avec infos (filename, size, uploaded_at).
    """
    if pdf_service is None:
        raise HTTPException(status_code=503, detail="PDF Service non initialisé")

    try:
        logger.info("Récupération de la liste des PDFs")
        pdfs = pdf_service.list_pdfs()

        return {
            "nb_pdfs": len(pdfs),
            "pdfs": pdfs
        }

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des PDFs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.delete("/api/mes-cours/{filename}")
async def delete_cours(filename: str):
    """Supprime un PDF importé.

    Args:
        filename: Nom du fichier à supprimer.

    Returns:
        Status de la suppression.
    """
    if pdf_service is None:
        raise HTTPException(status_code=503, detail="PDF Service non initialisé")

    try:
        logger.info(f"Suppression du PDF: {filename}")
        success = pdf_service.delete_pdf(filename)

        if not success:
            raise HTTPException(status_code=404, detail="PDF non trouvé")

        return {
            "status": "success",
            "message": f"PDF '{filename}' supprimé avec succès"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.post("/api/search-mes-cours")
async def search_mes_cours(request: ChatRequest):
    """Recherche dans les documents personnels uniquement.

    Args:
        request: Requête avec question.

    Returns:
        Résultats de recherche dans les PDFs personnels.
    """
    if pdf_service is None:
        raise HTTPException(status_code=503, detail="PDF Service non initialisé")

    try:
        logger.info(f"Recherche dans Mes Cours: '{request.question}'")

        results = pdf_service.search_in_personal_docs(
            question=request.question,
            top_k=5
        )

        return {
            "question": request.question,
            "nb_results": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


# Servir le frontend (fichiers statiques)
from pathlib import Path
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
