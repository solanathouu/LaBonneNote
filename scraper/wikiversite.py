"""Scraper Wikiversité via l'API MediaWiki.

Collecte les leçons structurées par niveau depuis fr.wikiversity.org.
Extrait automatiquement les niveaux et matières depuis les catégories.
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional

import cloudscraper
import requests

from .metadata import creer_metadata

logger = logging.getLogger(__name__)

API_URL = "https://fr.wikiversity.org/w/api.php"
BASE_URL = "https://fr.wikiversity.org/wiki/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 "
    "ChatbotScolaireRAG/1.0 (educational project)"
)
DELAI_REQUETE = 1.0  # secondes entre chaque requête

# Mapping niveau Wikiversité → niveau scolaire français
# Basé sur l'analyse: Pythagore=niveau 9 (4ème), Fraction=niveau 8 (6ème)
NIVEAU_MAPPING = {
    7: "6eme",
    8: "6eme",
    9: "5eme",
    10: "4eme",
    11: "3eme",
    12: "3eme",
    13: "3eme",  # Peut aussi être 2nde, on garde 3ème
}

# Niveaux à scraper (collège)
NIVEAUX_COLLEGE = [7, 8, 9, 10, 11, 12, 13]

# Mapping catégorie faculté → matière
FACULTES_MATIERES = {
    "mathématiques": "mathematiques",
    "français": "francais",
    "histoire": "histoire_geo",
    "géographie": "histoire_geo",
    "physique": "physique_chimie",
    "chimie": "physique_chimie",
    "biologie": "svt",
    "géologie": "svt",
    "sciences de la vie et de la terre": "svt",
    "technologie": "technologie",
    "anglais": "anglais",
    "espagnol": "espagnol",
}


class WikiversiteScraper:
    """Scraper pour les leçons Wikiversité via l'API MediaWiki."""

    def __init__(self, dossier_sortie: str = "data/raw/wikiversite"):
        self.dossier_sortie = Path(dossier_sortie)
        self.dossier_sortie.mkdir(parents=True, exist_ok=True)
        self.session = cloudscraper.create_scraper()
        self.lecons_vues: set[str] = set()  # éviter les doublons
        # Compteurs de progression
        self._lecons_ok = 0
        self._lecons_skip = 0
        self._lecons_err = 0
        self._niveaux_traites = 0
        self._derniere_progression = time.time()

    def _afficher_progression(self, force: bool = False) -> None:
        """Affiche la progression toutes les 10 secondes ou si force=True."""
        now = time.time()
        if not force and (now - self._derniere_progression) < 10:
            return
        self._derniere_progression = now
        total = self._lecons_ok + self._lecons_skip + self._lecons_err
        logger.info(
            "[PROGRESSION] %d niveaux | %d lecons extraites | "
            "%d ignorees | %d erreurs | %d total traitees",
            self._niveaux_traites,
            self._lecons_ok,
            self._lecons_skip,
            self._lecons_err,
            total,
        )

    def scraper_tout(self) -> list[dict]:
        """Scrape tous les niveaux collège configurés.

        Returns:
            Liste de toutes les leçons scrapées (dict avec 'titre', 'texte', 'metadata').
        """
        toutes_lecons = []

        for niveau_wv in NIVEAUX_COLLEGE:
            logger.info("========================================")
            logger.info("=== Scraping niveau Wikiversité: %d ===", niveau_wv)
            logger.info("========================================")

            lecons_niveau = self._scraper_niveau(niveau_wv)
            toutes_lecons.extend(lecons_niveau)

            logger.info(
                "[RESULTAT] Niveau %d: %d lecons scrapees",
                niveau_wv,
                len(lecons_niveau),
            )

        # Sauvegarder toutes les leçons
        self._sauvegarder(toutes_lecons, "toutes_lecons")
        logger.info("========================================")
        logger.info("[TERMINE] Total: %d lecons scrapees", len(toutes_lecons))
        self._afficher_progression(force=True)
        return toutes_lecons

    def scraper_niveau(self, niveau_wv: int) -> list[dict]:
        """Scrape un seul niveau Wikiversité.

        Args:
            niveau_wv: Numéro du niveau Wikiversité (7-13 pour collège).

        Returns:
            Liste des leçons scrapées.
        """
        if niveau_wv not in NIVEAUX_COLLEGE:
            logger.error("Niveau invalide: %d (attendu: 7-13)", niveau_wv)
            return []

        lecons = self._scraper_niveau(niveau_wv)
        self._sauvegarder(lecons, f"niveau_{niveau_wv}")
        logger.info("[RESULTAT] Niveau %d: %d lecons scrapees", niveau_wv, len(lecons))
        self._afficher_progression(force=True)
        return lecons

    def _scraper_niveau(self, niveau_wv: int) -> list[dict]:
        """Scrape toutes les leçons d'un niveau.

        Args:
            niveau_wv: Numéro du niveau Wikiversité.

        Returns:
            Liste des leçons scrapées.
        """
        self._niveaux_traites += 1
        categorie = f"Catégorie:Leçons de niveau {niveau_wv}"
        niveau_scolaire = NIVEAU_MAPPING.get(niveau_wv, "college")

        logger.info("Niveau %d → %s", niveau_wv, niveau_scolaire)

        # Lister toutes les leçons de ce niveau
        titres_lecons = self._lister_lecons_niveau(categorie)
        logger.info("  -> %d lecons trouvees", len(titres_lecons))

        lecons = []
        for i, titre in enumerate(titres_lecons):
            if titre in self.lecons_vues:
                self._lecons_skip += 1
                continue
            self.lecons_vues.add(titre)

            lecon = self._extraire_lecon(titre, niveau_scolaire, niveau_wv)
            if lecon:
                lecons.append(lecon)
                self._lecons_ok += 1
            else:
                self._lecons_skip += 1

            self._afficher_progression()

        return lecons

    def _lister_lecons_niveau(self, categorie: str) -> list[str]:
        """Liste les leçons d'une catégorie de niveau.

        Args:
            categorie: Nom de la catégorie (ex: "Catégorie:Leçons de niveau 9").

        Returns:
            Liste des titres de leçons.
        """
        titres = []
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": categorie,
            "cmtype": "page",  # Uniquement les pages (pas les sous-catégories)
            "cmlimit": "50",
            "format": "json",
        }

        while True:
            time.sleep(DELAI_REQUETE)
            try:
                response = self.session.get(API_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except (requests.RequestException, json.JSONDecodeError) as e:
                logger.error("Erreur API pour categorie %s: %s", categorie, e)
                self._lecons_err += 1
                break

            membres = data.get("query", {}).get("categorymembers", [])
            for membre in membres:
                # Filtrer les pages de leçons (namespace 0)
                if membre.get("ns") == 0:
                    titres.append(membre["title"])

            # Pagination
            if "continue" in data:
                params["cmcontinue"] = data["continue"]["cmcontinue"]
            else:
                break

        return titres

    def _extraire_lecon(
        self, titre: str, niveau_scolaire: str, niveau_wv: int
    ) -> Optional[dict]:
        """Extrait le contenu texte d'une leçon Wikiversité.

        Args:
            titre: Titre de la leçon.
            niveau_scolaire: Niveau scolaire français (6eme, 5eme, etc.).
            niveau_wv: Niveau Wikiversité original.

        Returns:
            Dict avec 'titre', 'texte', 'url', 'metadata' ou None si échec.
        """
        # 1. Récupérer le contenu texte
        params = {
            "action": "query",
            "prop": "extracts|categories",
            "explaintext": "1",
            "redirects": "1",
            "titles": titre,
            "cllimit": "100",
            "format": "json",
        }

        time.sleep(DELAI_REQUETE)
        try:
            response = self.session.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error("[ERREUR] Lecon '%s': %s", titre, e)
            self._lecons_err += 1
            return None

        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            # Pages inexistantes ont un id négatif
            if int(page_id) < 0:
                logger.debug("Page inexistante: %s", titre)
                return None

            extrait = page.get("extract", "")
            titre_reel = page.get("title", titre)
            categories = page.get("categories", [])

            if not extrait or len(extrait.strip()) < 50:
                logger.debug("Lecon trop courte ou vide: %s", titre_reel)
                return None

            # 2. Déterminer la matière depuis les catégories
            matiere = self._detecter_matiere(categories)

            # 3. Créer les métadonnées
            url = BASE_URL + titre_reel.replace(" ", "_")
            metadata = creer_metadata(
                source="wikiversite",
                matiere=matiere,
                titre=titre_reel,
                url=url,
                categorie=f"Niveau {niveau_wv}",
                niveau=niveau_scolaire,
            )
            # Ajouter le niveau Wikiversité original pour référence
            metadata["niveau_wikiversite"] = niveau_wv

            logger.debug(
                "Lecon extraite: %s [%s - %s] (%d chars)",
                titre_reel,
                matiere,
                niveau_scolaire,
                len(extrait),
            )
            return {
                "titre": titre_reel,
                "texte": extrait,
                "url": url,
                "metadata": metadata,
            }

        return None

    def _detecter_matiere(self, categories: list[dict]) -> str:
        """Détecte la matière depuis les catégories de la page.

        Args:
            categories: Liste des catégories de la page.

        Returns:
            Identifiant de la matière (ex: "mathematiques") ou "autre".
        """
        for cat in categories:
            cat_title = cat["title"].lower()

            # Chercher "Leçons de la faculté X"
            if "leçons de la faculté" in cat_title or "lecons de la faculte" in cat_title:
                for faculte, matiere in FACULTES_MATIERES.items():
                    if faculte in cat_title:
                        return matiere

            # Fallback: chercher directement les noms de matières
            for faculte, matiere in FACULTES_MATIERES.items():
                if faculte in cat_title:
                    return matiere

        return "autre"

    def _sauvegarder(self, lecons: list[dict], nom_fichier: str) -> None:
        """Sauvegarde les leçons brutes en JSON.

        Args:
            lecons: Liste des leçons à sauvegarder.
            nom_fichier: Nom de base du fichier (sans extension).
        """
        if not lecons:
            return

        fichier = self.dossier_sortie / f"{nom_fichier}.json"
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(lecons, f, ensure_ascii=False, indent=2)

        logger.info("[SAUVEGARDE] %d lecons -> %s", len(lecons), fichier)
