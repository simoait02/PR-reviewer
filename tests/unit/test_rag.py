import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from github_mcp_tools.rag import database
from github_mcp_tools.rag import service as rag_service
from github_mcp_tools.rag.retriever import (
    BestPracticesRetriever,
    _heading_match_score,
)

from scripts.ingest_rag import split_into_rules


def run(coroutine):
    return asyncio.run(coroutine)


class FakeEmbeddingClient:
    def __init__(self):
        self.calls = []
        self.embeddings = self

    async def create(self, *, model, input):
        self.calls.append((model, input))
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])])


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows
        self.statement = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def execute(self, statement):
        self.statement = statement
        return FakeResult(self.rows)


def test_retriever_search_clamps_limit_and_maps_rows():
    rows = [
        {
            "title": "Testing",
            "content": "Testing guidance section.",
            "metadata_": {"section": "unit"},
            "distance": 0.25,
        }
    ]
    session = FakeSession(rows)
    embeddings = FakeEmbeddingClient()
    retriever = BestPracticesRetriever(lambda: session, embeddings)

    result = run(retriever.search("unit tests", limit=100))

    assert result[0].title == "Testing"
    assert result[0].distance == 0.25
    assert embeddings.calls == [(database.EMBEDDING_MODEL, "unit tests")]
    assert session.statement is not None


def test_ingestion_creates_one_focused_chunk_per_rule():
    chunks = split_into_rules(
        """# Chapter

Intro

## First rule

`id: first-rule | category: readability`

Look for this.

## Second rule

`id: second-rule | category: design`

        Fix this.
""",
    )

    assert [chunk.metadata["rule_id"] for chunk in chunks] == [
        "first-rule",
        "second-rule",
    ]
    assert all(chunk.metadata["chunk_type"] == "rule" for chunk in chunks)
    assert all("parent" not in chunk.metadata for chunk in chunks)
    assert all(
        chunk.metadata["heading_path"] == ["Chapter", heading]
        for chunk, heading in zip(chunks, ("First rule", "Second rule"), strict=True)
    )


def test_retriever_applies_minimum_limit():
    session = FakeSession([])
    retriever = BestPracticesRetriever(lambda: session, FakeEmbeddingClient())

    result = run(retriever.search("query", limit=0))

    assert result == []
    assert session.statement is not None


def test_retriever_prioritizes_exact_heading_matches():
    rows = [
        {
            "title": "Semantic match",
            "content": "Semantic result.",
            "metadata_": {"heading_path": ["Other Topic"]},
            "distance": 0.05,
        },
        {
            "title": "Heading match",
            "content": "Heading result.",
            "metadata_": {"heading_path": ["Exact Topic"]},
            "distance": 0.50,
        },
    ]
    session = FakeSession(rows)
    retriever = BestPracticesRetriever(lambda: session, FakeEmbeddingClient())

    result = run(retriever.search("Exact Topic", limit=1))

    assert result[0].title == "Heading match"


def test_heading_match_score_handles_invalid_metadata():
    assert _heading_match_score("Exact Topic", None) == 0
    assert _heading_match_score("Exact Topic", {"heading_path": "Exact Topic"}) == 0


def test_retriever_from_env_constructs_dependencies(monkeypatch):
    session_factory = object()
    embedding_client = object()
    monkeypatch.setattr(
        "github_mcp_tools.rag.retriever.get_session_factory",
        lambda: session_factory,
    )
    monkeypatch.setattr(
        "github_mcp_tools.rag.retriever.AsyncOpenAI",
        lambda: embedding_client,
    )

    retriever = BestPracticesRetriever.from_env()
    assert retriever.session_factory is session_factory
    assert retriever.embedding_client is embedding_client


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
