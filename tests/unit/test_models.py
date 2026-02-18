"""Tests unitaires pour les modèles Pydantic."""

import pytest
from pydantic import ValidationError
from backend.models.requests import ChatRequest
from backend.models.responses import ChatResponse, HealthResponse


class TestChatRequest:
    """Tests du modèle ChatRequest."""

    def test_chat_request_valid_full(self):
        """Requête complète valide."""
        req = ChatRequest(
            question="C'est quoi Pythagore ?",
            niveau="4eme",
            matiere="mathematiques"
        )
        assert req.question == "C'est quoi Pythagore ?"
        assert req.niveau == "4eme"
        assert req.matiere == "mathematiques"

    def test_chat_request_minimal(self):
        """Requête minimale (seulement question)."""
        req = ChatRequest(question="Test question")
        assert req.question == "Test question"
        assert req.niveau == "college"  # Valeur par défaut
        assert req.matiere is None  # Optionnel

    def test_chat_request_empty_question_fails(self):
        """Question vide doit échouer (min_length=1)."""
        with pytest.raises(ValidationError):
            ChatRequest(question="")

    def test_chat_request_missing_question_fails(self):
        """Question manquante doit échouer."""
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_request_with_niveau_only(self):
        """Requête avec question et niveau uniquement."""
        req = ChatRequest(question="Question test", niveau="6eme")
        assert req.question == "Question test"
        assert req.niveau == "6eme"
        assert req.matiere is None

    def test_chat_request_with_matiere_only(self):
        """Requête avec question et matière uniquement."""
        req = ChatRequest(question="Question test", matiere="svt")
        assert req.question == "Question test"
        assert req.niveau == "college"
        assert req.matiere == "svt"

    def test_chat_request_long_question(self):
        """Longue question doit être acceptée."""
        long_question = "Pouvez-vous m'expliquer en détail " * 20
        req = ChatRequest(question=long_question)
        assert len(req.question) > 100


class TestChatResponse:
    """Tests du modèle ChatResponse."""

    def test_chat_response_valid_full(self):
        """Réponse complète valide."""
        resp = ChatResponse(
            answer="Voici la réponse",
            sources=[{"titre": "Leçon 1", "url": "http://test.com"}],
            nb_sources=1
        )
        assert resp.answer == "Voici la réponse"
        assert len(resp.sources) == 1
        assert resp.nb_sources == 1

    def test_chat_response_empty_sources(self):
        """Réponse sans sources (liste vide)."""
        resp = ChatResponse(
            answer="Réponse sans source",
            sources=[],
            nb_sources=0
        )
        assert resp.answer == "Réponse sans source"
        assert resp.sources == []
        assert resp.nb_sources == 0

    def test_chat_response_missing_answer_fails(self):
        """Answer manquant doit échouer."""
        with pytest.raises(ValidationError):
            ChatResponse(sources=[], nb_sources=0)

    def test_chat_response_missing_nb_sources_fails(self):
        """nb_sources manquant doit échouer."""
        with pytest.raises(ValidationError):
            ChatResponse(answer="Test", sources=[])

    def test_chat_response_default_sources(self):
        """Sources par défaut doit être liste vide."""
        resp = ChatResponse(answer="Test", nb_sources=0)
        assert resp.sources == []

    def test_chat_response_multiple_sources(self):
        """Réponse avec plusieurs sources."""
        sources = [
            {"titre": "Source 1", "url": "http://1.com"},
            {"titre": "Source 2", "url": "http://2.com"},
            {"titre": "Source 3", "url": "http://3.com"},
        ]
        resp = ChatResponse(answer="Test", sources=sources, nb_sources=3)
        assert len(resp.sources) == 3
        assert resp.nb_sources == 3


class TestHealthResponse:
    """Tests du modèle HealthResponse."""

    def test_health_response_valid(self):
        """Réponse health check valide."""
        resp = HealthResponse(status="healthy", message="API opérationnelle")
        assert resp.status == "healthy"
        assert resp.message == "API opérationnelle"

    def test_health_response_unhealthy(self):
        """Réponse unhealthy."""
        resp = HealthResponse(status="unhealthy", message="Erreur")
        assert resp.status == "unhealthy"
        assert resp.message == "Erreur"

    def test_health_response_missing_status_fails(self):
        """Status manquant doit échouer."""
        with pytest.raises(ValidationError):
            HealthResponse(message="Test")

    def test_health_response_missing_message_fails(self):
        """Message manquant doit échouer."""
        with pytest.raises(ValidationError):
            HealthResponse(status="healthy")
