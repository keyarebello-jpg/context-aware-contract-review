"""
rules_engine.py
---------------
Determines which regulatory rules are triggered by a given company profile
and contract context, then evaluates compliance against each triggered rule.

Design rationale:
  Compliance is conditional — GDPR applies only if personal data is processed,
  EU AI Act applies only in EU/EEA jurisdictions with high-risk AI, etc.

  We model this as a two-stage process:
    Stage 1: TRIGGER  — which rules *apply* to this company/contract?
    Stage 2: EVALUATE — for the triggered rules, does the contract satisfy them?

  This separation is important: it prevents false positives (flagging rules that
  simply don't apply) and makes the output legible to a lawyer reading the report.

  Trigger conditions are AND-logic across fields, OR-logic within each field.
  Example: jurisdiction must be in ["EU","EEA"] AND activity must be in [...]
"""

from typing import Any


# ---------------------------------------------------------------------------
# Stage 1: Trigger evaluation
# ---------------------------------------------------------------------------

def _check_trigger(
    condition_value: Any,
    profile_value: Any,
    field: str
) -> bool:
    """
    Evaluate a single trigger condition field.

    Rules:
      - If condition_value is a list, check if profile_value (or any element
        of profile_value if it's also a list) intersects with condition_value.
      - If condition_value is a bool, do a direct equality check.
      - If condition_value is a string, do a direct equality check.
    """
    if condition_value is None:
        return True  # No constraint on this field → always passes

    if isinstance(condition_value, list):
        # Profile value could be a single item or a list
        if isinstance(profile_value, list):
            return bool(set(profile_value) & set(condition_value))
        else:
            return profile_value in condition_value

    if isinstance(condition_value, bool):
        return profile_value == condition_value

    # String equality
    return str(profile_value).lower() == str(condition_value).lower()


def evaluate_trigger(
    rule: dict[str, Any],
    company_profile: dict[str, Any],
    contract: dict[str, Any]
) -> tuple[bool, list[str]]:
    """
    Evaluate whether a rule's trigger conditions are met.

    Returns (is_triggered, list_of_matched_conditions)

    We source values from both the company profile and contract, because some
    conditions (like jurisdiction) can come from either source. Contract
    jurisdiction takes precedence if present.
    """
    conditions = rule.get("trigger_conditions", {})
    matched = []
    failed = []

    # Build a unified lookup: merge profile + contract, contract wins on conflict
    context = {**company_profile}

    # Contract-level overrides
    contract_jurisdiction = contract.get("jurisdiction", "")
    if contract_jurisdiction:
        context["jurisdiction"] = contract_jurisdiction
        context["operational_jurisdiction"] = [contract_jurisdiction]

    # Map trigger condition keys to context lookup paths
    FIELD_MAPPING = {
        "jurisdiction": ["operational_jurisdiction", "jurisdiction", "primary_jurisdiction"],
        "activities": ["activities"],
        "sector": ["sector"],
        "ai_risk_category": ["ai_risk_category"],
        "processes_personal_data": ["processes_personal_data"],
        "uses_ai": ["uses_ai"],
        "public_procurement": ["public_procurement"],
        "clients_types": ["clients", "types"],
    }

    for condition_key, condition_value in conditions.items():
        # Resolve the profile value using field mapping
        if condition_key in FIELD_MAPPING:
            paths = FIELD_MAPPING[condition_key]
            profile_val = _resolve_nested(context, paths)
        else:
            profile_val = context.get(condition_key)

        if _check_trigger(condition_value, profile_val, condition_key):
            matched.append(condition_key)
        else:
            failed.append(condition_key)

    # Rule triggers only if ALL conditions match (AND logic across conditions)
    is_triggered = len(failed) == 0

    return is_triggered, matched


def _resolve_nested(data: dict, path: list[str]) -> Any:
    """
    Try to resolve a value from a dict using a list of possible key paths.
    Handles simple nested access (e.g., ["clients", "types"]).
    Returns the first successful resolution, or None.
    """
    # Try direct key first
    for key in path:
        if key in data:
            return data[key]

    # Try nested (two-level)
    if len(path) == 2:
        parent = data.get(path[0], {})
        if isinstance(parent, dict):
            return parent.get(path[1])

    return None


def filter_applicable_rules(
    regulations: dict[str, Any],
    company_profile: dict[str, Any],
    contract: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Return only the rules that are triggered by this company/contract context,
    enriched with metadata about why they were triggered.
    """
    applicable = []

    for rule in regulations.get("rules", []):
        triggered, matched_conditions = evaluate_trigger(rule, company_profile, contract)
        if triggered:
            applicable.append({
                **rule,
                "_trigger_matched_conditions": matched_conditions,
                "_triggered": True,
            })

    return applicable


# ---------------------------------------------------------------------------
# Stage 2: Compliance evaluation
# ---------------------------------------------------------------------------

def evaluate_compliance(
    rule: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    """
    For a triggered rule, evaluate whether the contract satisfies it.

    A rule is satisfied if ANY of the following is true:
      a) At least one required clause type is present in the contract.
      b) At least one required keyword is found in the contract's keyword hits.

    We require both checks to be considered 'satisfied' only if the rule has
    both required_clause_types and required_keywords — either signal is enough
    but the absence of both is a clear gap.

    Returns a result dict with:
      - satisfied: bool
      - evidence: list of what was found
      - gaps: list of what was missing
      - severity: inherited from rule
    """
    present_types = set(t.lower() for t in contract.get("all_present_types", []))
    keyword_hits = contract.get("keyword_hits", {})
    # Flatten all found keywords into one searchable set
    all_found_keywords: set[str] = set()
    for hit_list in keyword_hits.values():
        all_found_keywords.update(k.lower() for k in hit_list)

    required_clause_types = [t.lower() for t in rule.get("required_clause_types", [])]
    required_keywords = [k.lower() for k in rule.get("required_keywords", [])]

    # Check clause type presence
    found_clause_types = [ct for ct in required_clause_types if ct in present_types]
    missing_clause_types = [ct for ct in required_clause_types if ct not in present_types]

    # Check keyword presence
    found_keywords = [kw for kw in required_keywords if kw in all_found_keywords]
    missing_keywords = [kw for kw in required_keywords if kw not in all_found_keywords]

    # Satisfied if we found at least one clause type OR at least one keyword
    has_clause_evidence = len(found_clause_types) > 0
    has_keyword_evidence = len(found_keywords) > 0
    satisfied = has_clause_evidence or has_keyword_evidence

    evidence = []
    gaps = []

    if has_clause_evidence:
        evidence.append(f"Clause types present: {', '.join(found_clause_types)}")
    if has_keyword_evidence:
        evidence.append(f"Keywords found: {', '.join(found_keywords)}")

    if not has_clause_evidence and missing_clause_types:
        gaps.append(f"Missing clause types: {', '.join(missing_clause_types)}")
    if not has_keyword_evidence and missing_keywords:
        # Surface the top 3 most specific missing keywords to keep output readable
        top_missing = missing_keywords[:3]
        gaps.append(f"No signals for: {', '.join(top_missing)}")

    return {
        "rule_id": rule["rule_id"],
        "name": rule["name"],
        "regulation": rule["regulation"],
        "severity": rule["severity"],
        "satisfied": satisfied,
        "evidence": evidence,
        "gaps": gaps,
        "explanation": rule.get("explanation", ""),
        "trigger_conditions": rule.get("_trigger_matched_conditions", []),
    }


def run_rules_engine(
    regulations: dict[str, Any],
    company_profile: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    """
    Full rules engine pipeline.
    Returns a structured result with applicable rules and per-rule evaluations.
    """
    applicable_rules = filter_applicable_rules(regulations, company_profile, contract)
    evaluations = [evaluate_compliance(rule, contract) for rule in applicable_rules]

    satisfied = [e for e in evaluations if e["satisfied"]]
    failed = [e for e in evaluations if not e["satisfied"]]

    # Risk scoring: weight by severity
    severity_weights = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    max_possible = sum(severity_weights.get(e["severity"], 1) for e in evaluations)
    gap_score = sum(severity_weights.get(e["severity"], 1) for e in failed)
    risk_score = round((gap_score / max_possible) * 100) if max_possible > 0 else 0

    return {
        "total_applicable_rules": len(applicable_rules),
        "satisfied_count": len(satisfied),
        "gap_count": len(failed),
        "risk_score": risk_score,  # 0-100: higher = more gaps
        "satisfied": satisfied,
        "gaps": failed,
        "all_evaluations": evaluations,
    }
