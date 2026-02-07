"""
Script d'ingestion des chunks dans ChromaDB.
Charge tous les chunks depuis data/processed/ et les stocke dans ChromaDB avec embeddings OpenAI.
"""
import json
import logging
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHROMADB_DIR = PROJECT_ROOT / "chromadb"

# Configuration ChromaDB
COLLECTION_NAME = "cours_college"
EMBEDDING_MODEL = "text-embedding-3-small"


def load_chunks_from_matiere(matiere_dir: Path) -> List[dict]:
    """Charge les chunks d'une matière depuis le fichier chunks.json."""
    chunks_file = matiere_dir / "chunks.json"

    if not chunks_file.exists():
        logger.warning(f"Fichier chunks.json introuvable pour {matiere_dir.name}")
        return []

    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    logger.info(f"Chargé {len(chunks)} chunks depuis {matiere_dir.name}")
    return chunks


def load_all_chunks() -> List[dict]:
    """Charge tous les chunks de toutes les matières."""
    all_chunks = []

    if not PROCESSED_DIR.exists():
        logger.error(f"Répertoire {PROCESSED_DIR} introuvable")
        return []

    for matiere_dir in PROCESSED_DIR.iterdir():
        if matiere_dir.is_dir():
            chunks = load_chunks_from_matiere(matiere_dir)
            all_chunks.extend(chunks)

    logger.info(f"Total: {len(all_chunks)} chunks chargés")
    return all_chunks


def chunks_to_documents(chunks: List[dict]) -> List[Document]:
    """Convertit les chunks au format LangChain Document."""
    documents = []

    for chunk in chunks:
        doc = Document(
            page_content=chunk["text"],
            metadata=chunk["metadata"]
        )
        documents.append(doc)

    return documents


def ingest_to_chromadb(documents: List[Document], batch_size: int = 100):
    """Ingère les documents dans ChromaDB avec embeddings OpenAI."""

    # Initialiser les embeddings OpenAI
    logger.info(f"Initialisation embeddings: {EMBEDDING_MODEL}")
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # Créer/charger ChromaDB avec persistance
    logger.info(f"Initialisation ChromaDB: {CHROMADB_DIR}")
    CHROMADB_DIR.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMADB_DIR)
    )

    # Ajouter les documents par batch pour éviter les timeout
    total = len(documents)
    logger.info(f"Ingestion de {total} documents par batch de {batch_size}")

    for i in range(0, total, batch_size):
        batch = documents[i:i+batch_size]
        vector_store.add_documents(documents=batch)
        logger.info(f"[PROGRESSION] {min(i+batch_size, total)}/{total} documents ingérés ({100*min(i+batch_size, total)//total}%)")

    logger.info(f"✅ Ingestion terminée: {total} documents dans ChromaDB")

    # Vérification
    collection = vector_store._collection
    count = collection.count()
    logger.info(f"Vérification: {count} documents dans la collection '{COLLECTION_NAME}'")

    return vector_store


def main():
    """Fonction principale."""
    logger.info("=== Début de l'ingestion ChromaDB ===")

    # 1. Charger tous les chunks
    chunks = load_all_chunks()
    if not chunks:
        logger.error("Aucun chunk trouvé. Arrêt.")
        return

    # 2. Convertir en Documents LangChain
    logger.info("Conversion en Documents LangChain")
    documents = chunks_to_documents(chunks)

    # 3. Ingérer dans ChromaDB
    vector_store = ingest_to_chromadb(documents, batch_size=100)

    logger.info("=== Ingestion terminée avec succès ===")


if __name__ == "__main__":
    main()
