"""
parser.py
---------
Extracts and enriches structured elements from the raw contract JSON.

Design rationale:
  A contract is unstructured text masquerading as structured data. Our job here
  is to surface latent structure — what clause types exist, what keywords are
  present, what is conspicuously absent. We treat this as a light NLP pass:
  no ML, just pattern matching against a legal vocabulary.

  Crucially, we also run a 'negative space' extraction — identifying clause
  types that are MISSING. Compliance gaps are often found in what a contract
  *doesn't* say, not what it does.
"""

import json
import re
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Keyword taxonomy — maps legal concepts to their natural language signals
# ---------------------------------------------------------------------------

CLAUSE_KEYWORDS: dict[str, list[str]] = {
    "audit_rights": [
        "audit", "right to audit", "inspection", "audit trail",
        "access to records", "record keeping", "logging", "audit rights"
    ],
    "human_oversight": [
        "human oversight", "human review", "human-in-the-loop",
        "manual review", "human intervention", "human supervision",
        "qualified person", "responsible person"
    ],
    "data_processing": [
        "data processing", "personal data", "data controller",
        "data processor", "GDPR", "data subject", "lawful basis"
    ],
    "data_processing_agreement": [
        "data processing agreement", "DPA", "controller", "processor",
        "data subject rights", "sub-processor", "Article 28"
    ],
    "data_subject_rights": [
        "data subject rights", "right to access", "right to erasure",
        "right to rectification", "data subject request", "right to object"
    ],
    "transparency": [
        "transparency", "explainability", "explain", "model documentation",
        "technical documentation", "system limitations", "interpretability"
    ],
    "model_documentation": [
        "model documentation", "technical specification", "algorithm documentation",
        "model card", "system documentation"
    ],
    "ai_usage": [
        "artificial intelligence", "machine learning", "AI", "ML model",
        "neural network", "automated decision", "algorithm", "predictive model",
        "AI system", "automated scoring"
    ],
    "liability": [
        "liability", "limitation of liability", "indemnity", "indemnification",
        "cap on liability", "consequential damages", "direct damages"
    ],
    "bias_assessment": [
        "bias", "fairness", "discrimination", "equitable", "bias testing",
        "algorithmic fairness", "disparate impact"
    ],
    "model_change_notification": [
        "model update", "model change", "algorithm change", "change notification",
        "material change", "version control", "model version"
    ],
    "step_in_rights": [
        "step-in", "step in", "step in rights", "business continuity",
        "service continuity", "disaster recovery", "continuity plan"
    ],
    "confidentiality": [
        "confidential", "confidentiality", "non-disclosure", "NDA",
        "proprietary information", "trade secret"
    ],
    "intellectual_property": [
        "intellectual property", "IP rights", "ownership", "license",
        "copyright", "proprietary"
    ],
}

AI_INDICATOR_KEYWORDS: list[str] = [
    "artificial intelligence", "machine learning", "AI", "ML",
    "neural network", "automated decision", "algorithm", "predictive",
    "risk scoring", "scoring model", "classification model"
]


def load_json(path):
    """Load and parse a JSON file, raising clearly if it fails."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _text_contains(text: str, keywords: list[str]) -> list[str]:
    """Return which keywords from a list are found in the text (case-insensitive)."""
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def extract_clause_types(contract: dict[str, Any]) -> dict[str, Any]:
    """
    Walk every clause in the contract and:
      1. Record the declared clause type (from the JSON field).
      2. Scan the clause text for keyword signals of *other* clause types.
      3. Flag whether AI is mentioned anywhere in the contract.

    Returns an enriched structure with:
      - present_clause_types: set of all types found
      - keyword_hits: mapping of clause_type -> list of matching keywords found
      - ai_indicators: keywords that signal AI usage
      - clause_index: full text indexed by clause id
    """
    clauses = contract.get("clauses", [])

    declared_types: set[str] = set()
    keyword_hits: dict[str, list[str]] = {}
    ai_indicators_found: list[str] = []
    clause_index: dict[str, dict] = {}

    for clause in clauses:
        cid = clause.get("id", "UNKNOWN")
        ctype = clause.get("type", "").lower()
        text = clause.get("text", "") + " " + clause.get("title", "")

        declared_types.add(ctype)
        clause_index[cid] = clause

        # Scan clause text against every keyword category
        for category, keywords in CLAUSE_KEYWORDS.items():
            hits = _text_contains(text, keywords)
            if hits:
                if category not in keyword_hits:
                    keyword_hits[category] = []
                keyword_hits[category].extend(hits)

        # Separately track AI indicators
        ai_hits = _text_contains(text, AI_INDICATOR_KEYWORDS)
        ai_indicators_found.extend(ai_hits)

    # Deduplicate
    for k in keyword_hits:
        keyword_hits[k] = list(set(keyword_hits[k]))
    ai_indicators_found = list(set(ai_indicators_found))

    # Derive inferred types from keyword hits
    # (e.g. a clause labelled "scope_of_services" might contain audit language)
    inferred_types = set(keyword_hits.keys())
    all_present_types = declared_types | inferred_types

    return {
        "declared_clause_types": list(declared_types),
        "inferred_clause_types": list(inferred_types),
        "all_present_types": list(all_present_types),
        "keyword_hits": keyword_hits,
        "ai_indicators": ai_indicators_found,
        "uses_ai": len(ai_indicators_found) > 0,
        "clause_index": clause_index,
        "total_clauses": len(clauses),
    }


def identify_missing_clauses(
    extracted,
    required_types: list[str]
) -> list[str]:
    """
    Given a list of required clause types, return those that are absent
    from the contract (both declared and keyword-inferred).
    """
    present = set(t.lower() for t in extracted["all_present_types"])
    return [rt for rt in required_types if rt.lower() not in present]


def parse_contract(contract_path):
    """
    Full parse pipeline for a contract file.
    Returns an enriched representation ready for the rules engine.
    """
    contract = load_json(contract_path)
    extracted = extract_clause_types(contract)

    return {
        "raw": contract,
        "contract_id": contract.get("contract_id", "UNKNOWN"),
        "title": contract.get("title", ""),
        "jurisdiction": contract.get("jurisdiction", ""),
        "parties": contract.get("parties", {}),
        **extracted,
    }


def parse_company_profile(profile_path):
    """Load and lightly validate the company profile."""
    profile = load_json(profile_path)

    # Flatten nested booleans for easier rule matching
    tech = profile.get("technology_profile", {})
    profile["uses_ai"] = tech.get("uses_ai", False)
    profile["processes_personal_data"] = tech.get("processes_personal_data", False)
    profile["ai_risk_category"] = tech.get("ai_risk_category", "unknown")
    profile["cross_border_data_transfer"] = tech.get("cross_border_data_transfer", False)

    return profile


def parse_regulations(reg_path):
    """Load the regulatory ruleset."""
    return load_json(reg_path)


if __name__ == "__main__":
    # Quick smoke test
    base = Path(__file__).parent.parent / "data"
    contract = parse_contract(base / "contract.json")
    profile = parse_company_profile(base / "company_profile.json")
    regs = parse_regulations(base / "regulations.json")

    print(f"Contract: {contract['contract_id']}")
    print(f"Clause types found: {contract['all_present_types']}")
    print(f"AI indicators: {contract['ai_indicators']}")
    print(f"Company uses AI: {profile['uses_ai']}")
    print(f"Rules loaded: {len(regs['rules'])}")
