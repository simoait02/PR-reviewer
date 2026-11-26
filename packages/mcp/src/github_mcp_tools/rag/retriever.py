"""Semantic retrieval for engineering best-practice chunks."""

from __future__ import annotations

import os
import re
from typing import Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from pr_logging.core import get_logger

from github_mcp_tools.rag.database import EMBEDDING_MODEL, get_database_url
from github_mcp_tools.rag.models import BestPracticeResult

logger = get_logger(__name__)

DEFAULT_COLLECTION_NAME = "engineering_practices"


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


def get_vector_store() -> PGVector:
    connection = get_database_url().render_as_string(hide_password=False)
    return PGVector(
        embeddings=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        collection_name=os.getenv("RAG_COLLECTION_NAME", DEFAULT_COLLECTION_NAME),
        connection=connection,
        embedding_length=1536,
        use_jsonb=True,
        create_extension=False,
        async_mode=True,
    )


class BestPracticesRetriever:
    """Retrieve the most relevant embedded best-practice chunks."""

    def __init__(self, vector_store: PGVector) -> None:
        self.vector_store = vector_store
        logger.debug("Initialized best-practices retriever")

    @classmethod
    def from_env(cls) -> BestPracticesRetriever:
        logger.debug("Creating best-practices retriever from environment")
        retriever = cls(vector_store=get_vector_store())
        logger.debug("Created best-practices retriever")
        return retriever

    async def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[BestPracticeResult]:
        requested_limit = limit
        limit = max(1, min(limit, 8))
        if requested_limit <= 0:
            return []

        candidate_limit = min(max(limit * 10, 50), 100)
        logger.info(
            "Searching best practices with limit {} (requested {}), "
            "candidate pool {}, query length {}",
            limit,
            requested_limit,
            candidate_limit,
            len(query),
        )

        rows = await self.vector_store.asimilarity_search_with_score(
            query,
            k=candidate_limit,
            filter={"chunk_type": "rule"},
        )
        ranked_rows = sorted(
            rows,
            key=lambda row: (
                -_heading_match_score(query, row[0].metadata),
                float(row[1]),
            ),
        )[:limit]

        results = [
            self._to_result(document, distance) for document, distance in ranked_rows
        ]
        logger.debug("Retrieved {} best-practices results", len(results))
        return results

    @staticmethod
    def _to_result(document: Document, distance: float) -> BestPracticeResult:
        metadata: dict[str, Any] = dict(document.metadata)
        return BestPracticeResult(
            title=str(metadata.get("title", "Engineering best practices")),
            content=document.page_content,
            metadata=metadata,
            distance=float(distance),
        )
