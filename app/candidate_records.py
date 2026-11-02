"""Build reviewable candidate records from the existing CV extractors."""

import re
from pathlib import Path

if __package__:
    from .classification_engine import classify_candidate
    from .certification_extractor import extract_certifications
    from .date_normalizer import normalize_employment_result
    from .education_extractor import extract_education
    from .employment_extractor import extract_employment_history
    from .experience_calculator import calculate_experience
    from .pre_ai import run_pre_ai
    from .technology_extractor import extract_technology_evidence
else:
    from classification_engine import classify_candidate
    from certification_extractor import extract_certifications
    from date_normalizer import normalize_employment_result
    from education_extractor import extract_education
    from employment_extractor import extract_employment_history
    from experience_calculator import calculate_experience
    from pre_ai import run_pre_ai
    from technology_extractor import extract_technology_evidence


OUTPUT_COLUMNS = [
    "Candidate",
    "Email",
    "Phone",
    "Domain",
    "Experience",
    "Level",
    "Location",
    "Key Skills",
    "OEMs",
    "Certifications",
    "Status",
    "Department",
    "Degree/Education",
    "Validity of information",
    "Industry",
    "Specialization / Subdomain",
    "Career Function",
    "Software Stack",
]

BUSINESS_DEPARTMENTS = [
    (
        "Human Resources",
        re.compile(
            r"\b(?:human resources?|hr|recruit(?:er|ment|ing)?|"
            r"talent acquisition|employee relations|hr operations)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Procurement",
        re.compile(
            r"\b(?:procurement|purchasing|buyer|sourcing)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Logistics & Supply Chain",
        re.compile(
            r"\b(?:supply chain|logistics|logistician|dispatch)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Inventory & Warehouse",
        re.compile(
            r"\b(?:inventory|warehouse|stock controller|stores officer)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Processing",
        re.compile(
            r"\b(?:processing|process operator|processing assistant)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Finance & Accounting",
        re.compile(
            r"\b(?:finance|account(?:ant|ing|s)?|accounts payable|"
            r"accounts receivable|bookkeeper|payroll)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Legal & Compliance",
        re.compile(
            r"\b(?:legal counsel|legal advisor|lawyer|attorney|"
            r"compliance officer|compliance analyst|contract specialist|"
            r"corporate governance)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Auditing & Compliance",
        re.compile(
            r"\b(?:auditor|auditing|internal audit|external audit)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Sales",
        re.compile(r"\b(?:sales|business development)\b", re.IGNORECASE),
    ),
    (
        "Marketing",
        re.compile(r"\bmarketing\b", re.IGNORECASE),
    ),
    (
        "Project Management",
        re.compile(r"\bproject manager|project management\b", re.IGNORECASE),
    ),
    (
        "Administration & Facilities",
        re.compile(
            r"\b(?:administrative|administration|admin assistant|"
            r"office assistant|office manager)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Administration & Facilities",
        re.compile(
            r"\b(?:facilities? manager|facilities? coordinator|"
            r"facility engineer|office facilities)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Customer Support / Success",
        re.compile(
            r"\b(?:customer support|customer success|customer service|"
            r"client support|customer experience)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Research & Development",
        re.compile(
            r"\b(?:research and development|research & development|"
            r"\br&d\b|research scientist|research engineer|"
            r"product researcher)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Production / Manufacturing",
        re.compile(
            r"\b(?:production manager|production supervisor|"
            r"manufacturing engineer|manufacturing supervisor|"
            r"assembly line|factory operations)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Quality Assurance",
        re.compile(
            r"\b(?:quality assurance|quality control|qa engineer|"
            r"qc inspector|quality inspector|software tester)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "Operations",
        re.compile(r"\boperations?\b", re.IGNORECASE),
    ),
    (
        "Coordination",
        re.compile(r"\bcoordinator\b", re.IGNORECASE),
    ),
]

TECHNICAL_DOMAIN_TITLES = [
    re.compile(r"\b(?:network|datacom|ip routing|noc)\b", re.IGNORECASE),
    re.compile(r"\b(?:system|systems|server|storage|virtualization)\b", re.IGNORECASE),
    re.compile(r"\b(?:cybersecurity|cyber security|security|soc analyst)\b", re.IGNORECASE),
    re.compile(r"\b(?:software|full[- ]stack|frontend|backend)\b", re.IGNORECASE),
    re.compile(r"\b(?:cloud|data center|datacenter)\b", re.IGNORECASE),
]
TECHNICAL_ROLE_PATTERN = re.compile(
    r"\b(?:engineer|developer|architect|administrator|analyst|"
    r"technician|support|presales|postsales)\b",
    re.IGNORECASE,
)

BUSINESS_SKILLS = {
    "Human Resources": [
        "recruitment",
        "talent acquisition",
        "onboarding",
        "payroll",
        "employee relations",
        "human resource information system",
        "hris",
        "attendance management",
        "performance management",
    ],
    "Procurement": [
        "procurement",
        "purchase order",
        "vendor management",
        "supplier management",
        "sourcing",
        "tender",
        "quotation",
    ],
    "Logistics & Supply Chain": [
        "supply chain",
        "logistics",
        "dispatch",
        "demand planning",
        "distribution",
        "shipment",
    ],
    "Inventory & Warehouse": [
        "inventory management",
        "stock control",
        "warehouse",
        "stocktaking",
        "goods receipt",
    ],
    "Processing": [
        "data processing",
        "document processing",
        "order processing",
        "transaction processing",
        "quality checking",
    ],
    "Finance & Accounting": [
        "bookkeeping",
        "accounts payable",
        "accounts receivable",
        "bank reconciliation",
        "financial reporting",
        "budgeting",
        "payroll",
        "accounts",
    ],
    "Legal & Compliance": [
        "contract review",
        "corporate governance",
        "regulatory compliance",
        "intellectual property",
        "legal research",
        "contract management",
    ],
    "Auditing & Compliance": [
        "internal audit",
        "external audit",
        "compliance",
        "control testing",
        "risk assessment",
    ],
    "Administration & Facilities": [
        "office administration",
        "record management",
        "scheduling",
        "filing",
        "correspondence",
    ],
    "Facilities": [
        "facilities management",
        "office maintenance",
        "security management",
        "workplace operations",
        "vendor coordination",
    ],
    "Customer Support / Success": [
        "customer support",
        "customer success",
        "client onboarding",
        "customer retention",
        "issue resolution",
        "customer satisfaction",
    ],
    "Research & Development": [
        "research and development",
        "prototype testing",
        "product innovation",
        "product development",
        "experimental design",
    ],
    "Production / Manufacturing": [
        "production planning",
        "manufacturing operations",
        "assembly line",
        "factory operations",
        "production control",
    ],
    "Quality Assurance": [
        "quality assurance",
        "quality control",
        "product testing",
        "safety standards",
        "quality inspection",
    ],
    "Operations": [
        "operations",
        "process improvement",
        "operational coordination",
        "data entry",
        "report preparation",
    ],
    "Coordination": [
        "coordination",
        "stakeholder coordination",
        "document coordination",
        "schedule coordination",
    ],
    "Sales": [
        "sales",
        "customer relationship management",
        "lead generation",
        "account management",
        "business development",
    ],
    "Marketing": [
        "digital marketing",
        "social media",
        "market research",
        "content marketing",
        "campaign management",
        "brand awareness",
        "advertising campaigns",
        "public relations",
    ],
    "Project Management": [
        "project management",
        "project planning",
        "project coordination",
        "stakeholder management",
    ],
}

NAME_LABEL_PATTERN = re.compile(
    r"^\s*(?:candidate\s+name|full\s+name|name)\s*[:\-]\s*(.+?)\s*$",
    re.IGNORECASE,
)
LOCATION_LABEL_PATTERN = re.compile(
    r"^\s*(?:current\s+location|location|city|based\s+in)\s*[:\-]\s*(.+?)\s*$",
    re.IGNORECASE,
)
NAME_STOP_WORDS = {
    "curriculum",
    "vitae",
    "resume",
    "cv",
    "profile",
    "engineer",
    "developer",
    "intern",
    "trainee",
    "assistant",
    "manager",
    "officer",
    "executive",
    "coordinator",
    "accountant",
    "analyst",
    "administrator",
    "operations",
    "human",
    "resources",
    "contact",
    "email",
    "phone",
    "mobile",
}


def _unique(values):
    results = []
    seen = set()
    for value in values:
        if not value:
            continue
        cleaned = str(value).strip()
        key = cleaned.casefold()
        if key not in seen:
            seen.add(key)
            results.append(cleaned)
    return results


def _extract_candidate_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:20]:
        match = NAME_LABEL_PATTERN.match(line)
        if match:
            candidate = match.group(1).strip(" |:-")
            if candidate and len(candidate) <= 80:
                return candidate, "explicit name label", line

    for line in lines[:10]:
        candidate = line.strip(" \t|:-")
        words = re.findall(r"[A-Za-z][A-Za-z'.-]*", candidate)
        if not 2 <= len(words) <= 5 or len(candidate) > 60:
            continue
        if any(word.casefold() in NAME_STOP_WORDS for word in words):
            continue
        if re.search(r"[@/:0-9]", candidate):
            continue
        if len("".join(words)) / max(len(candidate), 1) < 0.75:
            continue
        return candidate, "top-of-document name heuristic", line

    return "", "", ""


def _extract_location(text):
    for line in text.splitlines()[:80]:
        match = LOCATION_LABEL_PATTERN.match(line.strip())
        if match:
            location = match.group(1).strip(" ,;|:-")
            if location and len(location) <= 100:
                return location, line.strip()
    return "", ""


def _classify_department(employment_records):
    titles = [
        record.get("job_title_raw") or ""
        for record in employment_records
    ]
    title_text = " ".join(titles)

    title_matches = [
        (name, pattern.search(title_text))
        for name, pattern in BUSINESS_DEPARTMENTS
    ]
    title_matches = _unique(name for name, match in title_matches if match)

    has_technical_domain = any(
        pattern.search(title_text)
        for pattern in TECHNICAL_DOMAIN_TITLES
    )
    if has_technical_domain:
        title_matches = [
            department
            for department in title_matches
            if department != "Operations"
        ]

    if len(title_matches) == 1:
        return title_matches[0], "employment title", True
    if len(title_matches) > 1:
        return "", "ambiguous employment titles", False
    if has_technical_domain and TECHNICAL_ROLE_PATTERN.search(title_text):
        return "Engineering / IT", "technical employment title", False
    return "", "", False


CAREER_FUNCTION_DEPARTMENTS = {
    "Human Resources": "Human Resources",
    "Finance & Accounts": "Finance & Accounting",
    "Legal & Compliance": "Legal & Compliance",
    "Administration & Facilities": "Administration & Facilities",
    "Sales / Business Development": "Sales",
    "Marketing": "Marketing",
    "Customer Support / Success": "Customer Support / Success",
    "Information Technology": "Engineering / IT",
    "Frontend / UI Development": "Engineering / IT",
    "Backend Development": "Engineering / IT",
    "DevOps / Platform Engineering": "Engineering / IT",
    "Data Engineering / BI": "Engineering / IT",
    "AI / Machine Learning": "Engineering / IT",
    "Quality Assurance / Testing": "Quality Assurance",
    "Product / UX Design": "Design",
    "Research & Development": "Research & Development",
    "Production / Manufacturing": "Production / Manufacturing",
    "Quality Assurance": "Quality Assurance",
    "Procurement / Purchasing": "Procurement",
    "Logistics & Supply Chain": "Logistics & Supply Chain",
}


def _infer_level(employment_records):
    titles = " ".join(
        record.get("job_title_raw") or ""
        for record in employment_records
    ).casefold()

    level_patterns = [
        ("Director / Head", r"\b(?:director|head of|chief|cto|ceo|cfo|cio)\b"),
        ("Manager", r"\bmanager\b"),
        ("Architect", r"\barchitect\b"),
        ("Lead", r"\b(?:team lead|tech lead|lead)\b"),
        ("Senior", r"\bsenior\b|\bsr\.?\b"),
        ("Entry / Junior", r"\b(?:junior|jr\.?|entry[- ]level)\b"),
        ("Intern / Trainee", r"\b(?:intern|internship|trainee)\b"),
    ]
    matches = [
        label for label, pattern in level_patterns
        if re.search(pattern, titles)
    ]
    return matches[0] if len(matches) == 1 else ""


def _format_experience(experience):
    if not experience.get("records"):
        return ""
    duration = experience.get("total_calendar_experience", {})
    years = duration.get("years")
    months = duration.get("months")
    if years is None or months is None:
        return ""
    return f"{years}y {months}m"


def _format_education(education):
    records = education.get("records", [])
    if not records:
        return ""

    def end_year(record):
        try:
            return int(record.get("end_date_raw") or 0)
        except (TypeError, ValueError):
            return 0

    latest = sorted(records, key=end_year, reverse=True)
    formatted = []
    for record in latest:
        parts = [
            record.get("qualification_raw"),
            record.get("field_raw"),
            record.get("institution_raw"),
        ]
        year = record.get("end_date_raw")
        if year:
            parts.append(str(year))
        value = " - ".join(str(part) for part in parts if part)
        if value:
            formatted.append(value)
    return " ; ".join(_unique(formatted))


def _evidence_score(document_assessment, employment, department, domain,
                    technology, education):
    breakdown = {}
    breakdown["document_text_quality"] = (
        30 if document_assessment.get("status") == "VALID" else 12
    )

    employment_records = employment.get("records", [])
    dated_records = [
        record for record in employment_records
        if record.get("start_date_raw") and record.get("end_date_raw")
    ]
    if len(dated_records) >= 2:
        breakdown["employment_date_coverage"] = 25
    elif dated_records:
        breakdown["employment_date_coverage"] = 15
    elif employment.get("section_found"):
        breakdown["employment_date_coverage"] = 8
    else:
        breakdown["employment_date_coverage"] = 0

    if department and domain:
        breakdown["classification_evidence"] = 20
    elif department or domain:
        breakdown["classification_evidence"] = 12
    else:
        breakdown["classification_evidence"] = 0

    summaries = technology.get("technology_summary", [])
    if any(item.get("practical_evidence_count", 0) for item in summaries):
        breakdown["skill_evidence"] = 15
    elif any(item.get("experience_mention_count", 0) for item in summaries):
        breakdown["skill_evidence"] = 10
    elif summaries:
        breakdown["skill_evidence"] = 5
    else:
        breakdown["skill_evidence"] = 0

    education_records = education.get("records", [])
    if any(
        item.get("qualification_raw") and item.get("institution_raw")
        for item in education_records
    ):
        breakdown["education_evidence"] = 10
    elif education.get("section_found"):
        breakdown["education_evidence"] = 5
    else:
        breakdown["education_evidence"] = 0

    return min(sum(breakdown.values()), 100), breakdown


def build_candidate_record(file_path, text, document_metadata=None):
    """Return user-facing candidate fields plus auditable supporting evidence."""
    path = Path(file_path)
    document_metadata = document_metadata or {}

    pre_ai = run_pre_ai(text)
    employment = extract_employment_history(text)
    normalized_employment = normalize_employment_result(employment)
    experience = calculate_experience(normalized_employment)
    education = extract_education(text)
    certifications = extract_certifications(text)
    technology = extract_technology_evidence(text)
    classification = classify_candidate(
        text,
        employment.get("records", []),
        education.get("records", []),
        technology,
    )

    candidate, name_method, name_evidence = _extract_candidate_name(text)
    location, location_evidence = _extract_location(text)
    employment_records = employment.get("records", [])
    department, department_evidence, business_department = (
        _classify_department(employment_records)
    )
    if not department:
        work_departments = _unique(
            CAREER_FUNCTION_DEPARTMENTS[function]
            for function in classification["career_functions"]
            if function in CAREER_FUNCTION_DEPARTMENTS
        )
        if len(work_departments) == 1:
            department = work_departments[0]
            department_evidence = "employment responsibility evidence"
            business_department = department != "Engineering / IT"
    if not department and len(
        classification["education_department_suggestions"]
    ) == 1:
        department = classification["education_department_suggestions"][0]
        department_evidence = "education-based suggestion"
        business_department = True

    tech_roles = [
        role for role in technology.get("roles", [])
        if role.get("section") == "experience"
    ]
    role_domains = _unique(role.get("domain") for role in tech_roles)
    technology_domains = _unique(
        item.get("domain")
        for item in technology.get("technology_summary", [])
        if item.get("practical_evidence_count", 0)
        or item.get("experience_mention_count", 0)
    )

    domain_aliases = {
        "Software": "Software / Applications / Platforms",
        "IT Systems": "IT Systems / Infrastructure",
        "Cloud": "Cloud & Digital Infrastructure",
    }
    domains = _unique(
        domain_aliases.get(domain_name, domain_name)
        for domain_name in [
            *classification["domains"],
            *role_domains,
            *technology_domains,
        ]
    )
    if business_department:
        domains.append("Business / Corporate")
    domain = " ; ".join(_unique(domains))

    skills = [
        item["normalized_name"]
        for item in sorted(
            technology.get("technology_summary", []),
            key=lambda item: (
                item.get("practical_evidence_count", 0),
                item.get("experience_mention_count", 0),
                item.get("occurrence_count", 0),
            ),
            reverse=True,
        )
    ]
    skills.extend(classification["software_technologies"])
    if department:
        text_lower = text.casefold()
        skills.extend(
            skill for skill in BUSINESS_SKILLS.get(department, [])
            if skill.casefold() in text_lower
        )
    skills = _unique(skills)[:15]

    oem_products = {}
    for item in technology.get("oems", []):
        name = item.get("normalized_name", "")
        if not name:
            continue
        product = item.get("product_line", "")
        oem_products.setdefault(name, [])
        if product and product not in oem_products[name]:
            oem_products[name].append(product)
    oems = [
        (
            f"{name} ({', '.join(products)})"
            if products
            else name
        )
        for name, products in oem_products.items()
    ]
    certification_names = _unique(
        (
            f"{item['normalized_name']} [{item['name_raw']}]"
            if item.get("name_raw", "").casefold()
            not in item.get("normalized_name", "").casefold()
            else item.get("normalized_name")
        )
        for item in certifications.get("records", [])
    )
    education_text = _format_education(education)
    experience_text = _format_experience(experience)
    level = _infer_level(employment_records)
    document_assessment = pre_ai.get("document_assessment", {})

    score, score_breakdown = _evidence_score(
        document_assessment,
        employment,
        department,
        domain,
        technology,
        education,
    )
    if document_assessment.get("status") != "VALID":
        validity_label = "Insufficient evidence"
    elif score >= 80:
        validity_label = "Strong"
    elif score >= 60:
        validity_label = "Reasonable"
    else:
        validity_label = "Limited"

    review_reasons = []
    if not candidate:
        review_reasons.append("Candidate name not confidently extracted")
    elif name_method == "top-of-document name heuristic":
        review_reasons.append("Verify name extracted from document heading")
    if not location:
        review_reasons.append("Location not confidently extracted")
    if not pre_ai.get("contact", {}).get("emails") and not pre_ai.get(
        "contact", {}
    ).get("phones"):
        review_reasons.append("No email or phone detected")
    if not department and not domain:
        review_reasons.append("Domain/department is unclear")
    if not employment_records:
        review_reasons.append("Employment history not extracted")
    if not education_text:
        review_reasons.append("Education not extracted")
    if not level:
        review_reasons.append("Career level not explicit in extracted titles")
    if document_assessment.get("status") != "VALID":
        review_reasons.append("Extracted text quality needs review")
    if department_evidence.startswith("ambiguous"):
        review_reasons.append("Employment evidence suggests multiple departments")
    if department_evidence == "education-based suggestion":
        review_reasons.append(
            "Department is suggested from education; verify against work history"
        )
    if len(role_domains) > 1:
        review_reasons.append("Employment evidence suggests multiple domains")

    status = "Needs review" if review_reasons else "Ready for review"
    emails = pre_ai.get("contact", {}).get("emails", [])
    phones = pre_ai.get("contact", {}).get("phones", [])

    public = {
        "Candidate": candidate,
        "Email": " ; ".join(emails),
        "Phone": " ; ".join(phones),
        "Domain": domain,
        "Experience": experience_text,
        "Level": level,
        "Location": location,
        "Key Skills": " ; ".join(skills),
        "OEMs": " ; ".join(oems),
        "Certifications": " ; ".join(certification_names),
        "Status": status,
        "Department": department,
        "Degree/Education": education_text,
        "Validity of information": (
            f"Provisional: {validity_label} ({score}/100)"
        ),
        "Industry": " ; ".join(classification["industries"]),
        "Specialization / Subdomain": " ; ".join(
            _unique(
                [
                    *classification["specializations"],
                    *(
                        item.get("subcategory", "")
                        for item in technology.get(
                            "technology_summary", []
                        )
                    ),
                ]
            )
        ),
        "Career Function": " ; ".join(
            classification["career_functions"]
        ),
        "Software Stack": " ; ".join(
            classification["software_stacks"]
        ),
    }

    evidence = {
        "source_filename": path.name,
        "source_path": str(path.resolve()),
        "processing_result": "SUCCESS",
        "error_message": "",
        "review_reasons": review_reasons,
        "name_extraction_method": name_method,
        "candidate_name_evidence": name_evidence,
        "location_evidence": location_evidence,
        "department_evidence": department_evidence,
        "document_metadata": document_metadata,
        "document_assessment": document_assessment,
        "contact": pre_ai.get("contact", {}),
        "employment": experience,
        "education": education,
        "certifications": certifications,
        "technology": technology,
        "classification": classification,
        "keyword_signals": pre_ai.get("signals", {}).get("keywords", {}),
        "validity_score_breakdown": score_breakdown,
        "validity_score_note": (
            "Provisional evidence-coverage proxy based on extracted text, "
            "employment, classification, skills, and education. It does not "
            "yet measure cross-field coherence/relevance and is not a truth, "
            "authenticity, or hiring-suitability score."
        ),
    }

    return {"public": public, "evidence": evidence}
