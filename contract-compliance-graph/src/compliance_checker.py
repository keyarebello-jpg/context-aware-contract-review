"""
compliance_checker.py
---------------------
Orchestrates the full compliance analysis pipeline and produces a
structured, human-readable compliance report.

Design rationale:
  This is the glue layer. It calls the parser (to extract contract elements),
  the rules engine (to evaluate which rules apply and whether they're satisfied),
  and then formats everything into a compliance report.

  The report is designed to be useful to three audiences:
    1. Legal engineers — seeing which rules fired and why
    2. Lawyers — reading clear natural-language explanations per gap
    3. Product teams — seeing the risk score and prioritised action list
"""

import json
from datetime import datetime
from pathlib import Path

from src.parser import parse_contract, parse_company_profile, parse_regulations
from src.rules_engine import run_rules_engine


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_ICONS = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
RISK_LABELS = {
    (0, 20): ("LOW", "Contract is largely compliant with applicable regulations."),
    (21, 50): ("MEDIUM", "Material gaps exist. Legal review recommended before execution."),
    (51, 80): ("HIGH", "Significant compliance gaps. Contract should not be executed as-is."),
    (81, 100): ("CRITICAL", "Contract fails multiple critical regulatory requirements. Do not execute."),
}


def _risk_label(score):
    for (lo, hi), label in RISK_LABELS.items():
        if lo <= score <= hi:
            return label
    return ("UNKNOWN", "")


def run_compliance_check(
    contract_path,
    company_profile_path,
    regulations_path,):
    """
    Full pipeline: parse inputs → evaluate rules → structure report.

    Returns a rich compliance report dict.
    """
    # --- Parse all inputs ---
    contract = parse_contract(contract_path)
    company_profile = parse_company_profile(company_profile_path)
    regulations = parse_regulations(regulations_path)

    # --- Run rules engine ---
    engine_result = run_rules_engine(regulations, company_profile, contract)

    # --- Sort gaps by severity ---
    sorted_gaps = sorted(
        engine_result["gaps"],
        key=lambda x: SEVERITY_ORDER.get(x["severity"], 99)
    )
    sorted_satisfied = sorted(
        engine_result["satisfied"],
        key=lambda x: SEVERITY_ORDER.get(x["severity"], 99)
    )

    risk_score = engine_result["risk_score"]
    risk_level, risk_summary = _risk_label(risk_score)

    # --- Build the report ---
    report = {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "contract_id": contract["contract_id"],
            "contract_title": contract["title"],
            "company_name": company_profile.get("name", ""),
            "analysis_engine_version": "1.0.0",
        },
        "executive_summary": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_summary": risk_summary,
            "total_rules_evaluated": engine_result["total_applicable_rules"],
            "satisfied": engine_result["satisfied_count"],
            "gaps": engine_result["gap_count"],
            "contract_uses_ai": contract.get("uses_ai", False),
            "ai_indicators_found": contract.get("ai_indicators", []),
        },
        "company_context": {
            "name": company_profile.get("name"),
            "jurisdiction": company_profile.get("primary_jurisdiction"),
            "sector": company_profile.get("sector"),
            "activities": company_profile.get("activities", []),
            "uses_ai": company_profile.get("uses_ai"),
            "ai_risk_category": company_profile.get("ai_risk_category"),
            "processes_personal_data": company_profile.get("processes_personal_data"),
            "regulatory_exposure": company_profile.get("regulatory_exposure", {}),
        },
        "contract_elements": {
            "declared_clause_types": contract["declared_clause_types"],
            "inferred_clause_types": contract["inferred_clause_types"],
            "keyword_hits_summary": {
                k: v[:3] for k, v in contract["keyword_hits"].items()
            },
            "total_clauses": contract["total_clauses"],
        },
        "compliance_gaps": [
            {
                "rule_id": gap["rule_id"],
                "name": gap["name"],
                "regulation": gap["regulation"],
                "severity": gap["severity"],
                "severity_icon": SEVERITY_ICONS.get(gap["severity"], "⚪"),
                "gaps": gap["gaps"],
                "explanation": gap["explanation"],
                "triggered_by": gap["trigger_conditions"],
            }
            for gap in sorted_gaps
        ],
        "satisfied_requirements": [
            {
                "rule_id": req["rule_id"],
                "name": req["name"],
                "regulation": req["regulation"],
                "severity": req["severity"],
                "evidence": req["evidence"],
            }
            for req in sorted_satisfied
        ],
        "remediation_actions": _build_remediation_actions(sorted_gaps),
    }

    return report


def _build_remediation_actions(gaps):
    """
    Translate each gap into a concrete remediation action.
    Sorted by priority (critical first).
    """
    REMEDIATION_TEMPLATES = {
        "EU-AI-01": "Add a Human Oversight clause specifying that a qualified person must review AI outputs before they influence decisions. Reference EU AI Act Article 14.",
        "EU-AI-02": "Add an Audit Rights clause granting the client the right to audit system logs, model outputs, and incident records. Specify retention periods.",
        "EU-AI-03": "Add a Transparency clause requiring the vendor to provide technical documentation of the AI system, including its capabilities, limitations, and intended use.",
        "GDPR-01": "Execute a Data Processing Agreement (DPA) compliant with GDPR Article 28, or incorporate DPA terms directly into this contract.",
        "GDPR-02": "Add a Data Subject Rights clause specifying how the vendor will assist the client in responding to data subject access, erasure, and rectification requests within GDPR timeframes.",
        "PROC-01": "Add an Audit Rights clause granting the contracting authority and relevant oversight bodies the right to inspect records and audit performance.",
        "PROC-02": "Add a Business Continuity clause covering step-in rights, disaster recovery obligations, and service continuity in the event of vendor failure.",
        "AI-GOV-01": "Add a Change Notification clause requiring the vendor to notify the client of significant model updates, retraining events, or changes that may affect output quality or risk profile.",
        "AI-GOV-02": "Add a Bias and Fairness clause requiring regular bias assessments, disclosure of fairness metrics, and mitigation obligations for discriminatory outcomes.",
    }

    actions = []
    for i, gap in enumerate(gaps, 1):
        rule_id = gap["rule_id"]
        action_text = REMEDIATION_TEMPLATES.get(
            rule_id,
            f"Review contract against {gap['regulation']} requirements and add appropriate clause."
        )
        actions.append({
            "priority": i,
            "rule_id": rule_id,
            "severity": gap["severity"],
            "severity_icon": SEVERITY_ICONS.get(gap["severity"], "⚪"),
            "action": action_text,
        })

    return actions


def format_report_text(report):
    """
    Render the compliance report as a clean, readable text document.
    This is the primary human-readable output.
    """
    lines = []

    def h1(text): lines.append(f"\n{'=' * 70}\n{text}\n{'=' * 70}")
    def h2(text): lines.append(f"\n{'-' * 50}\n{text}\n{'-' * 50}")
    def line(text=""): lines.append(text)

    meta = report["report_metadata"]
    summary = report["executive_summary"]
    ctx = report["company_context"]

    h1("CONTRACT COMPLIANCE ANALYSIS REPORT")
    line(f"Generated:      {meta['generated_at']}")
    line(f"Contract ID:    {meta['contract_id']}")
    line(f"Contract Title: {meta['contract_title']}")
    line(f"Company:        {meta['company_name']}")
    line(f"Engine Version: {meta['analysis_engine_version']}")

    h2("EXECUTIVE SUMMARY")
    risk_icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(summary["risk_level"], "⚪")
    line(f"Risk Level:     {risk_icon} {summary['risk_level']}  (Score: {summary['risk_score']}/100)")
    line(f"Assessment:     {summary['risk_summary']}")
    line()
    line(f"Rules Evaluated:  {summary['total_rules_evaluated']}")
    line(f"  ✅ Satisfied:   {summary['satisfied']}")
    line(f"  ❌ Gaps Found:  {summary['gaps']}")
    line()
    if summary["ai_indicators_found"]:
        line(f"⚠️  AI Usage Detected: {', '.join(summary['ai_indicators_found'][:4])}")

    h2("COMPANY & CONTRACT CONTEXT")
    line(f"Jurisdiction:   {ctx['jurisdiction']}")
    line(f"Sector:         {ctx['sector']}")
    line(f"Activities:     {', '.join(ctx['activities'])}")
    line(f"Uses AI:        {'Yes' if ctx['uses_ai'] else 'No'}")
    line(f"AI Risk Class:  {ctx['ai_risk_category']}")
    line(f"Processes PII:  {'Yes' if ctx['processes_personal_data'] else 'No'}")
    line()
    line("Regulatory Exposure:")
    for reg, exposed in ctx["regulatory_exposure"].items():
        icon = "✓" if exposed else "✗"
        line(f"  {icon} {reg}")

    h2(f"COMPLIANCE GAPS ({len(report['compliance_gaps'])} found)")
    if not report["compliance_gaps"]:
        line("No compliance gaps found. Contract satisfies all applicable rules.")
    else:
        for gap in report["compliance_gaps"]:
            icon = gap["severity_icon"]
            line(f"\n{icon} [{gap['severity'].upper()}]  {gap['name']}")
            line(f"   Regulation: {gap['regulation']}")
            line(f"   Triggered by: {', '.join(gap['triggered_by'])}")
            for g in gap["gaps"]:
                line(f"   Gap: {g}")
            line(f"   Why this matters: {gap['explanation']}")

    h2(f"SATISFIED REQUIREMENTS ({len(report['satisfied_requirements'])} found)")
    if not report["satisfied_requirements"]:
        line("No requirements were satisfied.")
    else:
        for req in report["satisfied_requirements"]:
            line(f"  ✅ [{req['severity'].upper()}]  {req['name']}")
            for ev in req["evidence"]:
                line(f"      Evidence: {ev}")

    h2("REMEDIATION ACTIONS (Priority Order)")
    for action in report["remediation_actions"]:
        icon = action["severity_icon"]
        line(f"\n  {action['priority']}. {icon} [{action['severity'].upper()}]  Rule: {action['rule_id']}")
        line(f"     Action: {action['action']}")

    h1("END OF REPORT")
    return "\n".join(lines)


if __name__ == "__main__":
    base = Path(__file__).parent.parent / "data"
    report = run_compliance_check(
        base / "contract.json",
        base / "company_profile.json",
        base / "regulations.json",
    )
    print(format_report_text(report))
