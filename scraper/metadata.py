"""Gestion des métadonnées pour les chunks scrapés."""

import logging

logger = logging.getLogger(__name__)

# Mapping catégorie Vikidia → matière
CATEGORIES_MATIERES = {
    # Mathématiques
    "Catégorie:Mathématiques": "mathematiques",
    "Catégorie:Algèbre": "mathematiques",
    "Catégorie:Arithmétique": "mathematiques",
    "Catégorie:Calcul": "mathematiques",
    "Catégorie:Géométrie": "mathematiques",
    "Catégorie:Nombre": "mathematiques",
    "Catégorie:Numération": "mathematiques",
    "Catégorie:Statistiques": "mathematiques",
    "Catégorie:Fonction": "mathematiques",
    "Catégorie:Analyse": "mathematiques",
    "Catégorie:Unité de mesure": "mathematiques",
    # Français
    "Catégorie:Français": "francais",
    "Catégorie:Grammaire": "francais",
    "Catégorie:Littérature": "francais",
    "Catégorie:Conjugaison": "francais",
    "Catégorie:Classe grammaticale": "francais",
    "Catégorie:Nature d'un mot": "francais",
    "Catégorie:Ponctuation": "francais",
    "Catégorie:Littérature française": "francais",
    "Catégorie:Genre ou forme littéraire": "francais",
    "Catégorie:Écrivain": "francais",
    "Catégorie:Écrivaine": "francais",
    "Catégorie:Livre": "francais",
    "Catégorie:Récit": "francais",
    # Histoire
    "Catégorie:Histoire": "histoire_geo",
    "Catégorie:Histoire par continent": "histoire_geo",
    "Catégorie:Histoire par pays": "histoire_geo",
    "Catégorie:Histoire par thème": "histoire_geo",
    "Catégorie:Histoire par siècle": "histoire_geo",
    "Catégorie:Période historique": "histoire_geo",
    "Catégorie:Personnalité historique": "histoire_geo",
    "Catégorie:Civilisation": "histoire_geo",
    "Catégorie:Guerre": "histoire_geo",
    "Catégorie:Chronologie": "histoire_geo",
    "Catégorie:Archéologie": "histoire_geo",
    "Catégorie:Colonisation": "histoire_geo",
    "Catégorie:Peuple": "histoire_geo",
    # Géographie
    "Catégorie:Géographie": "histoire_geo",
    "Catégorie:Géographie par continent": "histoire_geo",
    "Catégorie:Géographie par pays": "histoire_geo",
    "Catégorie:Continent": "histoire_geo",
    "Catégorie:Pays": "histoire_geo",
    "Catégorie:Capitale": "histoire_geo",
    "Catégorie:Climat": "histoire_geo",
    "Catégorie:Relief": "histoire_geo",
    "Catégorie:Cours d'eau": "histoire_geo",
    "Catégorie:Cartographie": "histoire_geo",
    "Catégorie:Ville": "histoire_geo",
    "Catégorie:Île": "histoire_geo",
    "Catégorie:Lac": "histoire_geo",
    "Catégorie:Terre": "histoire_geo",
    "Catégorie:Démographie": "histoire_geo",
    # SVT (Sciences de la Vie et de la Terre)
    "Catégorie:Biologie": "svt",
    "Catégorie:Anatomie": "svt",
    "Catégorie:Botanique": "svt",
    "Catégorie:Cellule": "svt",
    "Catégorie:Évolution": "svt",
    "Catégorie:Génétique": "svt",
    "Catégorie:Microbiologie": "svt",
    "Catégorie:Zoologie": "svt",
    "Catégorie:Écologie": "svt",
    "Catégorie:Géologie": "svt",
    "Catégorie:Fossile": "svt",
    "Catégorie:Minéral": "svt",
    "Catégorie:Roche": "svt",
    "Catégorie:Érosion": "svt",
    "Catégorie:Ressource naturelle": "svt",
    # Physique-Chimie
    "Catégorie:Physique": "physique_chimie",
    "Catégorie:Chimie": "physique_chimie",
    "Catégorie:Électromagnétisme": "physique_chimie",
    "Catégorie:Gaz": "physique_chimie",
    "Catégorie:Grandeur physique": "physique_chimie",
    "Catégorie:Loi de la physique": "physique_chimie",
    "Catégorie:Mécanique": "physique_chimie",
    "Catégorie:Optique": "physique_chimie",
    "Catégorie:Thermodynamique": "physique_chimie",
    "Catégorie:Atome": "physique_chimie",
    "Catégorie:Classification chimique": "physique_chimie",
    "Catégorie:Acide": "physique_chimie",
    "Catégorie:Air": "physique_chimie",
    # Technologie
    "Catégorie:Technologie": "technologie",
    "Catégorie:Aéronautique": "technologie",
    "Catégorie:Astronautique": "technologie",
    "Catégorie:Instrument de mesure": "technologie",
    "Catégorie:Outil": "technologie",
    "Catégorie:Robot": "technologie",
    # Anglais
    "Catégorie:Anglais": "anglais",
    # Espagnol
    "Catégorie:Espagnol": "espagnol",
}

# Catégories racines à scraper par matière
CATEGORIES_RACINES = {
    "mathematiques": [
        "Catégorie:Mathématiques",
    ],
    "francais": [
        "Catégorie:Français",
        "Catégorie:Grammaire",
        "Catégorie:Littérature",
    ],
    "histoire_geo": [
        "Catégorie:Histoire",
        "Catégorie:Géographie",
    ],
    "svt": [
        "Catégorie:Biologie",
        "Catégorie:Géologie",
    ],
    "physique_chimie": [
        "Catégorie:Physique",
        "Catégorie:Chimie",
    ],
    "technologie": [
        "Catégorie:Technologie",
    ],
    "anglais": [
        "Catégorie:Anglais",
    ],
    "espagnol": [
        "Catégorie:Espagnol",
    ],
}

# Catégories à ignorer lors du crawl récursif (pas pertinentes pour le collège)
CATEGORIES_IGNOREES = {
    "Catégorie:Ébauche mathématiques",
    "Catégorie:Image mathématiques",
    "Catégorie:Quiz mathématiques",
    "Catégorie:Livre de mathématiques",
    "Catégorie:Instrument de mathématiques",
    "Catégorie:Mathématicien",
    "Catégorie:Historien",
    "Catégorie:Généalogie",
    "Catégorie:Géographe",
    "Catégorie:Faune",
    "Catégorie:Forme de végétation",
    "Catégorie:Salonnière",
    "Catégorie:Médecine comme source d'inspiration littéraire",
    "Catégorie:Critique littéraire",
    "Catégorie:Prix littéraire",
    "Catégorie:Écriture expérimentale",
    "Catégorie:Littérature musulmane",
    "Catégorie:Sherlock Holmes",
    # Sciences
    "Catégorie:Image biologie",
    "Catégorie:Modèle biologie",
    "Catégorie:Biologiste",
    "Catégorie:Image physique",
    "Catégorie:Ébauche physique",
    "Catégorie:Histoire de la physique",
    "Catégorie:Physicien",
    "Catégorie:Image chimie",
    "Catégorie:Chimiste",
    "Catégorie:Image géologie",
    "Catégorie:Ébauche géologie",
    "Catégorie:Image technologie",
    "Catégorie:Ébauche technologie",
    "Catégorie:Cosmologie",
    "Catégorie:Astronomie",
}


def determiner_matiere(categorie: str) -> str:
    """Détermine la matière à partir de la catégorie source.

    Args:
        categorie: Nom de la catégorie Vikidia (ex: "Catégorie:Mathématiques").

    Returns:
        Identifiant de la matière (ex: "mathematiques").
    """
    return CATEGORIES_MATIERES.get(categorie, "autre")


def creer_metadata(
    source: str,
    matiere: str,
    titre: str,
    url: str,
    categorie: str = "",
    niveau: str = "college",
) -> dict:
    """Crée le dictionnaire de métadonnées pour un chunk.

    Args:
        source: Identifiant de la source (vikidia, wikiversite, eduscol).
        matiere: Identifiant de la matière.
        titre: Titre de la page source.
        url: URL de la page source.
        categorie: Catégorie d'origine.
        niveau: Niveau scolaire (défaut: "college").

    Returns:
        Dictionnaire de métadonnées.
    """
    return {
        "source": source,
        "matiere": matiere,
        "niveau": niveau,
        "titre": titre,
        "url": url,
        "categorie": categorie,
    }


def est_categorie_ignoree(categorie: str) -> bool:
    """Vérifie si une catégorie doit être ignorée lors du crawl."""
    return categorie in CATEGORIES_IGNOREES
