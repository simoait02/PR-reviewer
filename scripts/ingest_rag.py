import os
from pathlib import Path

import frontmatter
from langchain_classic.indexes import IndexingResult, SQLRecordManager, index
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import MarkdownHeaderTextSplitter

from scripts.database import get_database_url

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "docs"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
COLLECTION_NAME = "engineering_practices"
INDEX_NAMESPACE = "engineering-practices"

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")],
    strip_headers=False,
)


def load_documents() -> list[Document]:
    documents: list[Document] = []

    for file_path in sorted(DOCUMENTS_DIR.rglob("*.md")):
        raw = file_path.read_bytes()
        parsed = frontmatter.loads(raw.decode("utf-8"))
        source = file_path.relative_to(DOCUMENTS_DIR).as_posix()
        metadata_title = parsed.metadata.get("title")
        title = (
            metadata_title
            if isinstance(metadata_title, str) and metadata_title
            else file_path.stem
        )

        for document in splitter.split_text(parsed.content):
            if (
                not document.metadata.get("Header 2")
                or not document.page_content.strip()
            ):
                continue

            document.page_content = document.page_content.strip()
            document.metadata.update(
                source=source,
                title=title,
                chunk_type="rule",
                heading_path=[
                    document.metadata[header]
                    for header in ("Header 1", "Header 2")
                    if document.metadata.get(header)
                ],
            )
            documents.append(document)

    return documents


def index_documents(documents: list[Document]) -> IndexingResult:
    connection = get_database_url().render_as_string(hide_password=False)
    vector_store = PGVector(
        embeddings=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        collection_name=os.getenv("RAG_COLLECTION_NAME", COLLECTION_NAME),
        connection=connection,
        embedding_length=EMBEDDING_DIMENSIONS,
        use_jsonb=True,
        create_extension=False,
    )
    record_manager = SQLRecordManager(
        os.getenv("RAG_INDEX_NAMESPACE", INDEX_NAMESPACE),
        db_url=connection,
    )
    record_manager.create_schema()

    return index(
        documents,
        record_manager,
        vector_store,
        batch_size=int(os.getenv("RAG_INDEX_BATCH_SIZE", "100")),
        cleanup="full",
        source_id_key="source",
        key_encoder="sha256",
    )


def main() -> None:
    documents = load_documents()
    if not documents:
        raise RuntimeError(f"No Markdown rules found in {DOCUMENTS_DIR}")

    result = index_documents(documents)
    print(f"Indexed {len(documents)} chunks: {result}")


if __name__ == "__main__":
    main()
