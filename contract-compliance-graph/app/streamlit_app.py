from pathlib import Path
import streamlit as st


st.set_page_config(
    page_title="Context-Aware Contract Review",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */
    .stApp {
        background-color: #FFFFFF;
        color: #111827;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 3.2rem;
        padding-bottom: 2.2rem;
    }

    .stApp p,
    .stApp li,
    .stApp label,
    .stApp div,
    .stMarkdown,
    .stText {
        color: #111827;
    }

    /* remove excess top chrome spacing effects */
    header[data-testid="stHeader"] {
        background: transparent;
        height: 0.5rem;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background-color: #223A2E;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        color: #F7F7F3 !important;
    }

    /* ---------- TYPOGRAPHY ---------- */
    .hero-title {
        font-size: 2.3rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.08;
        margin-top: 0;
        margin-bottom: 0.35rem;
        color: #111827;
    }

    .hero-subtitle {
        font-size: 1rem;
        line-height: 1.65;
        color: #4B5563;
        max-width: 780px;
        margin-bottom: 1.25rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-top: 1.15rem;
        margin-bottom: 0.65rem;
        color: #223A2E;
    }

    .body-copy {
        font-size: 0.98rem;
        line-height: 1.72;
        color: #111827;
    }

    .divider-space {
        height: 0.22rem;
    }

    /* ---------- GREEN BLOCK HEADERS ---------- */
    .green-header {
        background-color: #223A2E;
        color: #FFFFFF !important;
        padding: 0.72rem 0.9rem;
        border-radius: 12px 12px 0 0;
        font-size: 0.98rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        margin-bottom: 0;
    }

    .green-section-card {
        border: 1px solid #E5E7EB;
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 0.95rem 1rem;
        background: #FFFFFF;
        margin-bottom: 1rem;
    }

    /* ---------- CARDS ---------- */
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 1rem 1.05rem;
        box-shadow: 0 2px 10px rgba(17, 24, 39, 0.03);
        margin-bottom: 0.85rem;
        color: #111827;
    }

    .small-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #6B7280;
        margin-bottom: 0.2rem;
    }

    .big-value {
        font-size: 1.08rem;
        font-weight: 600;
        line-height: 1.28;
        color: #111827;
    }

    .assessment-box {
        background: #FAFAF9;
        border: 1px solid #D1D5DB;
        border-radius: 14px;
        padding: 1rem 1.05rem;
        margin-bottom: 1rem;
    }

    /* ---------- TABLE ---------- */
    .mapping-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 0.45rem;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }

    .mapping-table th,
    .mapping-table td {
        border: 1px solid #E5E7EB;
        padding: 0.78rem 0.82rem;
        vertical-align: top;
        text-align: left;
        color: #111827;
    }

    .mapping-table th {
        background: #F9FAFB;
        color: #223A2E;
        font-weight: 600;
    }

    /* ---------- BUTTON ---------- */
    .stButton > button {
        background-color: #223A2E;
        color: white !important;
        border: 1px solid #223A2E;
        border-radius: 10px;
        padding: 0.52rem 0.95rem;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: #1B2F25;
        border-color: #1B2F25;
        color: white !important;
    }

    /* ---------- INFO ---------- */
    [data-testid="stInfo"] {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        color: #111827 !important;
    }

    /* ---------- EXPANDERS / TABS ---------- */
    details summary {
        color: #111827 !important;
    }

    button[role="tab"] {
        color: #223A2E !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## Context-Aware Contract Review")
    page = st.radio(
        "Navigation",
        [
            "About",
            "OSINT Profile",
            "Sample Contract",
            "Regulatory Mapping",
            "Analysis & Findings",
            "OSINT-Informed Drafting",
        ],
        label_visibility="collapsed",
    )


def hero(title, subtitle):
    st.markdown(f"<div class='hero-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)


def body(text):
    st.markdown(f"<div class='body-copy'>{text}</div>", unsafe_allow_html=True)


def card(label, value):
    st.markdown(
        f"""
        <div class="card">
            <div class="small-label">{label}</div>
            <div class="big-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def green_block(title, items):
    st.markdown(f"<div class='green-header'>{title}</div>", unsafe_allow_html=True)
    st.markdown("<div class='green-section-card'>", unsafe_allow_html=True)
    for item in items:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)


def about_page():
    hero(
        "Context-Aware Contract Review",
        "A legal engineering prototype that connects contract text, structured company context, and regulatory logic to identify compliance gaps in a way that is explainable, usable, and grounded in real-world drafting.",
    )

    left, right = st.columns([1.45, 0.95], gap="large")

    with left:
        section("About Me")
        body(
            "Keya Rebello is a legal researcher at the Cambridge Centre for Alternative Finance working on AI governance, digital public infrastructure, and regulatory design, with a focus on translating complex legal frameworks into structured, actionable systems."
        )
        st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
        body(
            "Her work focuses on how regulatory systems interact with real-world implementation, particularly in public-sector contexts involving data-sharing, financial infrastructure, and AI-enabled decision-making."
        )

        section("What This Project Does")
        body(
            "This project takes three inputs: a contract, a structured company profile derived from OSINT-style analysis, and a set of regulatory rules. It evaluates which regulatory obligations apply to the company, and whether those obligations are reflected in the contract. Where they are not, it surfaces specific compliance gaps and prioritised drafting interventions."
        )

        section("Core Idea")
        body(
            "Compliance is not a document-level problem. It is a context-dependent evaluation. A contract that appears complete in isolation may be non-compliant when assessed against the company’s actual activities, jurisdictional footprint, use of infrastructure, and exposure to sector-specific regulation."
        )

    with right:
        section("System Logic")
        st.markdown(
            """
            <div class="card">
                1. Extract clause types and signals from the contract<br><br>
                2. Map company attributes, including jurisdiction, sector, activities, and infrastructure role<br><br>
                3. Determine which regulatory rules apply<br><br>
                4. Evaluate whether required clauses are present<br><br>
                5. Surface gaps and generate drafting recommendations
            </div>
            """,
            unsafe_allow_html=True,
        )

        section("Why This Matters")
        body(
            "Contracts are often drafted using templates that assume a generic counterparty. In practice, regulatory risk is shaped by the counterparty’s actual operating profile. This project demonstrates how that gap can be made visible, structured, and actionable."
        )

        section("Positioning")
        body(
            "This is a prototype for legal engineering workflows involving contract intelligence, regulatory mapping, OSINT-informed analysis, and context-aware drafting."
        )


def osint_page():
    hero(
        "OSINT Profile",
        "A contract-relevant OSINT map of a hypothetical fintech infrastructure provider, focusing on the operational characteristics and risk signals that shape regulatory exposure.",
    )

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        card("Company", "EuroFlow Infrastructure GmbH")
    with c2:
        card("Primary Jurisdiction", "European Union (Germany)")
    with c3:
        card("Sector", "Fintech Infrastructure")

    left, right = st.columns(2, gap="large")
    with left:
        green_block(
            "Core Systems",
            [
                "Real-time payment processing infrastructure (SEPA Instant)",
                "Open banking API aggregation for regulated institutions",
                "Account-to-account payment routing systems",
                "Fraud detection and transaction monitoring systems",
                "Digital identity verification and KYC orchestration",
                "Cross-border settlement and reconciliation infrastructure",
                "Data-sharing infrastructure for financial institutions",
            ],
        )

    with right:
        green_block(
            "Integration Points",
            [
                "Regulated banks and financial institutions",
                "Public treasury and public finance authorities",
                "Fintech platforms and payment service providers",
                "Cloud infrastructure providers",
                "Identity verification vendors",
                "Payment scheme operators",
            ],
        )

    green_block(
        "OSINT-Derived Risk Signals",
        [
            "Cross-border operations across multiple EU jurisdictions",
            "High-volume processing of personal and financial data",
            "Reliance on third-party banking and infrastructure partners",
            "Use of machine learning in fraud detection systems",
            "Exposure to public-sector or regulated financial clients",
            "Operational dependence on uptime, resilience, and system availability",
        ],
    )

    green_block(
        "Regulatory Exposure",
        [
            "General Data Protection Regulation (GDPR)",
            "Payment Services Directive (PSD2)",
            "Digital Operational Resilience Act (DORA)",
            "Anti-Money Laundering and KYC Regulations",
            "Cross-border data transfer requirements",
        ],
    )

    section("General Notes")
    body(
        "The purpose of this map is to identify the aspects of a counterparty’s operations that are relevant to risk, rather than to provide a purely descriptive account of corporate structure."
    )


def sample_contract_page():
    hero(
        "Sample Contract",
        "A hypothetical services agreement between a public finance authority and a fintech infrastructure provider. The contract is commercially plausible on its face, but intentionally drafted without several protections that become important once the counterparty’s operational profile is understood.",
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        card("Contract Title", "Public Finance Payment Infrastructure Services Agreement")
        card("Parties", "European Public Treasury Authority and EuroFlow Infrastructure GmbH")
    with c2:
        card("Jurisdiction", "European Union (Germany)")
        card("Contract Type", "Fintech Infrastructure / Payment Services Agreement")

    section("Purpose of the Agreement")
    body(
        "This agreement governs the provision of payment processing and financial data infrastructure services by EuroFlow Infrastructure GmbH to a public authority responsible for disbursement, reconciliation, and treasury-facing financial operations."
    )
    st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
    body(
        "The vendor will provide infrastructure to support account-to-account payment routing, API-based payment initiation, transaction monitoring, and reconciliation support for public finance workflows."
    )

    section("Key Contract Terms")

    clauses = [
        (
            "1. Scope of Services",
            "The vendor will provide payment infrastructure services, including transaction routing, payment initiation support, reconciliation tools, and related technical support services.",
        ),
        (
            "2. Data Processing",
            "The vendor may process financial and personal data to the extent necessary for performance of the services and will comply with applicable data protection law.",
        ),
        (
            "3. Fees and Payment",
            "The authority will pay the vendor the agreed service fees in accordance with the pricing schedule set out in the commercial annex.",
        ),
        (
            "4. Confidentiality",
            "Each party will keep confidential all non-public business, technical, and financial information received from the other party and will not disclose such information except as required by law.",
        ),
        (
            "5. Liability",
            "The vendor’s liability under this agreement is limited to direct losses and capped at the total fees paid under the agreement in the twelve months preceding the relevant claim.",
        ),
        (
            "6. Service Availability",
            "The vendor will use commercially reasonable efforts to maintain availability of the payment infrastructure services and provide notice of material service interruptions.",
        ),
        (
            "7. Termination",
            "Either party may terminate the agreement for material breach if such breach is not remedied within thirty days of written notice.",
        ),
        (
            "8. Intellectual Property",
            "All intellectual property rights in the vendor’s systems, software, documentation, and underlying infrastructure remain vested in the vendor.",
        ),
    ]

    for title, text in clauses:
        with st.expander(title):
            st.write(text)

    section("How to Read This Contract")
    body(
        "This contract is designed to appear professionally drafted and commercially usable. It includes the kinds of provisions commonly found in technology services agreements."
    )

    section("General Notes")
    st.write("- Commercial scope")
    st.write("- Data processing at a high level")
    st.write("- Confidentiality")
    st.write("- Liability allocation")
    st.write("- Service availability")
    st.write("- Termination")
    st.write("- Intellectual property")
    st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
    body(
        "At the same time, it does not yet reflect the fuller implications of the counterparty’s operational profile, cross-border activities, infrastructure role, and regulatory exposure. Those issues are surfaced in the later pages of the project."
    )


def regulatory_mapping_page():
    hero(
        "Regulatory Mapping",
        "A structured mapping of regulatory frameworks relevant to a fintech infrastructure provider operating in the European Union, linking legal obligations to the types of contractual provisions typically required to address them.",
    )

    st.markdown(
        """
        <table class="mapping-table">
            <thead>
                <tr>
                    <th>Regulation</th>
                    <th>Trigger (from company profile)</th>
                    <th>Typical Contractual Requirement</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>GDPR (General Data Protection Regulation)</strong></td>
                    <td>Processing of personal and financial data</td>
                    <td>Data Processing Agreement, data subject rights support, breach notification obligations</td>
                </tr>
                <tr>
                    <td><strong>PSD2 (Payment Services Directive)</strong></td>
                    <td>Payment initiation and account-to-account infrastructure</td>
                    <td>Security standards, authentication requirements, liability allocation for unauthorised transactions</td>
                </tr>
                <tr>
                    <td><strong>DORA (Digital Operational Resilience Act)</strong></td>
                    <td>Provision of critical digital infrastructure to financial entities</td>
                    <td>Incident reporting, resilience obligations, ICT risk management, outsourcing controls</td>
                </tr>
                <tr>
                    <td><strong>AML / KYC Regulations</strong></td>
                    <td>Identity verification and transaction monitoring</td>
                    <td>Customer due diligence obligations, reporting cooperation, data retention requirements</td>
                </tr>
                <tr>
                    <td><strong>Cross-border Data Transfer Rules</strong></td>
                    <td>Operations across multiple EU jurisdictions</td>
                    <td>Data transfer mechanisms, localisation safeguards, regulatory cooperation clauses</td>
                </tr>
                <tr>
                    <td><strong>Public Procurement / Public Finance Requirements</strong></td>
                    <td>Provision of infrastructure to public authorities</td>
                    <td>Audit rights, transparency obligations, service continuity, reporting requirements</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    section("How to Read It")
    body(
        "Each row reflects a regulatory framework triggered by the company’s activities and operating context. The third column identifies the categories of contractual provisions typically used to translate those regulatory obligations into enforceable terms."
    )

    section("General Notes")
    body(
        "This mapping is intentionally simplified and does not attempt to exhaustively set out the full legal requirements of each regime. Instead, it highlights the contractual architecture that would ordinarily be expected for a counterparty with this operational profile."
    )


def analysis_page():
    hero(
        "Analysis & Findings",
        "A context-aware evaluation of the contract against the company’s operational profile and applicable regulatory frameworks.",
    )

    st.markdown(
        """
        <div class="assessment-box">
            <div class="section-title" style="margin-top:0; margin-bottom:0.75rem;">Overall Assessment</div>
            <div style="display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 0.8rem;">
                <div class="card">
                    <div class="small-label">Alignment Level</div>
                    <div class="big-value">Low</div>
                </div>
                <div class="card">
                    <div class="small-label">Regulatory Sensitivity</div>
                    <div class="big-value">High</div>
                </div>
                <div class="card">
                    <div class="small-label">Contract Coverage</div>
                    <div class="big-value">Partial</div>
                </div>
            </div>
            <div class="body-copy" style="margin-top:0.8rem;">
                This contract is commercially coherent but does not fully reflect the regulatory and operational implications associated with the counterparty’s role as a cross-border fintech infrastructure provider.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    body(
        "This analysis evaluates the contract against the company profile and regulatory mapping to identify where contractual provisions may not fully reflect the counterparty’s operational and regulatory context."
    )

    if st.button("Run Analysis", use_container_width=True):
        st.session_state["analysis_ran"] = True

    if st.session_state.get("analysis_ran"):
        section("Executive Summary")
        body(
            "The contract is commercially coherent and includes core provisions typically found in technology services agreements. However, when evaluated against the counterparty’s operational profile as a cross-border fintech infrastructure provider, several areas of contractual coverage are not aligned with the level of regulatory exposure and operational dependency involved."
        )
        st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
        body(
            "The analysis below highlights where the contract does not fully reflect the implications of cross-border financial infrastructure operations, processing of personal and financial data, reliance on third-party providers, and provision of infrastructure to public authorities."
        )

        section("Key Findings")
        findings = [
            (
                "1. Data Processing and Cross-Border Operations",
                "The contract includes a general data processing provision, but it does not reflect the complexity associated with cross-border financial data flows or the level of regulatory scrutiny applicable to such operations.\n\nThe current drafting does not address structured data processing obligations, cross-border transfer considerations, or interaction with data subject rights.",
            ),
            (
                "2. Infrastructure Role and Service Criticality",
                "The contract treats service availability at a general level, using a 'commercially reasonable efforts' standard.\n\nGiven the counterparty’s role in payment infrastructure supporting public finance operations, this does not fully reflect operational criticality, dependency on system availability, or expectations around resilience and continuity.",
            ),
            (
                "3. Third-Party Dependencies",
                "The operational model relies on integrations with banks, cloud providers, and identity services.\n\nThe contract does not explicitly address subcontracting controls, third-party oversight, or flow-down of obligations.",
            ),
            (
                "4. Public Sector Context",
                "The contract is structured as a standard commercial agreement and does not fully reflect the additional accountability typically associated with public-sector engagements.\n\nThis includes auditability, transparency, and reporting expectations.",
            ),
            (
                "5. Regulatory Alignment",
                "While the contract is broadly consistent with general commercial standards, it does not explicitly map to the regulatory frameworks triggered by the company’s activities.\n\nThis results in a gap between the regulatory environment in which the services operate and the contractual mechanisms used to allocate and manage risk.",
            ),
        ]

        for title, text in findings:
            with st.expander(title):
                st.write(text)

        section("Interpretation")
        body(
            "The observations above do not indicate that the contract is defective in a general commercial sense. Rather, they show that the contract has been drafted without full reference to the counterparty’s specific operational and regulatory context."
        )
        st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
        body(
            "This distinction is important: a contract can appear complete when assessed in isolation, but incomplete when evaluated against the realities of how the services are delivered and regulated."
        )

        section("General Notes")
        body(
            "Traditional contract analysis identifies gaps by comparing a document against general legal standards. This analysis extends that approach by incorporating structured context about the counterparty, allowing contractual expectations to be shaped by actual operational and regulatory exposure."
        )
        st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
        body(
            "The following section translates these observations into specific drafting considerations, showing how the contract could be adapted to better reflect the counterparty’s profile."
        )
    else:
        st.info("Click Run Analysis to display the findings.")


def drafting_page():
    hero(
        "OSINT-Informed Drafting",
        "Illustrative redline-style revisions showing how contractual provisions can be adapted when the counterparty’s operational profile and regulatory exposure are taken into account.",
    )

    body(
        "This section translates the observations from the analysis into concrete drafting adjustments. The examples below are not exhaustive, but demonstrate how contract language changes when informed by structured context about the counterparty."
    )

    revisions = [
        (
            "1. Data Processing Clause",
            "The vendor may process financial and personal data to the extent necessary for performance of the services and will comply with applicable data protection law.",
            "The vendor shall process personal and financial data strictly in accordance with applicable data protection law, including Regulation (EU) 2016/679 (GDPR).\n\nThe parties shall enter into a data processing agreement incorporating the requirements of Article 28 GDPR, including provisions addressing data subject rights, sub-processing, and security measures.\n\nThe vendor shall notify the authority without undue delay of any personal data breach and, where applicable, in sufficient time to enable the authority to comply with its obligation to notify supervisory authorities within 72 hours.\n\nWhere personal data is transferred across jurisdictions, the vendor shall implement appropriate safeguards, including recognised transfer mechanisms.",
        ),
        (
            "2. Service Availability / Infrastructure Clause",
            "The vendor will use commercially reasonable efforts to maintain availability of the payment infrastructure services.",
            "The vendor shall ensure the availability of the payment infrastructure services in accordance with defined service levels, including minimum uptime thresholds and response and recovery targets to be set out in a service level schedule.\n\nThe vendor shall maintain and regularly test business continuity and disaster recovery plans appropriate to the criticality of the services.\n\nAny material service disruption shall be promptly notified to the authority together with details of remedial action.",
        ),
        (
            "3. Subcontracting and Third-Party Dependencies",
            "No clause currently addresses subcontractor use, third-party dependencies, or equivalent obligations flowing through the supply chain.",
            "The vendor shall not engage subcontractors in connection with the services without prior written consent of the authority.\n\nThe vendor shall notify the authority of any intended changes to subcontractors and provide sufficient information to enable the authority to assess the impact of such changes.\n\nThe vendor shall remain fully responsible for the acts and omissions of any subcontractors and shall ensure that all subcontractors are subject to obligations equivalent to those set out in this agreement.",
        ),
        (
            "4. Audit Rights",
            "No clause currently grants the authority, or relevant supervisory bodies, a contractual right to inspect records, systems, or compliance controls.",
            "The authority, and any relevant regulatory or supervisory body, shall have the right, on reasonable notice, to audit the vendor’s compliance with this agreement.\n\nRoutine audits shall be conducted on not less than 10 business days’ notice, except where shorter notice is required in connection with regulatory requirements or suspected breaches.\n\nThe vendor shall cooperate fully with such audits and shall implement a remediation plan within a reasonable timeframe to address any material findings.",
        ),
        (
            "5. Liability Clause",
            "The vendor’s liability under this agreement is limited to direct losses and capped at the total fees paid under the agreement in the twelve months preceding the relevant claim.",
            "The vendor’s liability under this agreement shall be subject to agreed financial caps set out in the commercial schedule.\n\nThe limitation of liability shall not apply to losses arising from fraud, wilful misconduct, breach of data protection obligations, or failure to comply with applicable regulatory requirements.\n\nThe parties shall ensure that liability thresholds appropriately reflect the nature of the services and the potential impact of service failure.",
        ),
        (
            "6. Public Sector / Regulatory Cooperation",
            "No clause currently addresses the vendor’s obligation to cooperate with public-sector audit, reporting, or regulatory inquiries.",
            "The vendor shall cooperate with the authority in complying with applicable legal and regulatory obligations, including those relating to public financial management, audit, and reporting.\n\nThe vendor shall maintain records sufficient to demonstrate compliance with this agreement and shall provide such information and assistance as may be reasonably required by the authority or competent regulators.",
        ),
    ]

    for title, current, revised in revisions:
        with st.expander(title):
            left, right = st.columns(2, gap="large")
            with left:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("**Current Draft**")
                st.write(current)
                st.markdown("</div>", unsafe_allow_html=True)
            with right:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("**OSINT-Informed Revision**")
                st.write(revised)
                st.markdown("</div>", unsafe_allow_html=True)

    section("General Notes")
    body(
        "These revisions illustrate that contractual drafting is shaped not only by general legal standards, but by the specific operational profile of the counterparty."
    )
    st.markdown("<div class='divider-space'></div>", unsafe_allow_html=True)
    body(
        "While automated tools can identify gaps against standard expectations, incorporating structured context, including operational dependencies, cross-border exposure, and regulatory positioning, allows those expectations to be refined and applied more precisely."
    )


if page == "About":
    about_page()
elif page == "OSINT Profile":
    osint_page()
elif page == "Sample Contract":
    sample_contract_page()
elif page == "Regulatory Mapping":
    regulatory_mapping_page()
elif page == "Analysis & Findings":
    analysis_page()
elif page == "OSINT-Informed Drafting":
    drafting_page()