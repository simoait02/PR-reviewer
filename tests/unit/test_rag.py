import asyncio
from unittest.mock import patch

from github_mcp_tools.rag import database
from github_mcp_tools.rag import service as rag_service
from github_mcp_tools.rag.retriever import (
    BestPracticesRetriever,
    _heading_match_score,
)
from langchain_core.documents import Document

from scripts import ingest_rag


def run(coroutine):
    return asyncio.run(coroutine)


class FakeVectorStore:
    def __init__(self):
        self.calls = []
        self.rows = []

    async def asimilarity_search_with_score(self, query, *, k, **kwargs):
        self.calls.append((query, k, kwargs["filter"]))
        return self.rows


def test_retriever_search_clamps_limit_and_maps_rows():
    vector_store = FakeVectorStore()
    vector_store.rows = [
        (
            Document(
                page_content="Testing guidance section.", metadata={"title": "Testing"}
            ),
            0.25,
        )
    ]
    retriever = BestPracticesRetriever(vector_store)

    result = run(retriever.search("unit tests", limit=100))

    assert result[0].title == "Testing"
    assert result[0].distance == 0.25
    assert vector_store.calls == [("unit tests", 80, {"chunk_type": "rule"})]


def test_ingestion_creates_one_focused_chunk_per_rule(tmp_path, monkeypatch):
    (tmp_path / "chapter.md").write_text(
        """# Chapter

Intro

## First rule

`id: first-rule | category: readability`

Look for this.

## Second rule

`id: second-rule | category: design`

        Fix this.
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(ingest_rag, "DOCUMENTS_DIR", tmp_path)

    chunks = ingest_rag.load_documents()

    assert [chunk.metadata["Header 2"] for chunk in chunks] == [
        "First rule",
        "Second rule",
    ]
    assert all(chunk.metadata["chunk_type"] == "rule" for chunk in chunks)
    assert all(chunk.page_content.startswith("##") for chunk in chunks)
    assert all("parent" not in chunk.metadata for chunk in chunks)
    assert all(
        chunk.metadata["heading_path"] == ["Chapter", heading]
        for chunk, heading in zip(chunks, ("First rule", "Second rule"), strict=True)
    )


def test_retriever_applies_minimum_limit():
    vector_store = FakeVectorStore()
    retriever = BestPracticesRetriever(vector_store)

    result = run(retriever.search("query", limit=0))

    assert result == []
    assert vector_store.calls == []


def test_retriever_prioritizes_exact_heading_matches():
    vector_store = FakeVectorStore()
    vector_store.rows = [
        (
            Document(
                page_content="Semantic result.",
                metadata={"title": "Semantic match", "heading_path": ["Other Topic"]},
            ),
            0.05,
        ),
        (
            Document(
                page_content="Heading result.",
                metadata={"title": "Heading match", "heading_path": ["Exact Topic"]},
            ),
            0.50,
        ),
    ]
    retriever = BestPracticesRetriever(vector_store)

    result = run(retriever.search("Exact Topic", limit=1))

    assert result[0].title == "Heading match"


def test_heading_match_score_handles_invalid_metadata():
    assert _heading_match_score("Exact Topic", None) == 0
    assert _heading_match_score("Exact Topic", {"heading_path": "Exact Topic"}) == 0


def test_retriever_from_env_constructs_dependencies(monkeypatch):
    vector_store = object()
    monkeypatch.setattr(
        "github_mcp_tools.rag.retriever.get_vector_store",
        lambda: vector_store,
    )

    retriever = BestPracticesRetriever.from_env()
    assert retriever.vector_store is vector_store


def test_database_url_uses_required_and_optional_environment(monkeypatch):
    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASSWORD", "password")
    monkeypatch.setenv("DB_NAME", "reviews")
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_PORT", raising=False)

    default_url = database.get_database_url()
    assert default_url.drivername == "postgresql+psycopg"
    assert default_url.host == "localhost"
    assert default_url.port == 5432

    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "5440")
    custom_url = database.get_database_url()
    assert custom_url.host == "db"
    assert custom_url.port == 5440


def test_database_engine_and_session_factory_are_cached(monkeypatch):
    database.get_engine.cache_clear()
    database.get_session_factory.cache_clear()
    monkeypatch.setenv("DB_USER", "user")
    monkeypatch.setenv("DB_PASSWORD", "password")
    monkeypatch.setenv("DB_NAME", "reviews")
    engine = object()
    session_factory = object()
    monkeypatch.setattr(
        database, "create_async_engine", lambda *_args, **_kwargs: engine
    )
    monkeypatch.setattr(
        database, "async_sessionmaker", lambda *_args, **_kwargs: session_factory
    )

    first_engine = database.get_engine()
    second_engine = database.get_engine()
    first_factory = database.get_session_factory()
    second_factory = database.get_session_factory()

    assert first_engine is second_engine is engine
    assert first_factory is second_factory is session_factory
    database.get_engine.cache_clear()
    database.get_session_factory.cache_clear()


def test_rag_service_reuses_one_retriever(monkeypatch):
    rag_service.get_best_practices_retriever.cache_clear()
    first = object()
    with patch.object(
        rag_service.BestPracticesRetriever,
        "from_env",
        return_value=first,
    ) as factory:
        assert rag_service.get_best_practices_retriever() is first
        assert rag_service.get_best_practices_retriever() is first
        factory.assert_called_once_with()
    rag_service.get_best_practices_retriever.cache_clear()
