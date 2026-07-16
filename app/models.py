from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from app.core.database import Base

JsonType = JSON().with_variant(JSONB, "postgresql")
UuidType = String(36).with_variant(UUID(as_uuid=False), "postgresql")

def uid() -> str: return str(uuid4())

class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    stage: Mapped[str] = mapped_column(String(50))
    versions: Mapped[list[AssessmentVersion]] = relationship(back_populates="assessment")

class AssessmentVersion(Base):
    __tablename__ = "assessment_versions"
    __table_args__ = (UniqueConstraint("assessment_id", "version"),)
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"))
    version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), index=True)
    definition: Mapped[dict] = mapped_column(JsonType)
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    assessment: Mapped[Assessment] = relationship(back_populates="versions")

class RuleSet(Base):
    __tablename__ = "rule_sets"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    stage: Mapped[str] = mapped_column(String(50))

class RuleSetVersion(Base):
    __tablename__ = "rule_set_versions"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    rule_set_id: Mapped[str] = mapped_column(ForeignKey("rule_sets.id"))
    version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30))
    rules: Mapped[list] = mapped_column(JsonType)

class Program(Base):
    __tablename__ = "programs"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class ResultTemplate(Base):
    __tablename__ = "result_templates"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    key: Mapped[str] = mapped_column(String(100), unique=True)
    content: Mapped[dict] = mapped_column(JsonType)

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(80))
    name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (UniqueConstraint("assessment_id", "idempotency_key"),)
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    public_token: Mapped[str] = mapped_column(String(80), unique=True, index=True, default=uid)
    assessment_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"))
    assessment_version_id: Mapped[str] = mapped_column(ForeignKey("assessment_versions.id"))
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id"))
    idempotency_key: Mapped[str | None] = mapped_column(String(200))
    answers: Mapped[dict] = mapped_column(JsonType)
    result: Mapped[dict] = mapped_column(JsonType)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class IntegrationDelivery(Base):
    __tablename__ = "integration_deliveries"
    id: Mapped[str] = mapped_column(UuidType, primary_key=True, default=uid)
    submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"))
    provider: Mapped[str] = mapped_column(String(50), default="gohighlevel")
    status: Mapped[str] = mapped_column(String(30), default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime)
    sanitized_response: Mapped[str | None] = mapped_column(Text)
