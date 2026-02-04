"""Nettoyage du texte brut extrait des APIs MediaWiki et du scraping HTML."""

import re
import logging

logger = logging.getLogger(__name__)

# Sections wiki à supprimer (non pertinentes pour l'apprentissage)
SECTIONS_A_SUPPRIMER = [
    "Voir aussi",
    "voir aussi",
    "Liens externes",
    "liens externes",
    "Références",
    "références",
    "Notes et références",
    "notes et références",
    "Notes",
    "notes",
    "Bibliographie",
    "bibliographie",
    "Sources",
    "sources",
    "Liens internes",
    "liens internes",
    "Articles connexes",
    "articles connexes",
    "Lien externe",
    "lien externe",
]

# Pattern LaTeX courants dans les extraits MediaWiki
LATEX_PATTERNS = [
    r"\{\\displaystyle[^}]*\}",
    r"\{\\scriptstyle[^}]*\}",
    r"\{\\textstyle[^}]*\}",
    r"\\displaystyle\s*",
    r"\\scriptstyle\s*",
    r"\\textstyle\s*",
    r"\\frac\{[^}]*\}\{[^}]*\}",
    r"\\(?:left|right)[(\[\{)\]\}]",
    r"\\(?:times|cdot|pm|mp|leq|geq|neq|approx|equiv|sim)",
    r"\\(?:alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega|phi|psi)",
    r"\\(?:sum|prod|int|lim|inf|sup|max|min|log|ln|sin|cos|tan)",
    r"\\(?:mathbb|mathrm|mathbf|mathcal|mathit)\{[^}]*\}",
    r"\\(?:text|mbox)\{[^}]*\}",
    r"\\(?:overline|underline|hat|tilde|vec|bar)\{[^}]*\}",
    r"\\[a-zA-Z]+",  # catch-all pour les commandes LaTeX restantes
]


def nettoyer_texte(texte: str) -> str:
    """Nettoie le texte brut extrait d'une page wiki.

    Args:
        texte: Texte brut extrait via l'API MediaWiki (explaintext).

    Returns:
        Texte nettoyé prêt pour le chunking.
    """
    if not texte:
        return ""

    # Supprimer les sections non pertinentes
    texte = _supprimer_sections(texte)

    # Nettoyer le LaTeX
    texte = _nettoyer_latex(texte)

    # Supprimer les marqueurs wiki résiduels
    texte = _nettoyer_wiki(texte)

    # Normaliser les espaces
    texte = _normaliser_espaces(texte)

    return texte.strip()


def _supprimer_sections(texte: str) -> str:
    """Supprime les sections non pertinentes (Voir aussi, Références, etc.)."""
    for section in SECTIONS_A_SUPPRIMER:
        # Trouver la section et supprimer tout jusqu'à la prochaine section de même niveau ou fin
        pattern = rf"==+\s*{re.escape(section)}\s*==+.*?(?===|\Z)"
        texte = re.sub(pattern, "", texte, flags=re.DOTALL | re.IGNORECASE)
    return texte


def _nettoyer_latex(texte: str) -> str:
    """Supprime les fragments LaTeX des extraits MediaWiki."""
    for pattern in LATEX_PATTERNS:
        texte = re.sub(pattern, " ", texte)

    # Supprimer les accolades orphelines laissées par le nettoyage LaTeX
    texte = re.sub(r"\{[\s,]*\}", "", texte)
    texte = re.sub(r"\{\s*\{", "", texte)
    texte = re.sub(r"\}\s*\}", "", texte)

    return texte


def _nettoyer_wiki(texte: str) -> str:
    """Supprime les marqueurs wiki résiduels."""
    # Supprimer les titres de sections (== Titre ==) mais garder le texte
    texte = re.sub(r"={2,}\s*(.+?)\s*={2,}", r"\n\1\n", texte)

    # Supprimer les balises HTML résiduelles
    texte = re.sub(r"<[^>]+>", "", texte)

    # Supprimer les modèles wiki {{...}}
    texte = re.sub(r"\{\{[^}]*\}\}", "", texte)

    # Supprimer les crochets de liens internes [[...]] en gardant le texte affiché
    texte = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", texte)

    # Supprimer les crochets de liens externes [http... texte]
    texte = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", texte)
    texte = re.sub(r"\[https?://\S+\]", "", texte)

    # Supprimer les puces wiki
    texte = re.sub(r"^\*+\s*", "- ", texte, flags=re.MULTILINE)

    return texte


def _normaliser_espaces(texte: str) -> str:
    """Normalise les espaces et les sauts de ligne."""
    # Remplacer les espaces multiples par un seul
    texte = re.sub(r"[ \t]+", " ", texte)

    # Remplacer 3+ sauts de ligne par 2
    texte = re.sub(r"\n{3,}", "\n\n", texte)

    # Supprimer les espaces en début/fin de ligne
    texte = re.sub(r"^ +| +$", "", texte, flags=re.MULTILINE)

    return texte
