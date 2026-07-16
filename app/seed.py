import json, sys
from pathlib import Path
from sqlalchemy import select
from app.core.database import Base, SessionLocal, engine
from app.models import Assessment, AssessmentVersion, Program, ResultTemplate, RuleSet, RuleSetVersion

def load(path: str) -> None:
    Base.metadata.create_all(bind=engine)
    data = json.loads(Path(path).read_text())
    with SessionLocal() as s:
        for item in data["assessments"]:
            a = s.execute(select(Assessment).where(Assessment.key==item["key"])).scalar_one_or_none() or Assessment(key=item["key"], name=item["name"], stage=item["stage"])
            s.add(a); s.flush()
            if not s.execute(select(AssessmentVersion).where(AssessmentVersion.assessment_id==a.id, AssessmentVersion.version==item["version"])).scalar_one_or_none():
                s.add(AssessmentVersion(assessment_id=a.id, version=item["version"], status="published", definition=item))
        for p in data["programs"]:
            if not s.execute(select(Program).where(Program.key==p["key"])).scalar_one_or_none(): s.add(Program(**p))
        for t in data["result_templates"]:
            if not s.execute(select(ResultTemplate).where(ResultTemplate.key==t["key"])).scalar_one_or_none(): s.add(ResultTemplate(**t))
        for rs in data["rule_sets"]:
            r = s.execute(select(RuleSet).where(RuleSet.key==rs["key"])).scalar_one_or_none() or RuleSet(key=rs["key"], stage=rs["stage"])
            s.add(r); s.flush()
            if not s.execute(select(RuleSetVersion).where(RuleSetVersion.rule_set_id==r.id, RuleSetVersion.version==rs["version"])).scalar_one_or_none(): s.add(RuleSetVersion(rule_set_id=r.id, version=rs["version"], status="published", rules=rs["rules"]))
        s.commit()

if __name__ == "__main__": load(sys.argv[1])
