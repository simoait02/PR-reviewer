import asyncio
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import frontmatter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from openai import AsyncOpenAI
from sqlalchemy import select

from scripts.database import get_engine, get_session_factory
from scripts.models import Chunk, Document, Embedding

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "docs"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 100

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")],
    strip_headers=False,
)


@dataclass
class RuleChunk:
    content: str
    metadata: dict[str, object]


@dataclass
class ParsedDocument:
    title: str
    content_hash: str
    chunks: list[RuleChunk]


def extract_title(content: str, fallback: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", content)
    return match.group(1).strip() if match else fallback


def split_into_rules(markdown: str) -> list[RuleChunk]:
    chunks: list[RuleChunk] = []

    for section in splitter.split_text(markdown):
        # One H2 section per rule; skip the chapter-title section.
        if not section.metadata.get("Header 2"):
            continue

        content = section.page_content.strip()
        if not content:
            continue

        heading_path = [
            section.metadata[header]
            for header in ("Header 1", "Header 2")
            if section.metadata.get(header)
        ]
        metadata: dict[str, object] = {
            "chunk_type": "rule",
            "chunk_index": len(chunks),
            "heading_path": heading_path,
            **section.metadata,
        }

        rule_id = re.search(r"(?m)\bid:\s*([^\s|`]+)", content)
        if not rule_id:
            heading = section.metadata.get("Header 2", "<unnamed>")
            raise ValueError(f"Missing rule id in section {heading!r}")
        metadata["rule_id"] = rule_id.group(1)

        chunks.append(RuleChunk(content=content, metadata=metadata))

    return chunks


def parse_file(file_path: Path) -> ParsedDocument:
    raw = file_path.read_bytes()
    parsed = frontmatter.loads(raw.decode("utf-8"))

    return ParsedDocument(
        title=str(
            parsed.metadata.get("title")
            or extract_title(parsed.content, file_path.stem)
        ),
        content_hash=hashlib.sha256(raw).hexdigest(),
        chunks=split_into_rules(parsed.content),
    )


async def embed_texts(
    texts: list[str],
    client: AsyncOpenAI,
) -> list[list[float]]:
    vectors: list[list[float]] = []

    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start : start + EMBEDDING_BATCH_SIZE]
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        if len(response.data) != len(batch):
            raise ValueError(
                "Embedding response size mismatch: "
                f"expected {len(batch)}, got {len(response.data)}"
            )
        vectors.extend(
            item.embedding
            for item in sorted(response.data, key=lambda item: item.index)
        )

    return vectors


async def is_unchanged(session_factory, doc: ParsedDocument) -> bool:
    async with session_factory() as session:
        stored_hash = await session.scalar(
            select(Document.content_hash).where(Document.title == doc.title)
        )
    return stored_hash == doc.content_hash


async def save_document(
    doc: ParsedDocument,
    vectors: list[list[float]],
    session_factory,
) -> None:
    chunks = [
        Chunk(
            content=chunk.content,
            metadata_=chunk.metadata,
            embedding=Embedding(embedding=vector),
        )
        for chunk, vector in zip(doc.chunks, vectors, strict=True)
    ]

    async with session_factory() as session, session.begin():
        existing_documents = (
            await session.scalars(select(Document).where(Document.title == doc.title))
        ).all()
        for existing in existing_documents:
            await session.delete(existing)
        if existing_documents:
            await session.flush()

        session.add(
            Document(
                title=doc.title,
                content_hash=doc.content_hash,
                chunks=chunks,
            )
        )


async def ingest_file(
    file_path: Path,
    session_factory,
    client: AsyncOpenAI,
) -> None:
    doc = parse_file(file_path)

    if await is_unchanged(session_factory, doc):
        print(f"Skipped: {file_path.name}")
        return

    # Embed before opening the write transaction so no DB connection
    # is held open during network calls.
    vectors = await embed_texts([c.content for c in doc.chunks], client)
    await save_document(doc, vectors, session_factory)

    print(f"Ingested {file_path.name}: {len(doc.chunks)} rules")


async def main() -> None:
    files = sorted(DOCUMENTS_DIR.rglob("*.md"))
    if not files:
        raise RuntimeError(f"No Markdown files found in {DOCUMENTS_DIR}")

    client = AsyncOpenAI()
    engine = get_engine()
    session_factory = get_session_factory()

    try:
        for file_path in files:
            await ingest_file(file_path, session_factory, client)
    finally:
        await client.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
