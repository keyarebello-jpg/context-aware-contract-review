# Contract Compliance Graph

> Built as a prototype for Legal Engineer roles to demonstrate contract-aware, context-driven compliance systems.

> A rule-based compliance analysis system that reads a contract, maps it against company context and regulatory obligations, and surfaces gaps before they become liabilities.

---

## What this is (and why it matters)

Most legal tech tools are still in document generation mode - fill a template, output a PDF, done. That is the wrong mental model for compliance engineering.

**Compliance is a graph problem.**

A contract does not exist in isolation. Its obligations and its risks only become visible when you overlay three things:

1. What the contract says (the document)
2. Who is signing it (the company's regulatory profile)
3. What the law requires (the applicable rules)

A limitation of liability clause is unremarkable in a SaaS B2B contract. In a contract where an AI system is making public finance decisions in the EU, it becomes a compliance risk.

This project builds that graph.

---

## The architecture

```
contract.json          company_profile.json      regulations.json
      |                        |                        |
      v                        v                        v
  parser.py  ------------> rules_engine.py ----------->
  (extract clause           |
   types + keywords)        |
                            v
                    compliance_checker.py
                    (format + risk score)
                            |
                            v
                    Compliance Report
```

**Three-stage pipeline:**

| Stage    | Module                  | What it does                                                                            |
| -------- | ----------------------- | --------------------------------------------------------------------------------------- |
| Parse    | `parser.py`             | Extracts declared and inferred clause types from contract JSON using a keyword taxonomy |
| Trigger  | `rules_engine.py`       | Determines which regulatory rules apply based on company context                        |
| Evaluate | `rules_engine.py`       | Checks whether the contract satisfies each triggered rule                               |
| Report   | `compliance_checker.py` | Formats results with severity, evidence, and remediation actions                        |

---

## Why company context is the key input

Consider this rule from the EU AI Act:

```
IF activity = "AI_risk_scoring"
AND jurisdiction = "EU"
AND ai_risk_category = "high_risk"
THEN require: human_oversight + audit_rights + transparency
```

Without the company profile, you cannot evaluate this rule at all.

The contract clause is the *what*.
The company context is the *why it matters*.

This is what a **knowledge graph of a business** enables: structured, queryable context about a company's regulatory exposure that can be applied across contracts.

---

## Project structure

```
contract-compliance-graph/
├── README.md
├── main.py
├── data/
│   ├── contract.json
│   ├── company_profile.json
│   └── regulations.json
├── src/
│   ├── parser.py
│   ├── rules_engine.py
│   └── compliance_checker.py
├── app/
│   └── streamlit_app.py
└── requirements.txt
```

---

## Quick start

```bash
pip install -r requirements.txt
python3 main.py
streamlit run app/streamlit_app.py
```

---

## Example scenario

**Company:** QuantumRisk Analytics Ltd — an AI company providing credit risk scoring to public finance authorities in the EU.

**Contract:** A service agreement that covers scope, data processing, liability, IP, termination, and confidentiality.

**What the system finds:**

```
CONTRACT COMPLIANCE ANALYSIS REPORT

Risk Level: CRITICAL (Score: 100/100)
Assessment: Contract fails multiple critical regulatory requirements.

Rules Evaluated: 8
Satisfied: 0
Gaps Found: 8

AI Usage Detected: AI, machine learning, risk scoring

Missing:
- Human oversight clause
- Audit rights
- Transparency obligations
```

---

## How the rules work

Rules are defined in `data/regulations.json` as structured JSON:

```json
{
  "rule_id": "EU-AI-01",
  "name": "Human Oversight Clause",
  "trigger_conditions": {
    "jurisdiction": ["EU"],
    "activities": ["AI_risk_scoring"]
  },
  "required_clause_types": ["human_oversight"],
  "severity": "critical"
}
```

**Trigger logic:** AND across fields, OR within values
**Satisfaction logic:** Clause type OR keyword must be present

---

## Extending the system

| Task               | How                           |
| ------------------ | ----------------------------- |
| Add new regulation | Edit `regulations.json`       |
| Add new company    | Update `company_profile.json` |
| Add new contract   | Replace `contract.json`       |
| Add new keywords   | Edit `parser.py`              |

---

## Design principles

* **Separation of concerns** — parsing, logic, and reporting are modular
* **Rules as data** — legal logic lives in JSON, not code
* **Negative space matters** — missing clauses are explicitly tracked
* **Context-first evaluation** — rules only apply when triggered

---

## Tech stack

* Python 3
* JSON
* Optional: Streamlit

---

## Why this matters

This project demonstrates how:

* contracts can be made machine-readable
* company context can inform legal analysis
* compliance can be evaluated dynamically

It reflects the shift toward:

* contract intelligence
* legal knowledge graphs
* real-time compliance systems

---

## Note

This project uses:

* publicly available contract templates
* simulated company profiles

It is intended as a conceptual prototype.
