import asyncio
import hashlib
import re
from pathlib import Path

import frontmatter
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from openai import AsyncOpenAI
from sqlalchemy import select

from scripts.database import get_engine, get_session_factory
from scripts.models import Chunk, Document, Embedding

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "docs"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 100

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
]

parent_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,
)

child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1600,
    chunk_overlap=200,
    separators=[
        "\n### ",
        "\n\n",
        "\n",
        " ",
        "",
    ],
)


def extract_title(content: str, fallback: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", content)

    if match:
        return match.group(1).strip()

    return fallback


def split_into_parent_children(
    markdown: str,
    source_path: str,
) -> list[dict]:
    parents = []

    sections = parent_splitter.split_text(markdown)

    for parent_index, section in enumerate(sections):
        parent_content = section.page_content.strip()

        if not parent_content:
            continue

        heading_path = [
            str(value)
            for value in section.metadata.values()
            if value
        ]

        parent_metadata = {
            "chunk_type": "parent",
            "source_path": source_path,
            "parent_index": parent_index,
            "heading_path": heading_path,
            **section.metadata,
        }

        children = []

        for child_index, child_content in enumerate(
            child_splitter.split_text(parent_content)
        ):
            child_content = child_content.strip()

            if not child_content:
                continue

            children.append(
                {
                    "content": child_content,
                    "metadata": {
                        **parent_metadata,
                        "chunk_type": "child",
                        "chunk_index": child_index,
                    },
                }
            )

        if children:
            parents.append(
                {
                    "content": parent_content,
                    "metadata": parent_metadata,
                    "children": children,
                }
            )

    return parents


def process_file(file_path: Path) -> dict:
    file_path = file_path.resolve()
    raw_content = file_path.read_bytes()
    content_hash = hashlib.sha256(raw_content).hexdigest()

    parsed = frontmatter.loads(
        raw_content.decode("utf-8")
    )

    source_path = file_path.relative_to(PROJECT_ROOT).as_posix()

    title = str(
        parsed.metadata.get("title")
        or extract_title(parsed.content, file_path.stem)
    )

    parents = split_into_parent_children(
        markdown=parsed.content,
        source_path=source_path,
    )

    return {
        "file_path": file_path,
        "title": title,
        "content_hash": content_hash,
        "parents": parents,
    }


async def embed_chunks(
    chunks: list[Chunk],
    openai_client: AsyncOpenAI,
) -> None:
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start : start + EMBEDDING_BATCH_SIZE]

        response = await openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[chunk.content for chunk in batch],
        )

        vectors = sorted(
            response.data,
            key=lambda item: item.index,
        )

        if len(vectors) != len(batch):
            raise RuntimeError(
                "Embedding response count does not match chunk count"
            )

        for chunk, vector in zip(batch, vectors):
            chunk.embedding = Embedding(
                embedding=vector.embedding,
            )


async def save_document(
    result: dict,
    session_local,
    openai_client: AsyncOpenAI,
) -> None:
    async with session_local() as session, session.begin():
        existing_document = await session.scalar(
            select(Document).where(
                Document.content_hash == result["content_hash"]
            )
        )

        if existing_document is not None:
            print(f"Skipped: {result['file_path'].name}")
            return

        document = Document(
            title=result["title"],
            content_hash=result["content_hash"],
        )

        child_chunks = []

        for parent_result in result["parents"]:
            parent_chunk = Chunk(
                content=parent_result["content"],
                metadata_=parent_result["metadata"],
            )

            document.chunks.append(parent_chunk)

            for child_result in parent_result["children"]:
                child_chunk = Chunk(
                    content=child_result["content"],
                    metadata_=child_result["metadata"],
                    parent=parent_chunk,
                )

                document.chunks.append(child_chunk)
                child_chunks.append(child_chunk)

        session.add(document)
        await session.flush()

        await embed_chunks(
            chunks=child_chunks,
            openai_client=openai_client,
        )

        print(
            f"Ingested {result['file_path'].name}: "
            f"{len(result['parents'])} parents, "
            f"{len(child_chunks)} children"
        )


async def main() -> None:
    files = sorted(DOCUMENTS_DIR.rglob("*.md"))

    if not files:
        raise RuntimeError(
            f"No Markdown files found in {DOCUMENTS_DIR}"
        )

    openai_client = AsyncOpenAI()
    engine = get_engine()
    session_local = get_session_factory()

    try:
        for file_path in files:
            result = process_file(file_path)

            await save_document(
                result=result,
                session_local=session_local,
                openai_client=openai_client,
            )
    finally:
        await openai_client.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())