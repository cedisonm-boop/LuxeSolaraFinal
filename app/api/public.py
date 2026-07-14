from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.domain.schemas import Rule, SubmissionCreate
from app.models import IntegrationDelivery, Lead, RuleSet, RuleSetVersion, Submission
from app.services.assessment_service import AssessmentService
from app.services.ghl import process_delivery
from app.services.qualification_engine import QualificationEngine

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/assessments/{assessment_key}")
def get_assessment(assessment_key: str, session: Session = Depends(get_session)) -> dict:
    _, _, definition = AssessmentService(session).published(assessment_key)
    return definition.model_dump(mode="json")


@router.post("/assessments/{assessment_key}/submissions")
def submit_assessment(
    assessment_key: str,
    payload: SubmissionCreate,
    idempotency_key: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> dict:
    service = AssessmentService(session)
    assessment, version, definition = service.published(assessment_key)
    idem = payload.idempotency_key or idempotency_key
    if idem:
        existing = session.execute(
            select(Submission).where(
                Submission.assessment_id == assessment.id,
                Submission.idempotency_key == idem,
            )
        ).scalar_one_or_none()
        if existing:
            return {
                "public_token": existing.public_token,
                "outcome": existing.result.get("outcome"),
                "idempotent": True,
            }

    service.validate_answers(definition, payload.answers)
    lead = Lead(
        email=payload.lead.get("email") or payload.answers.get("email"),
        phone=payload.lead.get("phone") or payload.answers.get("phone"),
        name=payload.lead.get("name") or payload.answers.get("name"),
    )
    session.add(lead)
    session.flush()

    rs = session.execute(
        select(RuleSet, RuleSetVersion)
        .join(RuleSetVersion)
        .where(
            RuleSet.stage == definition.stage.value,
            RuleSetVersion.status == "published",
        )
        .order_by(RuleSetVersion.version.desc())
    ).first()
    rules = [Rule.model_validate(r) for r in (rs.t[1].rules if rs else [])]
    result = QualificationEngine().evaluate(rules, payload.answers, rs.t[1].version if rs else 1)
    submission = Submission(
        assessment_id=assessment.id,
        assessment_version_id=version.id,
        lead_id=lead.id,
        idempotency_key=idem,
        answers=payload.answers,
        result=result.model_dump(mode="json"),
    )
    session.add(submission)
    session.flush()

    delivery = IntegrationDelivery(submission_id=submission.id)
    session.add(delivery)
    session.commit()
    process_delivery(session, delivery.id)

    return {
        "public_token": submission.public_token,
        "outcome": result.outcome,
        "eligible_for_paid_audit": result.eligible_for_paid_audit,
    }


@router.get("/submissions/{public_token}/result")
def get_result(public_token: str, session: Session = Depends(get_session)) -> dict:
    submission = session.execute(
        select(Submission).where(Submission.public_token == public_token)
    ).scalar_one_or_none()
    if not submission:
        raise HTTPException(404, "Result not found")
    result = dict(submission.result)
    result.pop("trace", None)
    result.pop("score", None)
    return result


@router.get("/submissions/{public_token}/status")
def get_status(public_token: str, session: Session = Depends(get_session)) -> dict:
    submission = session.execute(
        select(Submission).where(Submission.public_token == public_token)
    ).scalar_one_or_none()
    if not submission:
        raise HTTPException(404, "Submission not found")
    return {"status": "complete", "outcome": submission.result.get("outcome")}
