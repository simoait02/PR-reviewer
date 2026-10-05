"""Shared RAG services used by MCP tools."""

from functools import lru_cache

from github_mcp_tools.rag.retriever import BestPracticesRetriever


@lru_cache
def get_best_practices_retriever() -> BestPracticesRetriever:
    """Return one retriever instance per MCP server process."""
    return BestPracticesRetriever.from_env()
