import re


# ============================================================
# EDUCATION EXTRACTION
# ============================================================


EDUCATION_HEADINGS = [
    "education",
    "academic background",
    "academic qualifications",
    "educational background",
    "educational qualifications",
    "qualifications",
]


EDUCATION_STOP_HEADINGS = [
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "employment history",
    "career history",
    "work history",
    "certifications",
    "certification",
    "licenses",
    "skills",
    "technical skills",
    "professional skills",
    "projects",
    "project experience",
    "achievements",
    "references",
    "languages",
    "interests",
    "personal information",
]


QUALIFICATION_PATTERNS = [
    (r"\bph\.?d\b|\bdoctorate\b", "phd"),
    (r"\bmaster(?:'s)?\b|\bm\.?s\.?\b|\bm\.?sc\.?\b|\bmba\b|\bma\b|\bmaster of\b", "masters"),
    (r"\bbachelor(?:'s)?\b|\bb\.?s\.?\b|\bb\.?sc\.?\b|\bbs\b|\bba\b|\bbba\b|\bbe\b|\bbcs\b|\bb\.?e\.?\b", "bachelors"),
    (r"\bassociate(?:'s)?\b|\bassociate degree\b", "associate"),
    (r"\bdiploma\b|\bhnd\b|\bhigher national diploma\b", "diploma"),
    (r"\bintermediate\b|\bf\.?sc\.?\b|\bfsc\b|\ba\.?level\b|\ba levels?\b", "intermediate"),
    (r"\bmatric(?:ulation)?\b|\bssc\b|\bo\.?level\b|\bo levels?\b", "matric"),
    (r"\bcertificate\b|\bcertification\b", "certificate"),
]


FIELD_PATTERNS = [
    (r"\bcomputer science\b", "computer science"),
    (r"\bsoftware engineering\b", "software engineering"),
    (r"\binformation technology\b|\binformation technologies\b", "information technology"),
    (r"\bcomputer engineering\b", "computer engineering"),
    (r"\bcyber\s*security\b|\bcybersecurity\b", "cybersecurity"),
    (r"\bnetwork engineering\b|\bnetworking\b", "networking"),
    (r"\belectrical engineering\b", "electrical engineering"),
    (r"\belectronics engineering\b", "electronics engineering"),
    (r"\btelecommunication(?:s)? engineering\b", "telecommunications engineering"),
    (r"\btelecommunication(?:s)\b", "telecommunications"),
    (r"\bdata science\b", "data science"),
    (r"\bartificial intelligence\b", "artificial intelligence"),
    (r"\bmachine learning\b", "machine learning"),
    (r"\bcomputer applications\b", "computer applications"),
    (r"\bbusiness administration\b", "business administration"),
    (r"\bbusiness management\b", "business management"),
    (r"\bmanagement sciences?\b", "management sciences"),
    (r"\baccounting\b", "accounting"),
    (r"\bfinance\b", "finance"),
    (r"\bhuman resources?\b|\bhr\b", "human resources"),
    (r"\bsupply chain\b", "supply chain"),
    (r"\bmarketing\b", "marketing"),
    (r"\beconomics\b", "economics"),
]


INSTITUTION_KEYWORDS = [
    "university",
    "institute",
    "college",
    "school",
    "academy",
    "polytechnic",
    "campus",
]


# ============================================================
# BASIC HELPERS
# ============================================================


def clean_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


def is_heading(line, heading_list):
    normalized = re.sub(r"[^a-z0-9 ]", "", line.lower())
    normalized = clean_spaces(normalized)

    for heading in heading_list:
        if normalized == heading.lower():
            return True

    return False


def detect_education_section(text):
    """
    Locate the education section and return its text.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    start_index = None

    for index, line in enumerate(lines):

        if is_heading(line, EDUCATION_HEADINGS):
            start_index = index + 1
            break

    if start_index is None:
        return {
            "found": False,
            "text": "",
            "lines": [],
        }

    education_lines = []

    for line in lines[start_index:]:

        if is_heading(line, EDUCATION_STOP_HEADINGS):
            break

        education_lines.append(line)

    return {
        "found": True,
        "text": "\n".join(education_lines),
        "lines": education_lines,
    }


# ============================================================
# QUALIFICATION
# ============================================================


def detect_qualification(line):
    """
    Detect qualification level and preserve the original
    qualification wording.
    """

    for pattern, level in QUALIFICATION_PATTERNS:

        match = re.search(pattern, line, re.IGNORECASE)

        if match:
            return {
                "qualification_level": level,
                "qualification_raw": line.strip(),
            }

    return {
        "qualification_level": None,
        "qualification_raw": None,
    }


# ============================================================
# FIELD
# ============================================================


def detect_field(text):
    """
    Detect academic field from the surrounding education text.
    """

    for pattern, field in FIELD_PATTERNS:

        if re.search(pattern, text, re.IGNORECASE):
            return field

    return None


# ============================================================
# DATES
# ============================================================


def extract_years(text):
    """
    Extract four-digit academic years.

    Example:
        2017 – 2021

    Returns:
        ['2017', '2021']
    """

    years = re.findall(r"\b(?:19|20)\d{2}\b", text)

    # Preserve order while removing duplicates
    result = []

    for year in years:
        if year not in result:
            result.append(year)

    return result


def extract_date_range(text):
    """
    Identify start/end academic years.

    Returns:
        start_year
        end_year
    """

    years = extract_years(text)

    if len(years) >= 2:

        return {
            "start_year": years[0],
            "end_year": years[1],
        }

    if len(years) == 1:

        return {
            "start_year": years[0],
            "end_year": None,
        }

    return {
        "start_year": None,
        "end_year": None,
    }


# ============================================================
# ACADEMIC PERFORMANCE
# ============================================================


def extract_academic_performance(text):
    """
    Extract CGPA, GPA, percentage and grade information.
    """

    result = {
        "cgpa": None,
        "gpa": None,
        "percentage": None,
        "grade": None,
        "raw": [],
    }

    # CGPA
    cgpa_match = re.search(
        r"\bcgpa\s*[:\-]?\s*(\d+(?:\.\d+)?)"
        r"(?:\s*/\s*(\d+(?:\.\d+)?))?",
        text,
        re.IGNORECASE,
    )

    if cgpa_match:

        value = cgpa_match.group(1)
        scale = cgpa_match.group(2)

        if scale:
            result["cgpa"] = f"{value} / {scale}"
        else:
            result["cgpa"] = value

        result["raw"].append(cgpa_match.group(0).strip())

    # GPA
    gpa_match = re.search(
        r"\bgpa\s*[:\-]?\s*(\d+(?:\.\d+)?)"
        r"(?:\s*/\s*(\d+(?:\.\d+)?))?",
        text,
        re.IGNORECASE,
    )

    if gpa_match:

        value = gpa_match.group(1)
        scale = gpa_match.group(2)

        if scale:
            result["gpa"] = f"{value} / {scale}"
        else:
            result["gpa"] = value

        result["raw"].append(gpa_match.group(0).strip())

    # Percentage
    percentage_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        text,
        re.IGNORECASE,
    )

    if percentage_match:

        result["percentage"] = percentage_match.group(1) + "%"

        result["raw"].append(
            percentage_match.group(0).strip()
        )

    # Grade
    grade_match = re.search(
        r"\bgrade\s*[:\-]?\s*([A-F][+\-]?)\b",
        text,
        re.IGNORECASE,
    )

    if grade_match:

        result["grade"] = grade_match.group(1).upper()

        result["raw"].append(
            grade_match.group(0).strip()
        )

    # Standalone grade such as "(A+)"
    if result["grade"] is None:

        standalone_grade = re.search(
            r"\(([A-F][+\-]?)\)",
            text,
            re.IGNORECASE,
        )

        if standalone_grade:

            result["grade"] = standalone_grade.group(1).upper()

            result["raw"].append(
                standalone_grade.group(0).strip()
            )

    return result


# ============================================================
# INSTITUTION
# ============================================================


def clean_institution_text(text):
    """
    Remove dates and academic performance information from
    institution text while preserving the actual institution.
    """

    cleaned = text.strip()

    # Remove academic performance information.
    cleaned = re.sub(
        r"\bCGPA\s*[:\-]?\s*\d+(?:\.\d+)?"
        r"(?:\s*/\s*\d+(?:\.\d+)?)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\bGPA\s*[:\-]?\s*\d+(?:\.\d+)?"
        r"(?:\s*/\s*\d+(?:\.\d+)?)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\bgrade\s*[:\-]?\s*[A-F][+\-]?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\([A-F][+\-]?\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*%",
        "",
        cleaned,
    )

    # Remove year ranges.
    cleaned = re.sub(
        r"\b(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\b",
        "",
        cleaned,
    )

    # Remove standalone years.
    cleaned = re.sub(
        r"\b(?:19|20)\d{2}\b",
        "",
        cleaned,
    )

    # Remove leftover separators.
    cleaned = re.sub(
        r"\s*\|\s*",
        " ",
        cleaned,
    )

    cleaned = re.sub(
        r"\s*[-–—]\s*$",
        "",
        cleaned,
    )

    cleaned = re.sub(
        r"\s*[:|,]\s*$",
        "",
        cleaned,
    )

    cleaned = clean_spaces(cleaned)

    return cleaned.strip(" |:-")


def detect_institution(lines):
    """
    Detect an institution from education lines.

    The institution is extracted independently from dates,
    grades and academic performance.
    """

    candidates = []

    for line in lines:

        if not any(
            keyword in line.lower()
            for keyword in INSTITUTION_KEYWORDS
        ):
            continue

        cleaned = clean_institution_text(line)

        if not cleaned:
            continue

        # Avoid returning a line that consists only of
        # qualification/date/performance information.
        if any(
            keyword in cleaned.lower()
            for keyword in INSTITUTION_KEYWORDS
        ):
            candidates.append(cleaned)

    if not candidates:
        return None

    # Prefer the longest meaningful institution candidate.
    candidates.sort(key=len, reverse=True)

    return candidates[0]


# ============================================================
# QUALIFICATION CLEANING
# ============================================================


def clean_qualification(line):
    """
    Remove institution, dates and academic performance from
    the qualification line where possible.
    """

    cleaned = line.strip()

    # Remove academic performance.
    cleaned = re.sub(
        r"\bCGPA\s*[:\-]?\s*\d+(?:\.\d+)?"
        r"(?:\s*/\s*\d+(?:\.\d+)?)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\bGPA\s*[:\-]?\s*\d+(?:\.\d+)?"
        r"(?:\s*/\s*\d+(?:\.\d+)?)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\bgrade\s*[:\-]?\s*[A-F][+\-]?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(
        r"\([A-F][+\-]?\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    # Remove date ranges.
    cleaned = re.sub(
        r"\b(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\b",
        "",
        cleaned,
    )

    # Remove standalone years.
    cleaned = re.sub(
        r"\b(?:19|20)\d{2}\b",
        "",
        cleaned,
    )

    cleaned = clean_spaces(cleaned)

    return cleaned.strip(" |:-")


# ============================================================
# RECORD EXTRACTION
# ============================================================


def extract_education_records(lines):
    """
    Build structured education records from education lines.
    """

    records = []

    for index, line in enumerate(lines):

        qualification_info = detect_qualification(line)

        if not qualification_info["qualification_level"]:
            continue

        # Use nearby lines as contextual evidence.
        context_lines = []

        start_context = max(0, index - 1)
        end_context = min(len(lines), index + 3)

        for context_index in range(start_context, end_context):
            context_lines.append(lines[context_index])

        context_text = "\n".join(context_lines)

        dates = extract_date_range(context_text)

        academic_performance = extract_academic_performance(
            context_text
        )

        institution = detect_institution(
            context_lines
        )

        field = detect_field(
            context_text
        )

        qualification_raw = clean_qualification(
            qualification_info["qualification_raw"]
        )

        evidence = []

        for evidence_line in context_lines:

            if evidence_line not in evidence:
                evidence.append(evidence_line)

        confidence = "medium"

        if (
            qualification_raw
            and institution
            and (
                dates["start_year"]
                or dates["end_year"]
            )
        ):
            confidence = "high"

        record = {
            "qualification_raw": qualification_raw,
            "qualification_level": qualification_info[
                "qualification_level"
            ],
            "field_raw": field,
            "institution_raw": institution,
            "start_date_raw": dates["start_year"],
            "end_date_raw": dates["end_year"],
            "date_values_raw": extract_years(
                context_text
            ),
            "academic_performance": academic_performance,
            "evidence": evidence,
            "confidence": confidence,
        }

        records.append(record)

    return records


# ============================================================
# PUBLIC API
# ============================================================


def extract_education(text):
    """
    Main public education extraction function.

    Returns:
        {
            "section_found": bool,
            "section_text": str,
            "records": [...],
            "record_count": int
        }
    """

    section = detect_education_section(text)

    if not section["found"]:

        return {
            "section_found": False,
            "section_text": "",
            "records": [],
            "record_count": 0,
        }

    records = extract_education_records(
        section["lines"]
    )

    return {
        "section_found": True,
        "section_text": section["text"],
        "records": records,
        "record_count": len(records),
    }


# ============================================================
# DISPLAY
# ============================================================


def print_education_summary(result):
    """
    Print education extraction in a human-readable format.
    """

    print("=" * 70)
    print("EDUCATION EXTRACTION")
    print("=" * 70)

    print(
        f"Education section found: "
        f"{result.get('section_found')}"
    )

    print(
        f"Education records: "
        f"{result.get('record_count', 0)}"
    )

    for index, record in enumerate(
        result.get("records", []),
        start=1
    ):

        print()
        print(f"RECORD {index}")

        print(
            f"Qualification: "
            f"{record.get('qualification_raw')}"
        )

        print(
            f"Level: "
            f"{record.get('qualification_level')}"
        )

        print(
            f"Field: "
            f"{record.get('field_raw')}"
        )

        print(
            f"Institution: "
            f"{record.get('institution_raw')}"
        )

        print(
            f"Start Date: "
            f"{record.get('start_date_raw')}"
        )

        print(
            f"End Date: "
            f"{record.get('end_date_raw')}"
        )

        print(
            f"Dates: "
            f"{record.get('date_values_raw')}"
        )

        performance = record.get(
            "academic_performance",
            {}
        )

        print("Academic Performance:")

        print(
            f"  CGPA: "
            f"{performance.get('cgpa')}"
        )

        print(
            f"  GPA: "
            f"{performance.get('gpa')}"
        )

        print(
            f"  Percentage: "
            f"{performance.get('percentage')}"
        )

        print(
            f"  Grade: "
            f"{performance.get('grade')}"
        )

        print(
            f"Confidence: "
            f"{record.get('confidence')}"
        )