"""Semantic retrieval for engineering best-practice chunks."""

from __future__ import annotations

import re

from openai import AsyncOpenAI
from pr_logging.core import get_logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from github_mcp_tools.rag.database import EMBEDDING_MODEL, get_session_factory
from github_mcp_tools.rag.models import (
    BestPracticeResult,
    Chunk,
    Document,
    Embedding,
)

logger = get_logger(__name__)


def _normalize_for_matching(value: str) -> str:
    return " ".join(re.findall(r"\w+", value.casefold()))


def _heading_match_score(query: str, metadata: object) -> int:
    if not isinstance(metadata, dict):
        return 0

    heading_path = metadata.get("heading_path", [])
    if not isinstance(heading_path, list):
        return 0

    normalized_query = f" {_normalize_for_matching(query)} "
    return max(
        (
            len(normalized_heading.split())
            for heading in heading_path
            if isinstance(heading, str)
            for normalized_heading in [_normalize_for_matching(heading)]
            if normalized_heading and f" {normalized_heading} " in normalized_query
        ),
        default=0,
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

        logger.debug("Initialized best-practices retriever")

    @classmethod
    def from_env(cls) -> BestPracticesRetriever:
        logger.debug("Creating best-practices retriever from environment")

        retriever = cls(
            session_factory=get_session_factory(),
            embedding_client=AsyncOpenAI(),
        )

        logger.debug("Created best-practices retriever")

        return retriever

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[BestPracticeResult]:
        requested_limit = limit
        limit = max(1, min(limit, 8))
        candidate_limit = min(max(limit * 10, 50), 100)

        logger.info(
            "Searching best practices with limit {} (requested {}), "
            "candidate pool {}, query length {}",
            limit,
            requested_limit,
            candidate_limit,
            len(query),
        )

        response = await self.embedding_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )
        query_vector = response.data[0].embedding

        logger.debug(
            "Generated query embedding with model '{}'",
            EMBEDDING_MODEL,
        )

        distance = Embedding.embedding.cosine_distance(query_vector)

        statement = (
            select(
                Document.title,
                Chunk.content,
                Chunk.metadata_.label("metadata_"),
                distance.label("distance"),
            )
            .join(Chunk, Chunk.document_id == Document.id)
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            # Older databases may still contain parent/child rows. Restrict
            # retrieval to the focused chunks created by the new ingestion.
            .where(Chunk.metadata_["chunk_type"].as_string() == "rule")
            .order_by(distance)
            .limit(candidate_limit)
        )

        async with self.session_factory() as session:
            rows = (await session.execute(statement)).mappings().all()

            ranked_rows = sorted(
                rows,
                key=lambda row: (
                    -_heading_match_score(query, row["metadata_"]),
                    float(row["distance"]),
                ),
            )[:limit]

        results = [
            BestPracticeResult(
                title=row["title"],
                content=row["content"],
                metadata=row["metadata_"],
                distance=float(row["distance"]),
            )
            for row in ranked_rows
        ]

        logger.debug(
            "Retrieved {} best-practices results",
            len(results),
        )

        return results
