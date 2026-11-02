import json
import re

if __package__:
    from .app_paths import config_file
else:
    from app_paths import config_file

# ============================================================
# CERTIFICATION DATABASE
# ============================================================

CERTIFICATION_PATTERNS = [

    # --------------------------------------------------------
    # Cisco
    # --------------------------------------------------------

    (
        r"\bccna\b",
        {
            "normalized_name": "Cisco Certified Network Associate",
            "vendor": "Cisco",
            "category": "Networking",
            "level": "Associate",
        },
    ),

    (
        r"\bccnp\b",
        {
            "normalized_name": "Cisco Certified Network Professional",
            "vendor": "Cisco",
            "category": "Networking",
            "level": "Professional",
        },
    ),

    (
        r"\bccie\b",
        {
            "normalized_name": "Cisco Certified Internetwork Expert",
            "vendor": "Cisco",
            "category": "Networking",
            "level": "Expert",
        },
    ),

    (
        r"\bccna\s+security\b",
        {
            "normalized_name": "Cisco Certified Network Associate Security",
            "vendor": "Cisco",
            "category": "Cybersecurity",
            "level": "Associate",
        },
    ),

    # --------------------------------------------------------
    # Huawei
    # --------------------------------------------------------

    (
        r"\bhcna\b",
        {
            "normalized_name": "Huawei Certified Network Associate",
            "vendor": "Huawei",
            "category": "Networking",
            "level": "Associate",
        },
    ),

    (
        r"\bhcnp\b",
        {
            "normalized_name": "Huawei Certified Network Professional",
            "vendor": "Huawei",
            "category": "Networking",
            "level": "Professional",
        },
    ),

    (
        r"\bhcip\b",
        {
            "normalized_name": "Huawei Certified ICT Professional",
            "vendor": "Huawei",
            "category": "ICT",
            "level": "Professional",
        },
    ),

    (
        r"\bhcie\b",
        {
            "normalized_name": "Huawei Certified ICT Expert",
            "vendor": "Huawei",
            "category": "ICT",
            "level": "Expert",
        },
    ),

    # --------------------------------------------------------
    # Microsoft
    # --------------------------------------------------------

    (
        r"\bmcse\b",
        {
            "normalized_name": "Microsoft Certified Solutions Expert",
            "vendor": "Microsoft",
            "category": "IT Systems",
            "level": "Expert",
        },
    ),

    (
        r"\bmcsa\b",
        {
            "normalized_name": "Microsoft Certified Solutions Associate",
            "vendor": "Microsoft",
            "category": "IT Systems",
            "level": "Associate",
        },
    ),

    (
        r"\baz[- ]?104\b",
        {
            "normalized_name": "Microsoft Azure Administrator Associate",
            "vendor": "Microsoft",
            "category": "Cloud",
            "level": "Associate",
        },
    ),

    (
        r"\baz[- ]?305\b",
        {
            "normalized_name": "Microsoft Azure Solutions Architect Expert",
            "vendor": "Microsoft",
            "category": "Cloud",
            "level": "Expert",
        },
    ),

    # --------------------------------------------------------
    # VMware
    # --------------------------------------------------------

    (
        r"\bvcp(?:[- ]?dcv)?\b",
        {
            "normalized_name": "VMware Certified Professional - Data Center Virtualization",
            "vendor": "VMware",
            "category": "Virtualization",
            "level": "Professional",
        },
    ),

    (
        r"\bvcap\b",
        {
            "normalized_name": "VMware Certified Advanced Professional",
            "vendor": "VMware",
            "category": "Virtualization",
            "level": "Advanced Professional",
        },
    ),

    (
        r"\bvcix\b",
        {
            "normalized_name": "VMware Certified Implementation Expert",
            "vendor": "VMware",
            "category": "Virtualization",
            "level": "Expert",
        },
    ),

    # --------------------------------------------------------
    # Red Hat
    # --------------------------------------------------------

    (
        r"\brhcsa\b",
        {
            "normalized_name": "Red Hat Certified System Administrator",
            "vendor": "Red Hat",
            "category": "Linux Systems",
            "level": "Associate",
        },
    ),

    (
        r"\brhce\b",
        {
            "normalized_name": "Red Hat Certified Engineer",
            "vendor": "Red Hat",
            "category": "Linux Systems",
            "level": "Professional",
        },
    ),

    (
        r"\brhcva\b",
        {
            "normalized_name": "Red Hat Certified Virtualization Administrator",
            "vendor": "Red Hat",
            "category": "Virtualization",
            "level": "Professional",
        },
    ),

    # --------------------------------------------------------
    # AWS
    # --------------------------------------------------------

    (
        r"\baws\s+certified\s+solutions\s+architect\b",
        {
            "normalized_name": "AWS Certified Solutions Architect",
            "vendor": "AWS",
            "category": "Cloud",
            "level": "Professional",
        },
    ),

    (
        r"\baws\s+certified\s+solutions\s+architect\s+associate\b",
        {
            "normalized_name": "AWS Certified Solutions Architect - Associate",
            "vendor": "AWS",
            "category": "Cloud",
            "level": "Associate",
        },
    ),

    (
        r"\baws\s+certified\s+cloud\s+practitioner\b",
        {
            "normalized_name": "AWS Certified Cloud Practitioner",
            "vendor": "AWS",
            "category": "Cloud",
            "level": "Foundational",
        },
    ),

    # --------------------------------------------------------
    # Cybersecurity
    # --------------------------------------------------------

    (
        r"\bcissp\b",
        {
            "normalized_name": "Certified Information Systems Security Professional",
            "vendor": "ISC2",
            "category": "Cybersecurity",
            "level": "Professional",
        },
    ),

    (
        r"\bceh\b",
        {
            "normalized_name": "Certified Ethical Hacker",
            "vendor": "EC-Council",
            "category": "Cybersecurity",
            "level": "Professional",
        },
    ),

    (
        r"\bsecurity\+\b",
        {
            "normalized_name": "CompTIA Security+",
            "vendor": "CompTIA",
            "category": "Cybersecurity",
            "level": "Professional",
        },
    ),

    # --------------------------------------------------------
    # IT / Project Management
    # --------------------------------------------------------

    (
        r"\bpmp\b",
        {
            "normalized_name": "Project Management Professional",
            "vendor": "PMI",
            "category": "Project Management",
            "level": "Professional",
        },
    ),

    (
        r"\bitil\b",
        {
            "normalized_name": "ITIL",
            "vendor": "PeopleCert / AXELOS",
            "category": "IT Service Management",
            "level": "Professional",
        },
    ),
]


CERTIFICATION_CATALOG_PATH = config_file("certification_catalog.json")


def _load_certification_catalog():
    try:
        with CERTIFICATION_CATALOG_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            catalog = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Certification catalog is missing: "
            f"{CERTIFICATION_CATALOG_PATH}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Invalid certification catalog JSON at "
            f"{CERTIFICATION_CATALOG_PATH}: line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc

    certifications = catalog.get("certifications")
    if not isinstance(certifications, list):
        raise ValueError(
            "Certification catalog must contain a 'certifications' list"
        )
    required_fields = {
        "pattern",
        "normalized_name",
        "vendor",
        "category",
        "level",
        "domain",
    }
    for index, item in enumerate(certifications):
        missing = required_fields.difference(item)
        if missing:
            raise ValueError(
                f"Certification entry {index} is missing: "
                + ", ".join(sorted(missing))
            )
        try:
            re.compile(item["pattern"])
        except re.error as exc:
            raise ValueError(
                f"Invalid regex in certification entry {index}: {exc}"
            ) from exc
    return certifications


CERTIFICATION_CATALOG = _load_certification_catalog()
CERTIFICATION_PATTERNS.extend(
    (item["pattern"], item)
    for item in CERTIFICATION_CATALOG
)

CERTIFICATION_DOMAIN_BY_CATEGORY = {
    "Networking": "IP Datacom / Networking",
    "Cybersecurity": "Cybersecurity",
    "IT Systems": "IT Systems / Infrastructure",
    "Virtualization": "IT Systems / Infrastructure",
    "Linux Systems": "IT Systems / Infrastructure",
    "Cloud": "Cloud & Digital Infrastructure",
    "Data Protection": "Storage & Data Protection",
    "Data Center Facilities": "Data Center Facilities",
    "Data Center / Cabling": "Data Center Facilities",
    "AI / Machine Learning": "AI / Machine Learning",
    "Observability": "Software / Applications / Platforms",
    "Monitoring": "Software / Applications / Platforms",
}


# ============================================================
# SECTION DETECTION
# ============================================================


CERTIFICATION_HEADINGS = [
    "certifications",
    "certification",
    "professional certifications",
    "professional certification",
    "certificates",
    "certification & training",
    "certifications & training",
    "licenses & certifications",
    "licenses and certifications",
]


CERTIFICATION_STOP_HEADINGS = [
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "employment history",
    "education",
    "academic background",
    "academic qualifications",
    "skills",
    "technical skills",
    "projects",
    "achievements",
    "references",
    "languages",
]


def clean_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def is_heading(line, heading_list):

    normalized = re.sub(
        r"[^a-z0-9 ]",
        "",
        line.lower()
    )

    normalized = clean_spaces(normalized)

    for heading in heading_list:

        if normalized == heading.lower():
            return True

    return False


def detect_certification_section(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    start_index = None

    for index, line in enumerate(lines):

        if is_heading(
            line,
            CERTIFICATION_HEADINGS
        ):
            start_index = index + 1
            break

    if start_index is None:

        return {
            "found": False,
            "text": "",
            "lines": [],
        }

    certification_lines = []

    for line in lines[start_index:]:

        if is_heading(
            line,
            CERTIFICATION_STOP_HEADINGS
        ):
            break

        certification_lines.append(line)

    return {
        "found": True,
        "text": "\n".join(certification_lines),
        "lines": certification_lines,
    }


# ============================================================
# CERTIFICATION EXTRACTION
# ============================================================


def extract_certifications_from_text(text, section_found=False):
    candidates = []
    context_pattern = re.compile(
        r"\b(?:certif\w*|credential\w*|license[ds]?|accredited|"
        r"certified|credentialed)\b",
        re.IGNORECASE,
    )

    for pattern_index, (pattern, metadata) in enumerate(
        CERTIFICATION_PATTERNS
    ):
        for match in re.finditer(pattern, text, re.IGNORECASE):
            raw = match.group(0).strip()
            local_context = text[
                max(0, match.start() - 90):
                min(len(text), match.end() + 90)
            ]
            compact_name = re.sub(r"[^A-Za-z0-9]", "", raw)
            has_explicit_context = bool(context_pattern.search(local_context))
            if (
                not section_found
                and len(compact_name) <= 4
                and not has_explicit_context
            ):
                continue

            candidates.append(
                (
                    match.start(),
                    match.end(),
                    len(pattern),
                    pattern_index,
                    match,
                    metadata,
                    local_context,
                    has_explicit_context,
                )
            )

    candidates.sort(
        key=lambda item: (
            item[0],
            -(item[1] - item[0]),
            -len(item[5]["normalized_name"]),
            -item[2],
            item[3],
        )
    )
    selected = []
    for candidate in candidates:
        start, end = candidate[0:2]
        if any(start < current[1] and end > current[0] for current in selected):
            continue
        selected.append((start, end, candidate))

    results = []
    seen = set()
    for _, _, candidate in selected:
        match = candidate[4]
        metadata = candidate[5]
        raw = match.group(0).strip()
        key = (metadata["normalized_name"].casefold(), raw.casefold())
        if key in seen:
            continue
        seen.add(key)
        groups = [value for value in match.groups() if value]
        result = {
            "name_raw": raw,
            "normalized_name": metadata["normalized_name"],
            "vendor": metadata["vendor"],
            "category": metadata["category"],
            "level": metadata["level"],
            "domain": metadata.get("domain")
            or CERTIFICATION_DOMAIN_BY_CATEGORY.get(
                metadata.get("category", ""),
                "",
            ),
            "credential_variant": " ; ".join(groups),
            "evidence": raw,
            "context_evidence": get_certification_line(
                text,
                match.start(),
                match.end(),
            ),
            "confidence": (
                "high"
                if section_found
                else "moderate"
                if candidate[7]
                else "low"
            ),
        }
        results.append(result)
    return results


def get_certification_line(text, start, end):
    line_start = text.rfind("\n", 0, start)
    line_end = text.find("\n", end)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end].strip()


# ============================================================
# PUBLIC API
# ============================================================


def extract_certifications(text):

    section = detect_certification_section(text)

    # Even if a formal certification section is absent,
    # search the complete CV for known certifications.
    search_text = (
        section["text"]
        if section["found"]
        else text
    )

    records = extract_certifications_from_text(
        search_text,
        section_found=section["found"],
    )

    return {
        "section_found": section["found"],
        "section_text": section["text"],
        "records": records,
        "record_count": len(records),
    }


# ============================================================
# DISPLAY
# ============================================================


def print_certification_summary(result):

    print("=" * 70)
    print("CERTIFICATION EXTRACTION")
    print("=" * 70)

    print(
        f"Certification section found: "
        f"{result.get('section_found')}"
    )

    print(
        f"Certifications detected: "
        f"{result.get('record_count', 0)}"
    )

    for index, record in enumerate(
        result.get("records", []),
        start=1
    ):

        print()
        print(f"RECORD {index}")

        print(
            f"Raw: "
            f"{record.get('name_raw')}"
        )

        print(
            f"Normalized: "
            f"{record.get('normalized_name')}"
        )

        print(
            f"Vendor: "
            f"{record.get('vendor')}"
        )

        print(
            f"Category: "
            f"{record.get('category')}"
        )

        print(
            f"Level: "
            f"{record.get('level')}"
        )

        print(
            f"Evidence: "
            f"{record.get('evidence')}"
        )

        print(
            f"Confidence: "
            f"{record.get('confidence')}"
        )