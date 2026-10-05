"""Semantic retrieval for engineering best-practice chunks."""

from __future__ import annotations

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from github_mcp_tools.rag.database import EMBEDDING_MODEL, get_session_factory
from github_mcp_tools.rag.models import (
    BestPracticeResult,
    Category,
    Chunk,
    Document,
    Embedding,
)


class BestPracticesRetriever:
    """Retrieve the most relevant embedded best-practice chunks."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        embedding_client: AsyncOpenAI,
    ) -> None:
        self.session_factory = session_factory
        self.embedding_client = embedding_client

    @classmethod
    def from_env(cls) -> BestPracticesRetriever:
        return cls(
            session_factory=get_session_factory(),
            embedding_client=AsyncOpenAI(),
        )

    async def search(
        self,
        query: str,
        category: Category | None = None,
        limit: int = 5,
    ) -> list[BestPracticeResult]:
        limit = max(1, min(limit, 8))
        response = await self.embedding_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )
        query_vector = response.data[0].embedding
        distance = Embedding.embedding.cosine_distance(query_vector)

        statement = (
            select(
                Document.title,
                Document.category,
                Chunk.content,
                Chunk.metadata_,
                distance.label("distance"),
            )
            .join(Chunk, Chunk.document_id == Document.id)
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .order_by(distance)
            .limit(limit)
        )

        if category is not None:
            statement = statement.where(Document.category == category)

        async with self.session_factory() as session:
            rows = (await session.execute(statement)).mappings().all()

        return [
            BestPracticeResult(
                title=row["title"],
                category=row["category"],
                content=row["content"],
                metadata=row["metadata_"],
                distance=float(row["distance"]),
            )
            for row in rows
        ]
