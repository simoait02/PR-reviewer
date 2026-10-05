import datetime
import uuid
from enum import Enum
from typing import Any

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Category(str, Enum):
    ARCHITECTURE = "architecture"
    CODE_QUALITY = "code-quality"
    CODE_REVIEW = "code-review"
    COLLABORATION = "collaboration"
    DELIVERY_AND_OPERATIONS = "delivery-and-operations"
    DEPENDENCIES_AND_SUPPLY_CHAIN = "dependencies-and-supply-chain"
    DOCUMENTATION_AND_TEAM_PRACTICES = "documentation-and-team-practices"
    OBSERVABILITY_AND_RELIABILITY = "observability-and-reliability"
    PROJECT_MANAGEMENT = "project-management"
    PROJECT_READINESS = "project-readiness"
    REQUIREMENTS_AND_PLANNING = "requirements-and-planning"
    SECURITY_AND_PRIVACY = "security-and-privacy"
    TESTING = "testing"


class BestPracticeResult(BaseModel):
    """A best-practice chunk returned by semantic retrieval."""

    title: str = Field(description="Title of the source best-practice document.")
    category: Category = Field(description="Category of the source document.")
    content: str = Field(description="Retrieved chunk content.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Chunk metadata from the source best-practice document.",
    )
    distance: float = Field(
        description="Cosine distance between the query and this chunk embedding."
    )


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[Category] = mapped_column(SqlEnum(Category), nullable=False)
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
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    document: Mapped[Document] = relationship(back_populates="chunks")
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
