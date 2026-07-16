from __future__ import annotations
from typing import Any
from app.domain.schemas import EvaluationResult, Rule

MISSING = object()

def _get(facts: dict[str, Any], key: str) -> Any:
    return facts.get(key, MISSING)

def compare(actual: Any, operator: str, expected: Any = None) -> bool:
    if operator == "exists": return actual is not MISSING and actual not in (None, "")
    if operator == "is_empty": return actual is MISSING or actual in (None, "", [], {})
    if actual is MISSING: return False
    if operator == "equals": return actual == expected
    if operator == "not_equals": return actual != expected
    if operator == "in": return actual in expected
    if operator == "not_in": return actual not in expected
    if operator == "greater_than": return actual > expected
    if operator == "greater_than_or_equal": return actual >= expected
    if operator == "less_than": return actual < expected
    if operator == "less_than_or_equal": return actual <= expected
    if operator == "between": return expected[0] <= actual <= expected[1]
    if operator == "contains": return expected in actual
    if operator == "contains_any": return any(v in actual for v in expected)
    if operator == "contains_all": return all(v in actual for v in expected)
    if operator == "starts_with": return str(actual).startswith(str(expected))
    if operator == "ends_with": return str(actual).endswith(str(expected))
    raise ValueError(f"Unsupported operator: {operator}")

class QualificationEngine:
    def evaluate_condition(self, condition: dict[str, Any], facts: dict[str, Any]) -> bool:
        if "all" in condition: return all(self.evaluate_condition(c, facts) for c in condition["all"])
        if "any" in condition: return any(self.evaluate_condition(c, facts) for c in condition["any"])
        if "none" in condition: return not any(self.evaluate_condition(c, facts) for c in condition["none"])
        if "not" in condition: return not self.evaluate_condition(condition["not"], facts)
        key = condition.get("field") or condition.get("fact")
        return compare(_get(facts, key), condition["operator"], condition.get("value"))

    def evaluate(self, rules: list[Rule], facts: dict[str, Any], rule_set_version: int = 1) -> EvaluationResult:
        result = EvaluationResult(rule_set_version=rule_set_version)
        priorities: dict[str, int] = {}
        for rule in sorted([r for r in rules if r.status == "active"], key=lambda r: r.priority):
            matched = self.evaluate_condition(rule.when, facts) if rule.when else True
            result.trace.append({"rule_key": rule.key, "matched": matched, "explanation": rule.internal_explanation})
            if not matched: continue
            if rule.public_explanation: result.public_summary.append(rule.public_explanation)
            for action in rule.then:
                name = action["action"]
                if name in {"add_score", "subtract_score"}:
                    cat = action.get("category", "default"); val = int(action.get("value", 0))
                    result.score[cat] = result.score.get(cat, 0) + (val if name == "add_score" else -val)
                elif name == "add_tag": result.tags.append(action["value"])
                elif name == "add_risk_flag": result.risk_flags.append(action["value"])
                elif name == "add_reason": result.reason_codes.append(action["code"])
                elif name == "require_verification": result.verification_required.append(action["field"])
                elif name == "disqualify": result.qualification_status = "disqualified"; result.outcome = action.get("outcome", "not_currently_eligible")
                elif name == "require_manual_review": result.manual_review = True; result.outcome = action.get("outcome", "potential_fit_manual_review")
                elif name == "qualify_for_paid_audit": result.eligible_for_paid_audit = True; result.qualification_status = "qualified"; result.outcome = "qualified_for_paid_audit"
                elif name == "recommend_program":
                    p = action["program_key"]; priorities[p] = int(action.get("priority", 100)); result.eligible_programs.append(p)
                elif name == "exclude_program": result.excluded_programs.append(action["program_key"])
                elif name == "recommend_alternative": result.alternative_recommendations.append(action["value"])
                elif name == "select_result_template": result.result_template_key = action["template_key"]
                elif name == "set_outcome": result.outcome = action["value"]
                elif name == "stop_processing": return self._finalize(result, priorities)
                else: raise ValueError(f"Unsupported action: {name}")
            if rule.stop_processing: break
        return self._finalize(result, priorities)

    def _finalize(self, result: EvaluationResult, priorities: dict[str, int]) -> EvaluationResult:
        result.eligible_programs = [p for p in dict.fromkeys(result.eligible_programs) if p not in result.excluded_programs]
        if result.eligible_programs:
            result.recommended_program = sorted(result.eligible_programs, key=lambda p: priorities.get(p, 100))[0]
        return result
