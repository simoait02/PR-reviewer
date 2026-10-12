import datetime
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
    )

    document: Mapped[Document] = relationship(
        back_populates="chunks",
    )

    parent: Mapped["Chunk | None"] = relationship(
        "Chunk",
        back_populates="children",
        remote_side=[id],
        foreign_keys=[parent_id],
    )

    children: Mapped[list["Chunk"]] = relationship(
        "Chunk",
        back_populates="parent",
        foreign_keys=[parent_id],
    )

    embedding: Mapped["Embedding | None"] = relationship(
        back_populates="chunk",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    chunk: Mapped[Chunk] = relationship(back_populates="embedding")
