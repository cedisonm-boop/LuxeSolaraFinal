from __future__ import annotations
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field

class Stage(StrEnum):
    fit_check = "fit_check"
    paid_audit = "paid_audit"

class VersionStatus(StrEnum):
    draft = "draft"
    published = "published"
    retired = "retired"
    scheduled = "scheduled"

class QuestionType(StrEnum):
    short_text="short_text"; long_text="long_text"; email="email"; phone="phone"; number="number"; currency="currency"; percentage="percentage"; date="date"; yes_no="yes_no"; single_select="single_select"; multi_select="multi_select"; radio="radio"; checkboxes="checkboxes"; dropdown="dropdown"; address="address"; resort_search="resort_search"; destination="destination"; inventory_type="inventory_type"; quantity="quantity"; file_upload_metadata="file_upload_metadata"; consent="consent"; info="info"

class QuestionOption(BaseModel):
    value: str
    label: str
    active: bool = True

class QuestionDefinition(BaseModel):
    key: str
    label: str
    type: QuestionType
    required: bool = False
    order: int = 0
    section: str = "default"
    help_text: str | None = None
    placeholder: str | None = None
    options: list[QuestionOption] = Field(default_factory=list)
    validation: dict[str, Any] = Field(default_factory=dict)
    visibility: dict[str, Any] | None = None
    sensitive: str = "standard"
    send_to_ghl: bool = False
    ghl_field: str | None = None
    rule_usable: bool = True

class AssessmentDefinition(BaseModel):
    key: str
    name: str
    description: str = ""
    stage: Stage
    version: int
    status: VersionStatus
    intro: str = ""
    completion: str = ""
    consent_text: str = ""
    questions: list[QuestionDefinition]

class SubmissionCreate(BaseModel):
    answers: dict[str, Any]
    lead: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None

class Rule(BaseModel):
    key: str
    name: str
    stage: Stage
    priority: int = 100
    status: Literal["active", "inactive"] = "active"
    when: dict[str, Any] = Field(default_factory=dict)
    then: list[dict[str, Any]] = Field(default_factory=list)
    public_explanation: str | None = None
    internal_explanation: str | None = None
    stop_processing: bool = False

class EvaluationResult(BaseModel):
    outcome: str = "additional_information_required"
    qualification_status: str = "pending"
    score: dict[str, int] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    verification_required: list[str] = Field(default_factory=list)
    manual_review: bool = False
    eligible_for_paid_audit: bool = False
    recommended_program: str | None = None
    eligible_programs: list[str] = Field(default_factory=list)
    excluded_programs: list[str] = Field(default_factory=list)
    alternative_recommendations: list[str] = Field(default_factory=list)
    result_template_key: str | None = None
    public_summary: list[str] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    rule_set_version: int = 1
