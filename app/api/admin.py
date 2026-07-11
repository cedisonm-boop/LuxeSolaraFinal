from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_session
from app.domain.schemas import Rule
from app.models import Assessment, AssessmentVersion, IntegrationDelivery, RuleSetVersion, Submission
from app.services.qualification_engine import QualificationEngine

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

def require_admin() -> bool:
    return True

@router.get("/assessments", dependencies=[Depends(require_admin)])
def assessments(session: Session = Depends(get_session)) -> list[dict]:
    return [{"id": a.id, "key": a.key, "name": a.name, "stage": a.stage} for a in session.execute(select(Assessment)).scalars()]

@router.post("/assessment-versions/{version_id}/validate", dependencies=[Depends(require_admin)])
def validate_assessment(version_id: str, session: Session = Depends(get_session)) -> dict:
    version = session.get(AssessmentVersion, version_id)
    return {"valid": bool(version), "errors": [] if version else ["missing version"]}

@router.post("/assessment-versions/{version_id}/publish", dependencies=[Depends(require_admin)])
def publish_assessment(version_id: str, session: Session = Depends(get_session)) -> dict:
    version = session.get(AssessmentVersion, version_id)
    if version and version.status == "draft":
        version.status = "published"; session.commit()
    return {"published": bool(version)}

@router.post("/rule-set-versions/{version_id}/simulate", dependencies=[Depends(require_admin)])
def simulate(version_id: str, facts: dict, session: Session = Depends(get_session)) -> dict:
    version = session.get(RuleSetVersion, version_id)
    rules = [Rule.model_validate(r) for r in (version.rules if version else [])]
    return QualificationEngine().evaluate(rules, facts, version.version if version else 1).model_dump(mode="json")

@router.get("/submissions", dependencies=[Depends(require_admin)])
def submissions(session: Session = Depends(get_session)) -> list[dict]:
    return [{"id": s.id, "created_at": s.created_at.isoformat(), "outcome": s.result.get("outcome")} for s in session.execute(select(Submission)).scalars()]

@router.post("/integrations/{delivery_id}/replay", dependencies=[Depends(require_admin)])
def replay(delivery_id: str, session: Session = Depends(get_session)) -> dict:
    delivery = session.get(IntegrationDelivery, delivery_id)
    if delivery:
        delivery.status = "pending"; session.commit()
    return {"queued": bool(delivery)}
