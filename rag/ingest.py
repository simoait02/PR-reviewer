import asyncio
import hashlib
import os
from pathlib import Path

import frontmatter
from openai import AsyncOpenAI
from langchain_text_splitters import MarkdownHeaderTextSplitter
from sqlalchemy import URL, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from rag.models import Document, Category, Chunk, Embedding

DOCUMENTS_DIR = (
      Path(__file__).resolve().parents[1]
      / "docs"
      / "good-practices")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "localhost"),
    port=os.environ["DB_PORT"],
    database=os.environ["DB_NAME"],
)

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
]

EMBEDDING_MODEL = "text-embedding-3-small"
openai_client = AsyncOpenAI()

markdown_header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on = headers_to_split_on,
)

def process_file(file_path: Path):
    raw_content = file_path.read_bytes()
    content_hash = hashlib.sha256(raw_content).hexdigest()
    file_content = frontmatter.loads(raw_content.decode("utf-8"))
    chunks = markdown_header_splitter.split_text(file_content.content)
    return {
        "file_path": file_path,
        "title": file_content["title"],
        "description": file_content["description"],
        "category": file_content["category"],
        "content_hash": content_hash,
        "chunks": chunks,
    }


engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_pre_ping=True,
)

session_local = async_sessionmaker(engine,expire_on_commit=False)

async def save_document(result):
    async with session_local() as session:
        async with session.begin():
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
                description=result["description"],
                category=Category(result["category"]),
                content_hash=result["content_hash"],
            )

            for chunk in result["chunks"]:
                document.chunks.append(
                    Chunk(
                        content=chunk.page_content,
                        metadata_=chunk.metadata,
                    )
                )

            session.add(document)
            await session.flush()

            embedding_response = await openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=[chunk.content for chunk in document.chunks],
            )

            vectors = sorted(
                embedding_response.data,
                key=lambda item: item.index,
            )

            for chunk, vector in zip(document.chunks, vectors):
                chunk.embedding = Embedding(embedding=vector.embedding)

            print(
                f"Ingested {result['file_path'].name}: "
                f"{len(document.chunks)} chunks"
            )

async def main():
    files = sorted(DOCUMENTS_DIR.glob("*.md"))

    if not files:
        raise RuntimeError(f"No Markdown files found in {DOCUMENTS_DIR}")

    for file_path in files:
        result = process_file(file_path)
        await save_document(result)

    await openai_client.close()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
