from typing import Any
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domain.schemas import AssessmentDefinition
from app.models import Assessment, AssessmentVersion

class AssessmentService:
    def __init__(self, session: Session): self.session = session
    def published(self, key: str) -> tuple[Assessment, AssessmentVersion, AssessmentDefinition]:
        stmt = select(Assessment, AssessmentVersion).join(AssessmentVersion).where(Assessment.key==key, AssessmentVersion.status=="published").order_by(AssessmentVersion.version.desc())
        row = self.session.execute(stmt).first()
        if not row: raise HTTPException(404, "Published assessment not found")
        a, v = row.t
        return a, v, AssessmentDefinition.model_validate(v.definition)
    def validate_answers(self, definition: AssessmentDefinition, answers: dict[str, Any]) -> None:
        errors = []
        for q in definition.questions:
            if q.type == "info": continue
            value = answers.get(q.key)
            if q.required and value in (None, "", [], {}): errors.append({"field": q.key, "message": "Required"})
            if value not in (None, "") and q.options and q.type.value in {"single_select","radio","dropdown","destination","inventory_type"}:
                allowed = {o.value for o in q.options if o.active}
                if value not in allowed: errors.append({"field": q.key, "message": "Invalid option"})
        if errors: raise HTTPException(422, {"code":"VALIDATION_FAILED","field_errors":errors})
