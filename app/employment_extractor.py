import re


# ------------------------------------------------------------
# EMPLOYMENT SECTION DETECTION
# ------------------------------------------------------------

EXPERIENCE_HEADINGS = [
    "professional experience",
    "work experience",
    "employment history",
    "career history",
    "professional history",
    "employment experience",
    "experience",
    "career",
]

STOP_HEADINGS = [
    "education",
    "academics",
    "academic qualifications",
    "certifications",
    "professional certifications",
    "skills",
    "skill set",
    "technical skills",
    "technical proficiencies",
    "achievements",
    "hobbies",
    "references",
    "languages",
    "interests",
]


# ------------------------------------------------------------
# DATE PATTERNS
# ------------------------------------------------------------

MONTHS = (
    r"(?:"
    r"january|february|march|april|may|june|july|august|"
    r"september|october|november|december|"
    r"jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
    r")"
)

MONTH_YEAR = rf"{MONTHS}\s*[-/.,]?\s*\d{{4}}"
YEAR = r"\d{4}"


# Range examples:
#
# July 2025 – Present
# July 2025 - Present
# January 2016 – to date
# Jun-2010-Apr, 2015
# June 2010 - April 2015
# 2010 - 2015
# 2010 – Present
#
# We deliberately allow unusual punctuation because CVs are often badly formatted.

DATE_RANGE_PATTERNS = [

    # Month + year to Present / to date
    rf"\b{MONTH_YEAR}\s*(?:[-–—]|to)\s*(?:present|current|to\s+date|date)\b",

    # Month + year to Month + year
    rf"\b{MONTH_YEAR}\s*(?:[-–—]|to)\s*{MONTH_YEAR}\b",

    # Month-year compact format:
    # Jun-2010-Apr, 2015
    rf"\b{MONTHS}\s*[-/.]\s*\d{{4}}\s*[-–—]\s*{MONTHS}\s*[,./-]?\s*\d{{4}}\b",

    # Year to Present
    rf"\b{YEAR}\s*(?:[-–—]|to)\s*(?:present|current|to\s+date|date)\b",

    # Year to Year
    rf"\b{YEAR}\s*(?:[-–—]|to)\s*{YEAR}\b",
]


DATE_RANGE_REGEX = re.compile(
    "|".join(f"({pattern})" for pattern in DATE_RANGE_PATTERNS),
    re.IGNORECASE,
)


# ------------------------------------------------------------
# ROLE KEYWORDS
# ------------------------------------------------------------

ROLE_KEYWORDS = [
    "engineer",
    "developer",
    "administrator",
    "architect",
    "manager",
    "assistant manager",
    "assistant",
    "director",
    "officer",
    "executive",
    "analyst",
    "consultant",
    "specialist",
    "technician",
    "supervisor",
    "coordinator",
    "lead",
    "team lead",
    "head",
    "intern",
    "trainee",
    "instructor",
    "trainer",
    "operator",
    "associate",
    "representative",
    "advisor",
    "accountant",
    "designer",
    "developer",
    "programmer",
    "scientist",
    "researcher",
]


# ------------------------------------------------------------
# BASIC HELPERS
# ------------------------------------------------------------

def clean_line(line):
    return re.sub(r"\s+", " ", line.strip())


def is_heading(line):
    """
    Detect likely section headings.
    """

    normalized = clean_line(line).lower()

    if normalized in STOP_HEADINGS:
        return True

    if normalized in EXPERIENCE_HEADINGS:
        return True

    return False


def is_stop_heading(line):
    normalized = clean_line(line).lower()

    return normalized in STOP_HEADINGS


def contains_date_range(line):
    return bool(DATE_RANGE_REGEX.search(line))


# ------------------------------------------------------------
# DATE PARSING
# ------------------------------------------------------------

def parse_date_range(raw_date):
    """
    Normalize common CV date formats while preserving the original value.

    Returns:
        {
            "start_date_raw": ...,
            "end_date_raw": ...,
            "date_range_raw": ...,
            "date_confidence": ...
        }
    """

    raw = clean_line(raw_date)

    # --------------------------------------------
    # Month Year -> Present / To Date
    # --------------------------------------------

    pattern = re.compile(
        rf"({MONTH_YEAR})\s*(?:[-–—]|to)\s*"
        rf"(present|current|to\s+date|date)",
        re.IGNORECASE,
    )

    match = pattern.search(raw)

    if match:

        start = clean_line(match.group(1))
        end = match.group(2)

        return {
            "start_date_raw": start,
            "end_date_raw": end,
            "date_range_raw": raw,
            "date_confidence": "high",
        }

    # --------------------------------------------
    # Month Year -> Month Year
    # --------------------------------------------

    pattern = re.compile(
        rf"({MONTH_YEAR})\s*(?:[-–—]|to)\s*({MONTH_YEAR})",
        re.IGNORECASE,
    )

    match = pattern.search(raw)

    if match:

        return {
            "start_date_raw": clean_line(match.group(1)),
            "end_date_raw": clean_line(match.group(2)),
            "date_range_raw": raw,
            "date_confidence": "high",
        }

    # --------------------------------------------
    # Compact format:
    # Jun-2010-Apr, 2015
    # --------------------------------------------

    pattern = re.compile(
        rf"({MONTHS})\s*[-/.]\s*(\d{{4}})\s*"
        rf"[-–—]\s*"
        rf"({MONTHS})\s*[,./-]?\s*(\d{{4}})",
        re.IGNORECASE,
    )

    match = pattern.search(raw)

    if match:

        start = f"{match.group(1)} {match.group(2)}"
        end = f"{match.group(3)} {match.group(4)}"

        return {
            "start_date_raw": start,
            "end_date_raw": end,
            "date_range_raw": raw,
            "date_confidence": "medium",
        }

    # --------------------------------------------
    # Year -> Present
    # --------------------------------------------

    pattern = re.compile(
        rf"\b({YEAR})\s*(?:[-–—]|to)\s*"
        rf"(present|current|to\s+date|date)\b",
        re.IGNORECASE,
    )

    match = pattern.search(raw)

    if match:

        return {
            "start_date_raw": match.group(1),
            "end_date_raw": match.group(2),
            "date_range_raw": raw,
            "date_confidence": "medium",
        }

    # --------------------------------------------
    # Year -> Year
    # --------------------------------------------

    pattern = re.compile(
        rf"\b({YEAR})\s*(?:[-–—]|to)\s*({YEAR})\b",
        re.IGNORECASE,
    )

    match = pattern.search(raw)

    if match:

        return {
            "start_date_raw": match.group(1),
            "end_date_raw": match.group(2),
            "date_range_raw": raw,
            "date_confidence": "medium",
        }

    return {
        "start_date_raw": None,
        "end_date_raw": None,
        "date_range_raw": raw,
        "date_confidence": "low",
    }


# ------------------------------------------------------------
# DATE EXTRACTION FROM LINE
# ------------------------------------------------------------

def extract_date_from_line(line):

    match = DATE_RANGE_REGEX.search(line)

    if not match:
        return None

    raw_date = match.group(0)

    return {
        "raw": clean_line(raw_date),
        **parse_date_range(raw_date),
    }


# ------------------------------------------------------------
# ROLE DETECTION
# ------------------------------------------------------------

def looks_like_role(line):

    normalized = clean_line(line).lower()

    if not normalized:
        return False

    # Ignore obvious section headings
    if is_stop_heading(normalized):
        return False

    # Ignore very long sentences
    if len(normalized) > 100:
        return False

    for keyword in ROLE_KEYWORDS:

        if re.search(rf"\b{re.escape(keyword)}\b", normalized):

            return True

    return False


# ------------------------------------------------------------
# TITLE EXTRACTION
# ------------------------------------------------------------

def extract_title_before_date(lines, date_index):

    """
    Search only the immediately preceding lines for a likely
    job title.

    We deliberately avoid treating arbitrary narrative text as
    a job title.
    """

    start = max(0, date_index - 2)

    candidates = []

    for index in range(start, date_index):

        line = clean_line(lines[index])

        if not line:
            continue

        if contains_date_range(line):
            continue

        if is_stop_heading(line):
            continue

        candidates.append(line)

    # Only accept a candidate that independently looks like a role.
    for line in reversed(candidates):

        if looks_like_role(line):
            return line

    return None


# ------------------------------------------------------------
# EMPLOYER EXTRACTION
# ------------------------------------------------------------

def extract_employer_from_date_line(line, date_info):

    """
    Extract employer information from text preceding the date.
    """

    raw_date = date_info["raw"]

    before_date = line.split(raw_date, 1)[0].strip()

    # Remove common opening/closing punctuation.
    before_date = before_date.strip(" (|:-–—")

    if not before_date:
        return None

    return clean_line(before_date)


def find_employer_before_date(lines, date_index):

    """
    Look immediately above the date line for a likely employer.
    """

    start = max(0, date_index - 2)

    for index in range(date_index - 1, start - 1, -1):

        line = clean_line(lines[index])

        if not line:
            continue

        if contains_date_range(line):
            continue

        if is_stop_heading(line):
            continue

        return line

    return None


# ------------------------------------------------------------
# SECTION EXTRACTION
# ------------------------------------------------------------

def find_experience_section(lines):

    start_index = None
    end_index = len(lines)

    for index, raw_line in enumerate(lines):

        line = clean_line(raw_line)

        if not line:
            continue

        normalized = line.lower()

        if normalized in EXPERIENCE_HEADINGS:

            start_index = index + 1
            break

    if start_index is None:

        # Some CVs omit an experience heading. Accept a date range only
        # when nearby text resembles a job title and the date is not in
        # a known non-employment section such as Education.
        section_state = None
        for index, raw_line in enumerate(lines):

            line = clean_line(raw_line)
            normalized = line.lower()

            if normalized in EXPERIENCE_HEADINGS:
                section_state = "experience"
            elif normalized in STOP_HEADINGS:
                section_state = "other"

            if not contains_date_range(line) or section_state == "other":
                continue

            context_start = max(0, index - 2)
            context_end = min(len(lines), index + 1)
            context_lines = lines[context_start:context_end]

            if any(looks_like_role(item) for item in context_lines):

                start_index = max(0, index - 2)
                break

    if start_index is None:

        return {
            "section_found": False,
            "section_text": "",
            "lines": [],
        }

    for index in range(start_index, len(lines)):

        line = clean_line(lines[index])

        if is_stop_heading(line):

            end_index = index
            break

    section_lines = [
        clean_line(line)
        for line in lines[start_index:end_index]
        if clean_line(line)
    ]

    return {
        "section_found": True,
        "section_text": "\n".join(section_lines),
        "lines": section_lines,
    }


# ------------------------------------------------------------
# EMPLOYMENT RECORD EXTRACTION
# ------------------------------------------------------------

def extract_employment_history(text):

    lines = text.splitlines()

    section = find_experience_section(lines)

    if not section["section_found"]:

        return {
            "section_found": False,
            "section_text": "",
            "records": [],
        }

    section_lines = section["lines"]

    date_lines = []

    for index, line in enumerate(section_lines):

        date_info = extract_date_from_line(line)

        if date_info:

            date_lines.append(
                {
                    "index": index,
                    "line": line,
                    "date": date_info,
                }
            )

    records = []

    for position, item in enumerate(date_lines):

        date_index = item["index"]
        date_info = item["date"]

        # ----------------------------------------------------
        # Determine record boundaries
        # ----------------------------------------------------

        next_date_index = (
            date_lines[position + 1]["index"]
            if position + 1 < len(date_lines)
            else len(section_lines)
        )

        # ----------------------------------------------------
        # Employer
        # ----------------------------------------------------

        employer = extract_employer_from_date_line(
            item["line"],
            date_info,
        )

        # If no employer is present before the date,
        # look at the preceding line.
        if not employer:

            employer = find_employer_before_date(
                section_lines,
                date_index,
            )

        # ----------------------------------------------------
        # Job title
        # ----------------------------------------------------

        title = extract_title_before_date(
            section_lines,
            date_index,
        )

        # ----------------------------------------------------
        # Evidence
        # ----------------------------------------------------

        evidence_start = max(0, date_index - 1)

        evidence_end = next_date_index

        # If the next employment record has a title immediately
        # before its date, do not include that title as evidence
        # for the current employment record.

        if position + 1 < len(date_lines):

            next_date_index_actual = date_lines[position + 1]["index"]

            if next_date_index_actual > 0:

                possible_next_title = clean_line(
                    section_lines[next_date_index_actual - 1]
                )

                if looks_like_role(possible_next_title):

                    evidence_end = next_date_index_actual - 1


        evidence = []

        for index in range(
            evidence_start,
            evidence_end,
        ):

            line = clean_line(section_lines[index])

            if line:
                evidence.append(line)

        # ----------------------------------------------------
        # Record
        # ----------------------------------------------------

        record = {
            "employer_raw": employer,
            "job_title_raw": title,
            "start_date_raw": date_info["start_date_raw"],
            "end_date_raw": date_info["end_date_raw"],
            "date_range_raw": date_info["date_range_raw"],
            "date_confidence": date_info["date_confidence"],
            "evidence": evidence,
        }

        records.append(record)

    # --------------------------------------------------------
    # Detect overlapping employment
    #
    # We do not attempt to determine whether an overlap is
    # legitimate or erroneous. We simply flag it.
    # --------------------------------------------------------

    overlap_detected = False

    # Basic overlap detection is deferred until normalized
    # dates are available. For now, mark whether multiple
    # simultaneous "Present" jobs exist.

    present_count = 0

    for record in records:

        end_date = record["end_date_raw"]

        if end_date:

            normalized_end = end_date.lower()

            if (
                "present" in normalized_end
                or "current" in normalized_end
                or "to date" in normalized_end
                or normalized_end == "date"
            ):

                present_count += 1

    if present_count > 1:
        overlap_detected = True

    return {
        "section_found": True,
        "section_text": section["section_text"],
        "records": records,
        "overlap_detected": overlap_detected,
    }