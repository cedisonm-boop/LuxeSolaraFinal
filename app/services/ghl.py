from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Assessment, IntegrationDelivery, Lead, Submission

GHL_UPSERT_URL = "https://services.leadconnectorhq.com/contacts/upsert"


def _setting_value(value: Any) -> str:
    if hasattr(value, "get_secret_value"):
        return value.get_secret_value()
    return value or ""


def _safe_response(status_code: int | None, body: str) -> str:
    return json.dumps({"status_code": status_code, "body": body[:2000]})


def _payload(session: Session, submission: Submission) -> dict:
    lead = session.get(Lead, submission.lead_id) if submission.lead_id else None
    assessment = session.get(Assessment, submission.assessment_id)
    answers = submission.answers or {}
    result = submission.result or {}

    name = answers.get("name") or (lead.name if lead else None) or "Luxe Solara Lead"
    parts = name.split()
    first_name = parts[0] if parts else name
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

    tags = [
        "luxe-solara",
        f"assessment-{assessment.key if assessment else 'unknown'}",
        f"outcome-{result.get('outcome', 'unknown')}",
    ]
    if result.get("eligible_for_paid_audit"):
        tags.append("eligible-paid-audit")

    settings = get_settings()
    return {
        "locationId": _setting_value(settings.ghl_location_id),
        "firstName": first_name,
        "lastName": last_name,
        "name": name,
        "email": answers.get("email") or (lead.email if lead else None),
        "phone": answers.get("phone") or (lead.phone if lead else None),
        "source": "Luxe Solara Qualification",
        "tags": tags,
    }


def process_delivery(session: Session, delivery_id: str) -> str:
    delivery = session.get(IntegrationDelivery, delivery_id)
    if not delivery:
        return "missing"

    settings = get_settings()
    api_key = _setting_value(settings.ghl_api_key)
    location_id = _setting_value(settings.ghl_location_id)
    delivery.attempt_count = (delivery.attempt_count or 0) + 1

    if not api_key or not location_id:
        delivery.status = "failed"
        delivery.sanitized_response = json.dumps({"error": "GHL_API_KEY or GHL_LOCATION_ID missing"})
        delivery.next_retry_at = datetime.utcnow() + timedelta(minutes=15)
        session.commit()
        return delivery.status

    submission = session.get(Submission, delivery.submission_id)
    if not submission:
        delivery.status = "failed"
        delivery.sanitized_response = json.dumps({"error": "submission missing"})
        session.commit()
        return delivery.status

    body = json.dumps(_payload(session, submission))

    try:
        completed = subprocess.run(
            [
                "curl",
                "-sS",
                "-X",
                "POST",
                GHL_UPSERT_URL,
                "-H",
                f"Authorization: Bearer {api_key}",
                "-H",
                "Version: 2021-07-28",
                "-H",
                "Content-Type: application/json",
                "-H",
                "Accept: application/json",
                "-H",
                "User-Agent: LuxeSolara/1.0",
                "--data-binary",
                "@-",
                "-w",
                "\n%{http_code}",
            ],
            input=body,
            text=True,
            capture_output=True,
            timeout=45,
        )

        output = completed.stdout or ""
        response_body, status_text = output.rsplit("\n", 1) if "\n" in output else (output, "")
        status_code = int(status_text) if status_text.isdigit() else None

        if completed.stderr:
            response_body = response_body + "\n" + completed.stderr

        delivery.status = "success" if status_code and 200 <= status_code < 300 else "failed"
        delivery.sanitized_response = _safe_response(status_code, response_body)
        delivery.next_retry_at = None if delivery.status == "success" else datetime.utcnow() + timedelta(minutes=15)

    except Exception as exc:
        delivery.status = "failed"
        delivery.sanitized_response = json.dumps({"error": str(exc)[:1000]})
        delivery.next_retry_at = datetime.utcnow() + timedelta(minutes=15)

    session.commit()
    return delivery.status
