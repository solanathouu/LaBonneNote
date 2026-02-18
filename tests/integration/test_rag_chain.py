"""Tests d'intégration pour backend/rag.py avec mocks."""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document


class TestRAGChainInit:
    """Tests initialisation RAGChain."""

    def test_ragchain_init_success(self, rag_chain_mocked):
        """RAGChain s'initialise correctement avec mocks."""
        assert rag_chain_mocked is not None
        assert hasattr(rag_chain_mocked, 'vector_store')
        assert hasattr(rag_chain_mocked, 'llm')
        assert rag_chain_mocked.top_k == 5

    def test_ragchain_init_custom_params(self, mock_vector_store, mock_openai_embeddings, mock_openai_llm):
        """Initialisation avec paramètres personnalisés."""
        with patch('backend.services.rag_chain.Chroma', return_value=mock_vector_store):
            with patch('backend.services.rag_chain.OpenAIEmbeddings', return_value=mock_openai_embeddings):
                with patch('backend.services.rag_chain.ChatOpenAI', return_value=mock_openai_llm):
                    from backend.services.rag_chain import RAGChain

                    chain = RAGChain(
                        chroma_dir="custom_dir",
                        top_k=10,
                        similarity_threshold=0.5
                    )

                    assert chain.top_k == 10
                    assert chain.similarity_threshold == 0.5


class TestRAGChainRetrieve:
    """Tests retrieve()."""

    def test_retrieve_no_filter(self, rag_chain_mocked):
        """Retrieve sans filtres."""
        docs = rag_chain_mocked.retrieve("théorème pythagore")

        assert isinstance(docs, list)
        assert len(docs) <= 5
        assert all(isinstance(doc, Document) for doc in docs)

    def test_retrieve_with_matiere_filter(self, rag_chain_mocked):
        """Retrieve avec filtre matière."""
        docs = rag_chain_mocked.retrieve("pythagore", matiere="mathematiques")

        # Vérifier que le mock a été appelé avec le filtre
        rag_chain_mocked.vector_store.similarity_search_with_score.assert_called_once()
        call_kwargs = rag_chain_mocked.vector_store.similarity_search_with_score.call_args[1]
        assert call_kwargs["filter"]["matiere"] == "mathematiques"

    def test_retrieve_with_niveau_filter(self, rag_chain_mocked):
        """Retrieve avec filtre niveau (ignoré car pas implémenté)."""
        docs = rag_chain_mocked.retrieve("pythagore", niveau="4eme")

        # Niveau est ignoré dans l'implémentation actuelle
        assert isinstance(docs, list)

    def test_retrieve_empty_results(self, rag_chain_mocked):
        """Retrieve sans résultats."""
        # Override the mock pour retourner rien
        def mock_empty_search(query, k=5, filter=None):
            return []

        rag_chain_mocked.vector_store.similarity_search_with_score = MagicMock(side_effect=mock_empty_search)
        docs = rag_chain_mocked.retrieve("hors sujet xyz123")

        assert docs == []

    def test_retrieve_filters_both(self, rag_chain_mocked):
        """Retrieve avec matière ET niveau."""
        docs = rag_chain_mocked.retrieve("pythagore", matiere="mathematiques", niveau="4eme")

        assert isinstance(docs, list)

    def test_retrieve_returns_documents_with_metadata(self, rag_chain_mocked):
        """Documents retournés contiennent des métadonnées."""
        docs = rag_chain_mocked.retrieve("pythagore", matiere="mathematiques")

        if docs:
            doc = docs[0]
            assert hasattr(doc, 'metadata')
            assert hasattr(doc, 'page_content')


class TestRAGChainGenerate:
    """Tests generate()."""

    def test_generate_with_documents(self, rag_chain_mocked):
        """Generate avec documents."""
        docs = [
            Document(
                page_content="Test content",
                metadata={"titre": "Test", "matiere": "mathematiques"}
            )
        ]
        answer = rag_chain_mocked.generate("Question test", docs, "4eme")

        assert isinstance(answer, str)
        assert len(answer) > 0
        rag_chain_mocked.llm.invoke.assert_called_once()

    def test_generate_no_documents_refus(self, rag_chain_mocked):
        """Generate sans documents retourne message de refus."""
        from backend.prompts import REFUS_MESSAGE

        answer = rag_chain_mocked.generate("Question", [], "college")

        assert answer == REFUS_MESSAGE
        # LLM ne doit PAS être appelé
        rag_chain_mocked.llm.invoke.assert_not_called()

    def test_generate_with_multiple_documents(self, rag_chain_mocked):
        """Generate avec plusieurs documents."""
        docs = [
            Document(page_content="Doc 1", metadata={"titre": "Titre 1", "matiere": "math"}),
            Document(page_content="Doc 2", metadata={"titre": "Titre 2", "matiere": "math"}),
        ]
        answer = rag_chain_mocked.generate("Question", docs, "3eme")

        assert isinstance(answer, str)

    def test_generate_niveau_adaptation(self, rag_chain_mocked):
        """Generate adapte le prompt selon le niveau."""
        docs = [Document(page_content="Test", metadata={"titre": "Test", "matiere": "svt"})]

        answer_6eme = rag_chain_mocked.generate("Question", docs, "6eme")
        answer_3eme = rag_chain_mocked.generate("Question", docs, "3eme")

        # Les deux doivent retourner des réponses
        assert isinstance(answer_6eme, str)
        assert isinstance(answer_3eme, str)


class TestRAGChainRun:
    """Tests run() pipeline complet."""

    def test_run_full_pipeline(self, rag_chain_mocked):
        """Pipeline complet retrieve + generate."""
        result = rag_chain_mocked.run("pythagore", "mathematiques", "4eme")

        assert "answer" in result
        assert "sources" in result
        assert "nb_sources" in result
        assert result["nb_sources"] == len(result["sources"])

    def test_run_sources_format(self, rag_chain_mocked):
        """Sources ont le bon format."""
        result = rag_chain_mocked.run("pythagore", "mathematiques", "4eme")

        for source in result["sources"]:
            assert "titre" in source
            assert "url" in source
            assert "matiere" in source
            assert "source" in source

    def test_run_without_matiere(self, rag_chain_mocked):
        """Run sans spécifier de matière."""
        result = rag_chain_mocked.run("Question générale")

        assert "answer" in result
        assert isinstance(result["sources"], list)

    def test_run_with_all_params(self, rag_chain_mocked):
        """Run avec tous les paramètres."""
        result = rag_chain_mocked.run(
            question="Question complète",
            matiere="svt",
            niveau="5eme"
        )

        assert "answer" in result

    def test_run_returns_dict(self, rag_chain_mocked):
        """Run retourne un dictionnaire."""
        result = rag_chain_mocked.run("Test")

        assert isinstance(result, dict)
        assert set(result.keys()) == {"answer", "sources", "nb_sources"}


class TestRAGChainGetAllLessons:
    """Tests get_all_lessons()."""

    def test_get_all_lessons_success(self, rag_chain_mocked):
        """Récupération de toutes les leçons."""
        lessons = rag_chain_mocked.get_all_lessons("mathematiques", None, 100)

        assert isinstance(lessons, list)

    def test_get_all_lessons_with_niveau(self, rag_chain_mocked):
        """Récupération avec filtre niveau."""
        lessons = rag_chain_mocked.get_all_lessons("mathematiques", "4eme", 100)

        assert isinstance(lessons, list)

    def test_get_all_lessons_grouping(self, rag_chain_mocked):
        """Leçons sont groupées par titre (dédupliquées)."""
        # Mock avec doublons - utiliser MagicMock pour override
        mock_results = {
            "ids": ["1", "2", "3"],
            "documents": ["Content A", "Content A2", "Content B"],
            "metadatas": [
                {"titre": "Leçon A", "matiere": "mathematiques", "url": "http://a.com", "niveau": "6eme", "source": "vikidia"},
                {"titre": "Leçon A", "matiere": "mathematiques", "url": "http://a.com", "niveau": "6eme", "source": "vikidia"},
                {"titre": "Leçon B", "matiere": "mathematiques", "url": "http://b.com", "niveau": "6eme", "source": "vikidia"},
            ]
        }

        # Override le mock pour ce test spécifique
        rag_chain_mocked.vector_store._collection.get = MagicMock(return_value=mock_results)

        lessons = rag_chain_mocked.get_all_lessons("mathematiques")

        # Doit grouper par titre
        assert len(lessons) == 2
        titres = [l["titre"] for l in lessons]
        assert "Leçon A" in titres
        assert "Leçon B" in titres

    def test_get_all_lessons_format(self, rag_chain_mocked):
        """Format des leçons retournées."""
        mock_results = {
            "ids": ["1"],
            "documents": ["Contenu test"],
            "metadatas": [{
                "titre": "Test Lesson",
                "matiere": "mathematiques",
                "url": "http://test.com",
                "niveau": "6eme",
                "source": "vikidia"
            }]
        }

        # Override le mock
        rag_chain_mocked.vector_store._collection.get = MagicMock(return_value=mock_results)

        lessons = rag_chain_mocked.get_all_lessons("mathematiques")

        assert len(lessons) == 1
        lesson = lessons[0]
        assert "titre" in lesson
        assert "url" in lesson
        assert "resume" in lesson
        assert "matiere" in lesson
        assert "niveau" in lesson
        assert "source" in lesson
        assert "nb_chunks" in lesson

    def test_get_all_lessons_error_handling(self, rag_chain_mocked):
        """Gestion d'erreur lors de la récupération."""
        rag_chain_mocked.vector_store._collection.get.side_effect = Exception("DB Error")

        lessons = rag_chain_mocked.get_all_lessons("mathematiques")

        assert lessons == []


class TestRAGChainGetLessonContent:
    """Tests get_lesson_content()."""

    def test_get_lesson_content_found(self, rag_chain_mocked):
        """Récupération du contenu d'une leçon."""
        mock_results = {
            "ids": ["1", "2"],
            "documents": ["Chunk 1 content", "Chunk 2 content"],
            "metadatas": [
                {"titre": "Pythagore", "matiere": "mathematiques", "url": "http://test.com", "niveau": "4eme", "source": "vikidia"},
                {"titre": "Pythagore", "matiere": "mathematiques", "url": "http://test.com", "niveau": "4eme", "source": "vikidia"},
            ]
        }

        # Override le mock
        rag_chain_mocked.vector_store._collection.get = MagicMock(return_value=mock_results)

        content = rag_chain_mocked.get_lesson_content("mathematiques", "Pythagore")

        assert content is not None
        assert content["titre"] == "Pythagore"
        assert "Chunk 1 content" in content["contenu_complet"]
        assert "Chunk 2 content" in content["contenu_complet"]
        assert content["nb_chunks"] == 2

    def test_get_lesson_content_not_found(self, rag_chain_mocked):
        """Leçon introuvable."""
        rag_chain_mocked.vector_store._collection.get.return_value = {
            "ids": [], "documents": [], "metadatas": []
        }

        content = rag_chain_mocked.get_lesson_content("francais", "Inexistant")

        assert content is None

    def test_get_lesson_content_format(self, rag_chain_mocked):
        """Format du contenu retourné."""
        mock_results = {
            "ids": ["1"],
            "documents": ["Contenu de la leçon"],
            "metadatas": [{
                "titre": "Test",
                "matiere": "svt",
                "url": "http://test.com",
                "niveau": "5eme",
                "source": "vikidia"
            }]
        }

        # Override le mock
        rag_chain_mocked.vector_store._collection.get = MagicMock(return_value=mock_results)

        content = rag_chain_mocked.get_lesson_content("svt", "Test")

        assert "titre" in content
        assert "resume" in content
        assert "contenu_complet" in content
        assert "url" in content
        assert "matiere" in content
        assert "niveau" in content
        assert "source" in content
        assert "nb_chunks" in content

    def test_get_lesson_content_error_handling(self, rag_chain_mocked):
        """Gestion d'erreur."""
        rag_chain_mocked.vector_store._collection.get.side_effect = Exception("Error")

        content = rag_chain_mocked.get_lesson_content("mathematiques", "Test")

        assert content is None
