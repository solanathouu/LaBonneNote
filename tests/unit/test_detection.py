"""Tests unitaires pour backend/detection.py."""

import pytest
from backend.detection import detect_matiere, detect_niveau, auto_detect


class TestDetectMatiere:
    """Tests détection de matière par mots-clés."""

    def test_detect_matiere_mathematiques_clear(self):
        """Cas clair : 'théorème' → mathematiques."""
        result = detect_matiere("C'est quoi le théorème de Pythagore ?")
        assert result["matiere_principale"] == "mathematiques"
        assert len(result["matieres_possibles"]) == 0

    def test_detect_matiere_histoire_clear(self):
        """Cas clair : 'révolution' → histoire_geo."""
        result = detect_matiere("Quand a commencé la Révolution française ?")
        assert result["matiere_principale"] == "histoire_geo"
        # Peut avoir ambiguïté si scores proches
        assert "histoire_geo" in [result["matiere_principale"]] + result.get("matieres_possibles", [])

    def test_detect_matiere_ambigue(self):
        """Cas ambigu : 'énergie' → physique OU svt."""
        result = detect_matiere("Explique l'énergie chaleur température")
        # Plusieurs mots-clés physique/chimie
        assert result["matiere_principale"] in ["physique_chimie", "svt", "technologie"]

    def test_detect_matiere_hors_perimetre(self):
        """Hors-périmètre : aucun mot-clé."""
        result = detect_matiere("Quelle est la météo aujourd'hui ?")
        assert result["matiere_principale"] is None
        assert all(score == 0 for score in result["scores"].values())

    def test_detect_matiere_case_insensitive(self):
        """Vérifier que la détection est insensible à la casse."""
        result1 = detect_matiere("THÉORÈME DE PYTHAGORE")
        result2 = detect_matiere("théorème de pythagore")
        assert result1["matiere_principale"] == result2["matiere_principale"]

    def test_detect_matiere_multiple_keywords(self):
        """Plusieurs mots-clés de la même matière augmentent le score."""
        result = detect_matiere("Calcul de l'aire d'un triangle rectangle")
        assert result["matiere_principale"] == "mathematiques"
        assert result["scores"]["mathematiques"] >= 2  # "calcul", "aire", "triangle"

    @pytest.mark.parametrize("question,expected", [
        ("théorème pythagore", "mathematiques"),
        ("verbe conjugaison", "francais"),
        ("cellule adn", "svt"),
        ("circuit électrique", "physique_chimie"),
        ("continent océan", "histoire_geo"),
        ("ordinateur robot", "technologie"),
    ])
    def test_detect_matiere_parametrize(self, question, expected):
        """Tests paramétrés : plusieurs matières."""
        result = detect_matiere(question)
        assert result["matiere_principale"] == expected

    def test_detect_matiere_scores_dict(self):
        """Vérifier que les scores sont retournés."""
        result = detect_matiere("théorème")
        assert "scores" in result
        assert isinstance(result["scores"], dict)
        assert len(result["scores"]) == 8  # 8 matières

    def test_detect_matiere_ambigue_equal_scores(self):
        """Cas d'ambiguïté avec scores égaux."""
        # Mot présent dans exactement 2 matières avec même fréquence
        result = detect_matiere("structure")  # Peut être en techno ou autres
        if len(result["matieres_possibles"]) > 1:
            # Vérifier que les scores sont effectivement proches
            top_score = result["scores"][result["matieres_possibles"][0]]
            second_score = result["scores"][result["matieres_possibles"][1]]
            assert abs(top_score - second_score) <= 1


class TestDetectNiveau:
    """Tests détection de niveau."""

    def test_detect_niveau_explicit_6eme(self):
        """Niveau explicite : '6ème'."""
        assert detect_niveau("Question de 6ème") == "6eme"

    def test_detect_niveau_explicit_5eme(self):
        """Niveau explicite : '5ème'."""
        assert detect_niveau("Cours de 5ème") == "5eme"

    def test_detect_niveau_explicit_4eme(self):
        """Niveau explicite : '4ème'."""
        assert detect_niveau("Exercice de 4ème") == "4eme"

    def test_detect_niveau_explicit_3eme(self):
        """Niveau explicite : '3ème'."""
        assert detect_niveau("Révision de 3ème") == "3eme"

    def test_detect_niveau_brevet(self):
        """Mot-clé 'brevet' → 3eme."""
        assert detect_niveau("Question pour le brevet") == "3eme"

    def test_detect_niveau_sixieme_word(self):
        """Niveau avec mot complet 'sixième'."""
        assert detect_niveau("Cours de sixième") == "6eme"

    @pytest.mark.parametrize("question,expected", [
        ("6ème", "6eme"),
        ("5ème", "5eme"),
        ("4ème", "4eme"),
        ("3ème", "3eme"),
        ("sixième", "6eme"),
        ("cinquième", "5eme"),
        ("quatrième", "4eme"),
        ("troisième", "3eme"),
        ("brevet", "3eme"),
    ])
    def test_detect_niveau_all_explicit(self, question, expected):
        """Tests paramétrés : tous les niveaux explicites."""
        assert detect_niveau(question) == expected

    def test_detect_niveau_heuristic_simple(self):
        """Heuristique : question courte → 6eme."""
        result = detect_niveau("C'est quoi ?")
        assert result in ["6eme", "5eme"]  # Question très simple

    def test_detect_niveau_heuristic_complex(self):
        """Heuristique : question complexe → niveaux supérieurs."""
        result = detect_niveau(
            "Pouvez-vous analyser en profondeur les mécanismes sous-jacents "
            "de ce phénomène complexe en utilisant des concepts avancés ?"
        )
        assert result in ["4eme", "3eme"]

    def test_detect_niveau_no_explicit_returns_default(self):
        """Sans indication explicite, retourne un niveau par heuristique."""
        result = detect_niveau("Explique moi")
        assert result in ["6eme", "5eme", "4eme", "3eme"]


class TestAutoDetect:
    """Tests pipeline complet auto_detect."""

    def test_auto_detect_full(self):
        """Pipeline complet avec niveau et matière explicites."""
        result = auto_detect("C'est quoi Pythagore en 4ème ?")
        assert result["niveau_detecte"] == "4eme"
        assert result["matiere_detectee"] == "mathematiques"
        assert not result["ambigue"]

    def test_auto_detect_ambigue(self):
        """Détection avec ambiguïté de matière."""
        result = auto_detect("Explique l'énergie")
        # "énergie" est dans plusieurs matières
        if result["ambigue"]:
            assert len(result["matieres_possibles"]) >= 2

    def test_auto_detect_hors_perimetre(self):
        """Question hors périmètre."""
        result = auto_detect("Quelle est la météo ?")
        assert result["matiere_detectee"] is None
        assert not result["ambigue"]

    def test_auto_detect_structure(self):
        """Vérifier la structure du retour."""
        result = auto_detect("Question test")
        assert "niveau_detecte" in result
        assert "matiere_detectee" in result
        assert "matieres_possibles" in result
        assert "ambigue" in result
        assert "scores" in result

    def test_auto_detect_matiere_claire(self):
        """Matière claire, pas d'ambiguïté."""
        result = auto_detect("Théorème de Pythagore")
        assert result["matiere_detectee"] == "mathematiques"
        assert not result["ambigue"]
        assert len(result["matieres_possibles"]) <= 1
