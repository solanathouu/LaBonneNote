"""Découpage du texte en chunks pour l'embedding et le stockage vectoriel."""

import logging

logger = logging.getLogger(__name__)

# Approximation : 1 token ≈ 4 caractères en français
CHARS_PAR_TOKEN = 4
TAILLE_CHUNK_TOKENS = 500
OVERLAP_TOKENS = 50

TAILLE_CHUNK_CHARS = TAILLE_CHUNK_TOKENS * CHARS_PAR_TOKEN  # ~2000 caractères
OVERLAP_CHARS = OVERLAP_TOKENS * CHARS_PAR_TOKEN  # ~200 caractères
TAILLE_MIN_CHUNK_CHARS = 100  # Ignorer les chunks trop petits


def decouper_en_chunks(texte: str, titre: str = "") -> list[dict]:
    """Découpe un texte en chunks de taille appropriée pour l'embedding.

    Stratégie : découpage par paragraphes/sections d'abord, puis par phrases
    si un paragraphe est trop long. Overlap entre chunks pour le contexte.

    Args:
        texte: Texte nettoyé à découper.
        titre: Titre de la page source (ajouté en contexte dans chaque chunk).

    Returns:
        Liste de dicts avec 'text' et 'index' (position du chunk).
    """
    if not texte or len(texte.strip()) < TAILLE_MIN_CHUNK_CHARS:
        if texte and texte.strip():
            return [{"text": _prepend_titre(texte.strip(), titre), "index": 0}]
        return []

    # Découper par sections (double saut de ligne)
    sections = texte.split("\n\n")
    sections = [s.strip() for s in sections if s.strip()]

    chunks = []
    buffer = ""

    for section in sections:
        # Si ajouter cette section dépasse la taille max
        if len(buffer) + len(section) + 2 > TAILLE_CHUNK_CHARS:
            if buffer:
                chunks.append(buffer.strip())

            # Si la section elle-même est trop longue, la découper par phrases
            if len(section) > TAILLE_CHUNK_CHARS:
                sous_chunks = _decouper_par_phrases(section)
                chunks.extend(sous_chunks)
                buffer = ""
            else:
                # Commencer un nouveau buffer avec overlap
                buffer = _extraire_overlap(buffer) + "\n\n" + section if buffer else section
        else:
            buffer = buffer + "\n\n" + section if buffer else section

    # Dernier buffer
    if buffer and len(buffer.strip()) >= TAILLE_MIN_CHUNK_CHARS:
        chunks.append(buffer.strip())

    # Ajouter le titre et l'index à chaque chunk
    resultats = []
    for i, chunk in enumerate(chunks):
        texte_chunk = _prepend_titre(chunk, titre)
        resultats.append({"text": texte_chunk, "index": i})

    logger.info("Texte découpé en %d chunks (titre: %s)", len(resultats), titre)
    return resultats


def _decouper_par_phrases(texte: str) -> list[str]:
    """Découpe un texte long par phrases pour respecter la taille max."""
    # Séparer par phrases (point + espace + majuscule ou fin de ligne)
    import re
    phrases = re.split(r"(?<=[.!?])\s+", texte)

    chunks = []
    buffer = ""

    for phrase in phrases:
        if len(buffer) + len(phrase) + 1 > TAILLE_CHUNK_CHARS:
            if buffer:
                chunks.append(buffer.strip())
            buffer = _extraire_overlap(buffer) + " " + phrase if buffer else phrase
        else:
            buffer = buffer + " " + phrase if buffer else phrase

    if buffer and len(buffer.strip()) >= TAILLE_MIN_CHUNK_CHARS:
        chunks.append(buffer.strip())

    return chunks


def _extraire_overlap(texte: str) -> str:
    """Extrait les derniers caractères d'un texte pour l'overlap."""
    if not texte or len(texte) <= OVERLAP_CHARS:
        return texte
    # Couper au dernier espace pour ne pas couper un mot
    overlap = texte[-OVERLAP_CHARS:]
    espace = overlap.find(" ")
    if espace > 0:
        overlap = overlap[espace + 1:]
    return overlap


def _prepend_titre(texte: str, titre: str) -> str:
    """Ajoute le titre en contexte au début du chunk."""
    if titre:
        return f"[{titre}]\n{texte}"
    return texte
