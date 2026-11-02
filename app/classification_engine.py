"""Editable rule-based classification for industry, CMC domains, and software."""

import json
import re

if __package__:
    from .app_paths import config_file
else:
    from app_paths import config_file


RULES_PATH = config_file("classification_rules.json")


def _load_rules():
    try:
        with RULES_PATH.open("r", encoding="utf-8") as file:
            rules = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Classification rules file is missing: {RULES_PATH}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid classification rules JSON at {RULES_PATH}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    required = {
        "industries",
        "domains",
        "software_technologies",
        "education_departments",
        "industry_taxonomies",
        "career_functions",
    }
    missing = required.difference(rules)
    if missing:
        raise ValueError(
            "Classification rules are missing required sections: "
            + ", ".join(sorted(missing))
        )
    return rules


RULES = _load_rules()


def _find_terms(text, terms):
    found = []
    for term in terms:
        escaped = re.escape(term.strip())
        escaped = re.sub(r"\\\s+", r"\\s+", escaped)
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        if pattern.search(text):
            found.append(term)
    return found


def _unique(values):
    result = []
    seen = set()
    for value in values:
        if not value:
            continue
        key = value.casefold()
        if key not in seen:
            result.append(value)
            seen.add(key)
    return result


def _classify_industries(text):
    classifications = []
    evidence = {}
    for industry in RULES["industries"]:
        name = industry["name"]
        if "subindustries" in industry:
            matched_subindustries = []
            for subindustry in industry["subindustries"]:
                terms = _find_terms(text, subindustry.get("keywords", []))
                if terms:
                    matched_subindustries.append(subindustry["name"])
                    evidence[f"{name} — {subindustry['name']}"] = terms

            specific = [
                label for label in matched_subindustries
                if label != "General / Integrated"
            ]
            if specific:
                classifications.extend(
                    f"{name} — {label}" for label in specific
                )
                if "General / Integrated" in matched_subindustries:
                    evidence[f"{name} — General / Integrated"] = (
                        evidence.get(f"{name} — General / Integrated", [])
                    )
            elif "General / Integrated" in matched_subindustries:
                classifications.append(name)
                evidence[name] = evidence.get(
                    f"{name} — General / Integrated", []
                )
        else:
            terms = _find_terms(text, industry.get("keywords", []))
            if terms:
                classifications.append(name)
                evidence[name] = terms
    for taxonomy in RULES["industry_taxonomies"]:
        for label in taxonomy["labels"]:
            terms = _find_terms(text, [label])
            if label == "Information" and terms:
                terms = _find_terms(
                    text,
                    [
                        "information services",
                        "information technology",
                        "information sector",
                        "information industry",
                    ],
                )
            if terms:
                classifications.append(label)
                evidence[label] = terms
    return _unique(classifications), evidence


def _match_software_technologies(text):
    matched = []
    evidence = {}
    for item in RULES["software_technologies"]:
        names = [item["name"], *item.get("aliases", [])]
        terms = _find_terms(text, names)
        if terms:
            matched.append(item)
            evidence[item["name"]] = terms
    return matched, evidence


def _classify_software(
    text,
    matched_technologies,
    technology_evidence,
    extracted_technology,
):
    classified_categories = {
        "Frontend",
        "Backend",
        "Mobile Development",
        "Database",
        "Containers",
        "Container Orchestration",
        "Event Streaming",
        "AI / ML",
        "Data Engineering",
        "Testing / QA",
    }
    known_names = {item["name"] for item in matched_technologies}
    for item in extracted_technology.get("technology_summary", []):
        name = item.get("normalized_name", "")
        category = item.get("category", "")
        if name and category in classified_categories and name not in known_names:
            matched_technologies.append(
                {"name": name, "category": category}
            )
            known_names.add(name)

    by_name = {item["name"]: item for item in matched_technologies}
    names = set(by_name)
    lower = text.casefold()

    def has_any(*values):
        return any(value in names for value in values)

    def text_has_any(*values):
        return any(value in lower for value in values)

    specializations = []
    stacks = []
    architecture = []

    mobile = {
        item["name"] for item in matched_technologies
        if item["category"] == "Mobile Development"
    }
    if mobile:
        specializations.append("Mobile App Development")

    frontend = {
        item["name"] for item in matched_technologies
        if item["category"] == "Frontend"
    }
    backend = {
        item["name"] for item in matched_technologies
        if item["category"] == "Backend"
    }
    databases = {
        item["name"] for item in matched_technologies
        if item["category"] == "Database"
    }

    named_mern = has_any("MERN")
    named_pern = has_any("PERN")
    inferred_mern = (
        has_any("React")
        and has_any("Node.js")
        and has_any("Express")
        and has_any("MongoDB")
    )
    inferred_pern = (
        has_any("React")
        and has_any("Node.js")
        and has_any("Express")
        and has_any("PostgreSQL")
    )
    if named_mern or inferred_mern:
        stacks.append("MERN")
        specializations.append("Full-Stack Development")
    if named_pern or inferred_pern:
        stacks.append("PERN")
        specializations.append("Full-Stack Development")

    aspnet_frontend_backend = (
        has_any("ASP.NET")
        and bool(frontend)
        and bool(databases)
    )
    if aspnet_frontend_backend:
        stacks.append("ASP.NET Full-Stack")
        specializations.append("Full-Stack Development")

    explicit_full_stack = has_any("Full Stack") or text_has_any(
        "full-stack",
        "full stack",
        "fullstack",
    )
    if explicit_full_stack:
        specializations.append("Full-Stack Development")
        if "ASP.NET Full-Stack" not in stacks and not (
            "MERN" in stacks or "PERN" in stacks
        ):
            stacks.append("Full-Stack (explicit CV claim)")
    elif frontend and backend and not stacks:
        specializations.append("Full-Stack Development")
        stacks.append("Full-Stack (frontend + backend evidence)")

    if frontend:
        specializations.append("Frontend Development")
    if backend:
        specializations.append("Backend Development")

    infrastructure_tools = {
        item["name"] for item in matched_technologies
        if item.get("category") in {"Containers", "Container Orchestration"}
    }
    automation_tools = {
        "Terraform",
        "Ansible",
        "GitHub Actions",
        "GitLab CI",
        "Jenkins",
        "CloudFormation",
    }.intersection(
        names
        | {
            item.get("normalized_name", "")
            for item in extracted_technology.get(
                "technology_summary",
                [],
            )
        }
    )
    if infrastructure_tools and automation_tools:
        specializations.append("DevOps / Platform Engineering")

    if any(item.get("category") == "AI / ML" for item in matched_technologies):
        specializations.append("AI / Machine Learning")
    if any(
        item.get("category") == "Data Engineering"
        for item in matched_technologies
    ):
        specializations.append("Data Engineering / BI")
    if any(
        item.get("category") == "Testing / QA"
        for item in matched_technologies
    ):
        specializations.append("Software Testing / QA")

    if any(item["category"] == "Event Streaming" for item in matched_technologies):
        specializations.append("Event Streaming / Messaging")
        if text_has_any(
            "event-driven",
            "event driven",
            "distributed systems",
            "microservices",
            "message-driven",
        ):
            architecture.append("Event-Driven / Distributed Architecture")

    if any(
        item["category"] in {"Containers", "Container Orchestration"}
        for item in matched_technologies
    ):
        specializations.append("Containerization / Orchestration")

    if "Microservices" in names:
        specializations.append("Microservices")
        architecture.append("Microservices Architecture")

    if any(
        item["category"] == "Database"
        for item in matched_technologies
    ):
        specializations.append("Database Development")

    matched_names = [item["name"] for item in matched_technologies]
    return {
        "specializations": _unique(specializations),
        "software_stacks": _unique(stacks),
        "architecture": _unique(architecture),
        "technology_names": _unique(matched_names),
        "technology_evidence": technology_evidence,
        "frontend_technologies": sorted(frontend),
        "backend_technologies": sorted(backend),
        "database_technologies": sorted(databases),
        "mobile_technologies": sorted(mobile),
    }


def _classify_domains(text, software, existing_technology):
    matched = []
    evidence = {}
    for domain in RULES["domains"]:
        name = domain["name"]
        terms = _find_terms(text, domain.get("keywords", []))
        if terms:
            matched.append(name)
            evidence[name] = terms

    if software["technology_names"] or software["specializations"]:
        matched.append("Software / Applications / Platforms")

    for item in existing_technology.get("domain_signals", []):
        if (
            item.get("role_occurrences", 0)
            or item.get("practical_action_occurrences", 0)
            or item.get("technology_occurrences", 0)
            or item.get("product_occurrences", 0)
        ):
            matched.append(item.get("domain", ""))
            evidence.setdefault(item.get("domain", ""), []).append(
                (
                    "product-line evidence"
                    if item.get("product_occurrences", 0)
                    else "technology/role evidence"
                )
            )
    return _unique(matched), evidence


CAREER_FUNCTION_PATTERNS = [
    ("Sales / Business Development", re.compile(r"\b(?:sales|account executive|business development)\b", re.I)),
    ("Presales", re.compile(r"\b(?:presales|pre-sales|solution consultant|sales engineer)\b", re.I)),
    ("Solution Architecture", re.compile(r"\b(?:solution architect(?:ure)?|solutions architect(?:ure)?|architecture design|hld|lld)\b", re.I)),
    ("Solution Delivery", re.compile(r"\b(?:implementation|deployment|integration|commissioning|delivery engineer)\b", re.I)),
    ("Postsales / Support", re.compile(r"\b(?:postsales|post-sales|after-sales service|field service|technical support|customer support|service desk)\b", re.I)),
    ("Frontend / UI Development", re.compile(r"\b(?:front[- ]end|frontend|ui developer|web interface developer)\b", re.I)),
    ("Backend Development", re.compile(r"\b(?:back[- ]end|backend|server[- ]side developer)\b", re.I)),
    ("DevOps / Platform Engineering", re.compile(r"\b(?:devops|site reliability|platform engineer|release engineer)\b", re.I)),
    ("Data Engineering / BI", re.compile(r"\b(?:data engineer|analytics engineer|bi developer|business intelligence developer)\b", re.I)),
    ("AI / Machine Learning", re.compile(r"\b(?:machine learning engineer|ml engineer|ai engineer|data scientist|genai engineer)\b", re.I)),
    ("Quality Assurance / Testing", re.compile(r"\b(?:qa engineer|quality assurance|quality control|test engineer|software tester)\b", re.I)),
    ("Product / UX Design", re.compile(r"\b(?:product designer|ux designer|ui designer|user experience designer)\b", re.I)),
    ("Consulting", re.compile(r"\b(?:consultant|consulting)\b", re.I)),
    ("Engineering", re.compile(r"\b(?:engineer|developer|programmer|technician)\b", re.I)),
    ("Operations", re.compile(r"\b(?:operations|operator|system administrator|network administrator)\b", re.I)),
    ("Management", re.compile(r"\b(?:manager|director|head of|team lead)\b", re.I)),
    ("Coordination", re.compile(r"\b(?:coordinator|coordination|scheduler)\b", re.I)),
    ("Administration & Facilities", re.compile(r"\b(?:administrative|office assistant|facilities management)\b", re.I)),
]


def _classify_career_functions(employment_records):
    work_text = " ".join(
        " ".join(
            [
                record.get("job_title_raw") or "",
                record.get("employer_raw") or "",
                *record.get("evidence", []),
            ]
        )
        for record in employment_records
    )
    functions = [
        name
        for name, pattern in CAREER_FUNCTION_PATTERNS
        if pattern.search(work_text)
    ]
    evidence = {
        name: pattern.search(work_text).group(0)
        for name, pattern in CAREER_FUNCTION_PATTERNS
        if pattern.search(work_text)
    }
    for item in RULES["career_functions"]:
        terms = _find_terms(work_text, item.get("keywords", []))
        if terms:
            functions.append(item["name"])
            evidence[item["name"]] = terms
    return _unique(functions), evidence


def _education_department(education_records):
    fields = " ".join(
        " ".join(
            str(record.get(key) or "")
            for key in ("qualification_raw", "field_raw")
        )
        for record in education_records
    )
    candidates = []
    evidence = {}
    for item in RULES["education_departments"]:
        terms = _find_terms(fields, item.get("keywords", []))
        if terms:
            candidates.append(item["department"])
            evidence[item["department"]] = terms
    return _unique(candidates), evidence


def classify_candidate(text, employment_records, education_records,
                       technology_evidence):
    """Classify independent profile dimensions and return matched evidence."""
    industries, industry_evidence = _classify_industries(text)
    matched_technologies, software_evidence = _match_software_technologies(text)
    software = _classify_software(
        text,
        matched_technologies,
        software_evidence,
        technology_evidence,
    )
    domains, domain_evidence = _classify_domains(
        text,
        software,
        technology_evidence,
    )
    career_functions, career_evidence = _classify_career_functions(
        employment_records
    )
    education_departments, education_evidence = _education_department(
        education_records
    )

    return {
        "industries": industries,
        "domains": domains,
        "specializations": software["specializations"],
        "software_stacks": software["software_stacks"],
        "software_technologies": software["technology_names"],
        "architecture": software["architecture"],
        "career_functions": career_functions,
        "education_department_suggestions": education_departments,
        "evidence": {
            "industries": industry_evidence,
            "domains": domain_evidence,
            "software_technologies": software["technology_evidence"],
            "career_functions": career_evidence,
            "education_departments": education_evidence,
        },
        "software_layer_coverage": {
            "frontend": software["frontend_technologies"],
            "backend": software["backend_technologies"],
            "database": software["database_technologies"],
            "mobile": software["mobile_technologies"],
        },
    }
