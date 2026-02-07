"""Détection automatique du niveau et de la matière depuis une question."""

import re
from typing import Dict, List, Optional


# Mots-clés par matière (lowercase pour matching case-insensitive)
KEYWORDS_BY_MATIERE = {
    "mathematiques": [
        "théorème", "pythagore", "triangle", "équation", "fraction", "décimal",
        "géométrie", "calcul", "nombre", "multiplication", "division", "addition",
        "soustraction", "aire", "périmètre", "volume", "angle", "parallèle",
        "perpendiculaire", "symétrie", "fonction", "graphique", "algèbre",
        "proportionnalité", "pourcentage", "statistique", "probabilité"
    ],
    "francais": [
        "verbe", "conjugaison", "grammaire", "orthographe", "accord", "participe",
        "sujet", "complément", "pronom", "adjectif", "adverbe", "phrase",
        "ponctuation", "temps", "imparfait", "passé", "futur", "présent",
        "conditionnel", "subjonctif", "littérature", "poème", "roman", "auteur",
        "écrivain", "vocabulaire", "synonyme", "antonyme", "homonyme"
    ],
    "histoire_geo": [
        "guerre", "révolution", "roi", "empereur", "moyen âge", "renaissance",
        "antiquité", "préhistoire", "napoléon", "louis", "république", "empire",
        "démocratie", "monarchie", "bataille", "traité", "colonisation",
        "continent", "pays", "ville", "capitale", "océan", "mer", "montagne",
        "fleuve", "climat", "population", "frontière", "carte", "région"
    ],
    "svt": [
        "cellule", "organe", "corps", "respiration", "digestion", "circulation",
        "reproduction", "adn", "génétique", "évolution", "espèce", "animal",
        "plante", "photosynthèse", "écosystème", "chaîne alimentaire", "fossile",
        "roche", "séisme", "volcan", "érosion", "tectonique", "planète", "terre"
    ],
    "physique_chimie": [
        "atome", "molécule", "réaction", "chimique", "élément", "ion", "acide",
        "base", "ph", "électricité", "circuit", "courant", "tension", "résistance",
        "énergie", "force", "vitesse", "masse", "poids", "lumière", "optique",
        "lentille", "miroir", "son", "onde", "température", "chaleur"
    ],
    "technologie": [
        "ordinateur", "programmation", "robot", "algorithme", "code", "logiciel",
        "matériau", "construction", "pont", "structure", "énergie renouvelable",
        "électronique", "circuit électrique", "capteur", "actionneur", "design",
        "prototype", "innovation", "automatisme"
    ],
    "anglais": [
        "english", "anglais", "verb", "grammar", "vocabulary", "tense",
        "present", "past", "future", "question", "answer"
    ],
    "espagnol": [
        "español", "espagnol", "verbo", "gramática", "vocabulario", "tiempo",
        "presente", "pasado", "futuro", "pregunta", "respuesta"
    ]
}

# Mots-clés de niveau (complexité du vocabulaire)
NIVEAU_INDICATORS = {
    "6eme": {
        "keywords": ["base", "simple", "découvrir", "commencer", "introduction"],
        "complexity_max": 3  # Phrases simples
    },
    "5eme": {
        "keywords": ["expliquer", "comprendre", "définition"],
        "complexity_max": 4
    },
    "4eme": {
        "keywords": ["analyser", "développer", "argumenter"],
        "complexity_max": 5
    },
    "3eme": {
        "keywords": ["approfondir", "synthétiser", "démontrer", "brevet"],
        "complexity_max": 6
    }
}


def detect_matiere(question: str) -> Dict[str, any]:
    """Détecte la matière depuis la question.

    Args:
        question: Question de l'élève (texte libre).

    Returns:
        Dict avec:
        - matiere_principale: matière la plus probable (str ou None)
        - matieres_possibles: liste des matières ambiguës si score proche
        - scores: scores par matière
    """
    question_lower = question.lower()
    scores = {}

    # Compter les mots-clés matchés par matière
    for matiere, keywords in KEYWORDS_BY_MATIERE.items():
        count = sum(1 for kw in keywords if kw in question_lower)
        scores[matiere] = count

    # Trier par score décroissant
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Si aucun match
    if sorted_scores[0][1] == 0:
        return {
            "matiere_principale": None,
            "matieres_possibles": [],
            "scores": scores
        }

    # Si ambiguïté (2 matières avec scores proches)
    top_score = sorted_scores[0][1]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

    if top_score == second_score and top_score > 0:
        # Ambiguïté : retourner les 2 meilleures
        return {
            "matiere_principale": sorted_scores[0][0],
            "matieres_possibles": [sorted_scores[0][0], sorted_scores[1][0]],
            "scores": scores
        }
    elif second_score > 0 and (top_score - second_score) <= 1:
        # Scores très proches (différence de 1 seul mot-clé)
        return {
            "matiere_principale": sorted_scores[0][0],
            "matieres_possibles": [sorted_scores[0][0], sorted_scores[1][0]],
            "scores": scores
        }
    else:
        # Matière claire
        return {
            "matiere_principale": sorted_scores[0][0],
            "matieres_possibles": [],
            "scores": scores
        }


def detect_niveau(question: str) -> str:
    """Détecte le niveau scolaire depuis la question (heuristique simple).

    Args:
        question: Question de l'élève.

    Returns:
        Niveau détecté (6eme, 5eme, 4eme, 3eme, ou college par défaut).
    """
    question_lower = question.lower()

    # Vérifier si le niveau est explicitement mentionné
    if "6ème" in question or "6eme" in question or "sixième" in question:
        return "6eme"
    if "5ème" in question or "5eme" in question or "cinquième" in question:
        return "5eme"
    if "4ème" in question or "4eme" in question or "quatrième" in question:
        return "4eme"
    if "3ème" in question or "3eme" in question or "troisième" in question or "brevet" in question:
        return "3eme"

    # Sinon, heuristique basée sur la complexité
    # Compter les mots et longueur moyenne
    words = question.split()
    num_words = len(words)
    avg_word_length = sum(len(w) for w in words) / max(num_words, 1)

    # Complexité simple
    if num_words < 8 and avg_word_length < 6:
        return "6eme"
    elif num_words < 12 and avg_word_length < 7:
        return "5eme"
    elif num_words < 16:
        return "4eme"
    else:
        return "3eme"


def auto_detect(question: str) -> Dict[str, any]:
    """Détection automatique complète : niveau + matière.

    Args:
        question: Question de l'élève.

    Returns:
        Dict avec niveau_detecte, matiere_detectee, matieres_possibles, ambigue.
    """
    niveau = detect_niveau(question)
    matiere_result = detect_matiere(question)

    return {
        "niveau_detecte": niveau,
        "matiere_detectee": matiere_result["matiere_principale"],
        "matieres_possibles": matiere_result["matieres_possibles"],
        "ambigue": len(matiere_result["matieres_possibles"]) > 1,
        "scores": matiere_result["scores"]
    }
