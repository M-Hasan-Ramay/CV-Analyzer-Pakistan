import re


# ------------------------------------------------------------
# MONTH NORMALIZATION
# ------------------------------------------------------------

MONTH_MAP = {
    "january": 1,
    "jan": 1,

    "february": 2,
    "feb": 2,

    "march": 3,
    "mar": 3,

    "april": 4,
    "apr": 4,

    "may": 5,

    "june": 6,
    "jun": 6,

    "july": 7,
    "jul": 7,

    "august": 8,
    "aug": 8,

    "september": 9,
    "sep": 9,
    "sept": 9,

    "october": 10,
    "oct": 10,

    "november": 11,
    "nov": 11,

    "december": 12,
    "dec": 12,
}


# ------------------------------------------------------------
# BASIC HELPERS
# ------------------------------------------------------------

def clean_text(value):

    if value is None:
        return None

    return re.sub(r"\s+", " ", str(value).strip())


def normalize_month_name(month_text):

    if not month_text:
        return None

    key = clean_text(month_text).lower().rstrip(".,")

    return MONTH_MAP.get(key)


# ------------------------------------------------------------
# OPEN / CURRENT DATE DETECTION
# ------------------------------------------------------------

def is_current_date(value):

    if not value:
        return False

    normalized = clean_text(value).lower()

    current_values = {
        "present",
        "current",
        "to date",
        "date",
        "till date",
        "until date",
        "ongoing",
        "currently",
    }

    return normalized in current_values


# ------------------------------------------------------------
# SINGLE DATE NORMALIZATION
# ------------------------------------------------------------

def normalize_single_date(value):

    """
    Normalize one employment date.

    Returns a structured representation.

    Examples:

        July 2025
        Jan-2020
        2018
        Apr, 2015
    """

    raw = clean_text(value)

    if not raw:

        return {
            "raw": value,
            "year": None,
            "month": None,
            "precision": None,
            "is_current": False,
            "confidence": "none",
        }

    # --------------------------------------------------------
    # Current / Present
    # --------------------------------------------------------

    if is_current_date(raw):

        return {
            "raw": raw,
            "year": None,
            "month": None,
            "precision": "open",
            "is_current": True,
            "confidence": "high",
        }

    # --------------------------------------------------------
    # Month + Year
    #
    # Examples:
    # July 2025
    # Jul 2025
    # Jan-2020
    # Apr, 2015
    # --------------------------------------------------------

    month_pattern = re.compile(
        r"\b("
        r"january|february|march|april|may|june|july|august|"
        r"september|october|november|december|"
        r"jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
        r")"
        r"\s*[-/.,]?\s*"
        r"(\d{4})\b",
        re.IGNORECASE,
    )

    match = month_pattern.search(raw)

    if match:

        month = normalize_month_name(match.group(1))
        year = int(match.group(2))

        return {
            "raw": raw,
            "year": year,
            "month": month,
            "precision": "month",
            "is_current": False,
            "confidence": "high",
        }

    # --------------------------------------------------------
    # Year only
    # --------------------------------------------------------

    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", raw)

    if year_match:

        year = int(year_match.group(1))

        return {
            "raw": raw,
            "year": year,
            "month": None,
            "precision": "year",
            "is_current": False,
            "confidence": "medium",
        }

    # --------------------------------------------------------
    # Unrecognized
    # --------------------------------------------------------

    return {
        "raw": raw,
        "year": None,
        "month": None,
        "precision": None,
        "is_current": False,
        "confidence": "low",
    }


# ------------------------------------------------------------
# EMPLOYMENT DATE NORMALIZATION
# ------------------------------------------------------------

def normalize_employment_dates(record):

    """
    Take an employment record produced by employment_extractor
    and add normalized start/end date structures.

    Original raw fields are preserved.
    """

    start_raw = record.get("start_date_raw")
    end_raw = record.get("end_date_raw")

    start = normalize_single_date(start_raw)
    end = normalize_single_date(end_raw)

    normalized = dict(record)

    normalized["start_date"] = start
    normalized["end_date"] = end

    return normalized


# ------------------------------------------------------------
# NORMALIZE COMPLETE EMPLOYMENT RESULT
# ------------------------------------------------------------

def normalize_employment_result(employment_result):

    """
    Normalize all employment records returned by
    extract_employment_history().
    """

    result = dict(employment_result)

    records = []

    for record in employment_result.get("records", []):

        records.append(
            normalize_employment_dates(record)
        )

    result["records"] = records

    return result


# ------------------------------------------------------------
# SIMPLE TEST MODE
# ------------------------------------------------------------

if __name__ == "__main__":

    test_values = [
        "July 2025",
        "January 2016",
        "Jun-2010",
        "Apr, 2015",
        "2018",
        "Present",
        "to date",
    ]

    print("=" * 70)
    print("DATE NORMALIZER TEST")
    print("=" * 70)

    for value in test_values:

        print()
        print(f"INPUT: {value}")
        print(normalize_single_date(value))