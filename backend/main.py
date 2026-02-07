"""API FastAPI pour le chatbot scolaire."""

import logging
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from rag import RAGChain

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

# Initialiser la chaîne RAG au démarrage
rag_chain: Optional[RAGChain] = None


@app.on_event("startup")
async def startup_event():
    """Initialise la chaîne RAG au démarrage de l'application."""
    global rag_chain
    logger.info("Démarrage de l'application...")
    try:
        rag_chain = RAGChain()
        logger.info("✅ RAG Chain initialisée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation du RAG: {e}")
        raise


# Modèles Pydantic pour validation des requêtes/réponses
class ChatRequest(BaseModel):
    """Requête de chat."""
    question: str = Field(..., min_length=1, description="Question de l'élève")
    niveau: Optional[str] = Field("college", description="Niveau scolaire (6eme, 5eme, 4eme, 3eme, college)")
    matiere: Optional[str] = Field(None, description="Matière optionnelle pour filtrer")


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
        logger.info(f"Question reçue: '{request.question}' (niveau={request.niveau}, matiere={request.matiere})")

        # Exécuter la chaîne RAG
        result = rag_chain.run(
            question=request.question,
            matiere=request.matiere,
            niveau=request.niveau or "college"
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


# Servir le frontend (fichiers statiques)
# Note: décommenter quand le frontend sera créé
# app.mount("/static", StaticFiles(directory="frontend"), name="static")

# @app.get("/")
# async def serve_frontend():
#     """Sert la page d'accueil du frontend."""
#     return FileResponse("frontend/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
