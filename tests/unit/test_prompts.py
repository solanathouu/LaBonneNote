"""Tests unitaires pour backend/prompts.py."""

import pytest
from backend.prompts import get_prompt, REFUS_MESSAGE, SYSTEM_PROMPT_BASE, PROMPTS_PAR_NIVEAU


class TestGetPrompt:
    """Tests génération de prompts."""

    def test_get_prompt_6eme_simple(self):
        """Prompt pour 6ème doit contenir vocabulaire simple."""
        prompt = get_prompt("C'est quoi une fraction ?", "Contexte test", "6eme")
        assert "6ème" in prompt or "6eme" in prompt
        assert "vocabulaire simple" in prompt.lower()
        assert "Contexte test" in prompt
        assert "C'est quoi une fraction ?" in prompt

    def test_get_prompt_3eme_academique(self):
        """Prompt pour 3ème doit contenir vocabulaire académique."""
        prompt = get_prompt("Fonction affine", "f(x) = ax + b", "3eme")
        assert "3ème" in prompt or "3eme" in prompt or "brevet" in prompt.lower()
        assert "vocabulaire académique" in prompt.lower() or "académique" in prompt.lower()
        assert "f(x) = ax + b" in prompt

    def test_get_prompt_college_default(self):
        """Prompt pour 'college' doit être générique."""
        prompt = get_prompt("Question test", "Contexte", "college")
        assert "collège" in prompt.lower() or "college" in prompt.lower()
        assert "Contexte" in prompt

    def test_get_prompt_invalid_niveau_fallback(self):
        """Niveau invalide doit fallback sur 'college'."""
        prompt = get_prompt("Question", "Contexte", "invalid_niveau")
        # Doit utiliser le prompt "college" par défaut
        assert "collège" in prompt.lower() or "college" in prompt.lower()

    @pytest.mark.parametrize("niveau", ["6eme", "5eme", "4eme", "3eme", "college"])
    def test_get_prompt_all_levels(self, niveau):
        """Vérifier que tous les niveaux génèrent des prompts valides."""
        prompt = get_prompt("Question test", "Contexte test", niveau)
        assert len(prompt) > 100
        assert "Contexte test" in prompt
        assert "Question test" in prompt

    def test_get_prompt_contains_rules(self):
        """Vérifier que le prompt contient les règles strictes."""
        prompt = get_prompt("Question", "Contexte", "college")
        assert "RÈGLES STRICTES" in prompt or "uniquement" in prompt.lower()

    def test_get_prompt_context_injection(self):
        """Vérifier que le contexte est bien injecté."""
        context = "Ceci est un contexte très spécifique avec des données uniques 12345"
        prompt = get_prompt("Question", context, "6eme")
        assert "très spécifique" in prompt
        assert "12345" in prompt

    def test_get_prompt_question_injection(self):
        """Vérifier que la question est bien injectée."""
        question = "Question très spécifique sur un sujet unique 98765"
        prompt = get_prompt(question, "Contexte", "4eme")
        assert "très spécifique" in prompt
        assert "98765" in prompt

    def test_get_prompt_6eme_vs_3eme_different(self):
        """Prompts 6ème et 3ème doivent être différents."""
        prompt_6eme = get_prompt("Question", "Contexte", "6eme")
        prompt_3eme = get_prompt("Question", "Contexte", "3eme")
        assert prompt_6eme != prompt_3eme

    def test_get_prompt_no_niveau_uses_default(self):
        """Sans niveau spécifié, doit utiliser 'college'."""
        prompt_default = get_prompt("Question", "Contexte")
        prompt_college = get_prompt("Question", "Contexte", "college")
        assert prompt_default == prompt_college


class TestRefusMessage:
    """Tests message de refus."""

    def test_refus_message_contains_matieres(self):
        """Message de refus doit lister les matières."""
        assert "Mathématiques" in REFUS_MESSAGE
        assert "Français" in REFUS_MESSAGE
        assert "Histoire-Géographie" in REFUS_MESSAGE
        assert "SVT" in REFUS_MESSAGE
        assert "Physique-Chimie" in REFUS_MESSAGE
        assert "Technologie" in REFUS_MESSAGE

    def test_refus_message_polite(self):
        """Message de refus doit être poli."""
        assert "désolé" in REFUS_MESSAGE.lower() or "sorry" in REFUS_MESSAGE.lower()

    def test_refus_message_not_empty(self):
        """Message de refus ne doit pas être vide."""
        assert len(REFUS_MESSAGE) > 50

    def test_refus_message_suggests_reformulation(self):
        """Message de refus doit suggérer de reformuler."""
        assert "reformuler" in REFUS_MESSAGE.lower() or "poser une question" in REFUS_MESSAGE.lower()


class TestPromptsConstants:
    """Tests des constantes de prompts."""

    def test_system_prompt_base_exists(self):
        """SYSTEM_PROMPT_BASE doit exister."""
        assert SYSTEM_PROMPT_BASE is not None
        assert len(SYSTEM_PROMPT_BASE) > 50

    def test_system_prompt_has_placeholders(self):
        """SYSTEM_PROMPT_BASE doit avoir des placeholders."""
        assert "{context}" in SYSTEM_PROMPT_BASE
        assert "{question}" in SYSTEM_PROMPT_BASE

    def test_prompts_par_niveau_all_levels(self):
        """PROMPTS_PAR_NIVEAU doit contenir tous les niveaux."""
        expected_levels = ["6eme", "5eme", "4eme", "3eme", "college"]
        for level in expected_levels:
            assert level in PROMPTS_PAR_NIVEAU

    def test_prompts_par_niveau_have_base_prompt_placeholder(self):
        """Tous les prompts par niveau doivent avoir {base_prompt}."""
        for level, prompt_template in PROMPTS_PAR_NIVEAU.items():
            assert "{base_prompt}" in prompt_template, f"Niveau {level} manque {{base_prompt}}"
