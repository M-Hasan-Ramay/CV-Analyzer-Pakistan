from datetime import date


def get_current_year_month():
    """
    Return the current year and month.

    Example:
        (2026, 9)
    """

    today = date.today()

    return today.year, today.month


def date_to_month_index(normalized_date, is_start=True):
    """
    Convert a normalized date into a continuous month index.

    Month-level dates:
        July 2025 -> July 2025

    Year-only dates:
        Start -> January of that year
        End   -> December of that year

    Open/current dates:
        Current year/month

    This is used internally for calculations only.
    The original date precision remains preserved elsewhere.
    """

    if normalized_date is None:
        return None

    precision = normalized_date.get("precision")

    year = normalized_date.get("year")
    month = normalized_date.get("month")

    is_current = normalized_date.get("is_current", False)

    # Current / Present / To Date
    if is_current:

        year, month = get_current_year_month()

        return year * 12 + month

    # No usable year
    if year is None:
        return None

    # Exact month available
    if precision == "month" and month is not None:

        return year * 12 + month

    # Year-only date
    if precision == "year":

        if is_start:

            # Assume January internally
            return year * 12 + 1

        else:

            # Assume December internally
            return year * 12 + 12

    return None


def months_to_duration(total_months):
    """
    Convert total months into years + remaining months.

    Examples:

        15 months  -> 1 year 3 months
        51 months  -> 4 years 3 months
        59 months  -> 4 years 11 months
        129 months -> 10 years 9 months
        188 months -> 15 years 8 months
    """

    if total_months is None:
        return {
            "total_months": None,
            "years": None,
            "months": None
        }

    if total_months < 0:
        total_months = 0

    years = total_months // 12
    months = total_months % 12

    return {
        "total_months": total_months,
        "years": years,
        "months": months
    }


def calculate_interval(start_date, end_date):
    """
    Calculate the inclusive duration between two normalized dates.

    Example:

        July 2025 -> September 2026

        = 15 months

    The calculation is inclusive because the CV gives employment
    periods by month rather than exact days.
    """

    start_index = date_to_month_index(
        start_date,
        is_start=True
    )

    end_index = date_to_month_index(
        end_date,
        is_start=False
    )

    if start_index is None or end_index is None:
        return None

    if end_index < start_index:
        return {
            "total_months": None,
            "years": None,
            "months": None,
            "invalid": True
        }

    total_months = end_index - start_index + 1

    duration = months_to_duration(total_months)

    duration["invalid"] = False

    return duration


def build_intervals(employment_result):
    """
    Build internal employment intervals.

    Each interval contains:

        record_index
        employer
        job_title
        start_index
        end_index
        start_date
        end_date
    """

    intervals = []

    records = employment_result.get("records", [])

    for index, record in enumerate(records):

        start_date = record.get("start_date")
        end_date = record.get("end_date")

        start_index = date_to_month_index(
            start_date,
            is_start=True
        )

        end_index = date_to_month_index(
            end_date,
            is_start=False
        )

        if start_index is None or end_index is None:
            continue

        if end_index < start_index:
            continue

        intervals.append({
            "record_index": index,
            "employer_raw": record.get("employer_raw"),
            "job_title_raw": record.get("job_title_raw"),
            "start_index": start_index,
            "end_index": end_index,
            "start_date": start_date,
            "end_date": end_date
        })

    return intervals


def calculate_record_durations(employment_result):
    """
    Calculate duration for every employment record.
    """

    results = []

    records = employment_result.get("records", [])

    for index, record in enumerate(records):

        start_date = record.get("start_date")
        end_date = record.get("end_date")

        duration = calculate_interval(
            start_date,
            end_date
        )

        if duration is None:

            duration = {
                "total_months": None,
                "years": None,
                "months": None,
                "invalid": True
            }

        new_record = dict(record)

        new_record["duration"] = duration

        new_record["record_index"] = index

        results.append(new_record)

    return results


def detect_overlaps(intervals):
    """
    Detect pairwise overlapping employment periods.

    Returns:

        [
            {
                "record_a": 0,
                "record_b": 1,
                "overlap_months": 15
            }
        ]
    """

    overlaps = []

    for i in range(len(intervals)):

        current = intervals[i]

        for j in range(i + 1, len(intervals)):

            other = intervals[j]

            overlap_start = max(
                current["start_index"],
                other["start_index"]
            )

            overlap_end = min(
                current["end_index"],
                other["end_index"]
            )

            if overlap_start <= overlap_end:

                overlap_months = (
                    overlap_end
                    - overlap_start
                    + 1
                )

                overlaps.append({
                    "record_a": current["record_index"],
                    "record_b": other["record_index"],
                    "overlap_months": overlap_months
                })

    return overlaps


def merge_intervals(intervals):
    """
    Merge overlapping or directly adjacent calendar intervals.

    This is used to calculate unique calendar experience without
    double-counting concurrent employment.
    """

    if not intervals:
        return []

    sorted_intervals = sorted(
        intervals,
        key=lambda item: (
            item["start_index"],
            item["end_index"]
        )
    )

    merged = []

    current_start = sorted_intervals[0]["start_index"]
    current_end = sorted_intervals[0]["end_index"]

    for interval in sorted_intervals[1:]:

        start = interval["start_index"]
        end = interval["end_index"]

        # Overlap or immediately adjacent
        if start <= current_end + 1:

            current_end = max(
                current_end,
                end
            )

        else:

            merged.append({
                "start_index": current_start,
                "end_index": current_end
            })

            current_start = start
            current_end = end

    merged.append({
        "start_index": current_start,
        "end_index": current_end
    })

    return merged


def calculate_merged_total_months(merged_intervals):
    """
    Calculate the total number of unique calendar months.
    """

    total = 0

    for interval in merged_intervals:

        total += (
            interval["end_index"]
            - interval["start_index"]
            + 1
        )

    return total


def detect_gaps(intervals):
    """
    Detect gaps between employment periods.

    Important:
    Gaps are detected using the original employment intervals,
    not the merged intervals.

    Example:

        April 2015
        January 2016

    produces:

        8 month gap
    """

    gaps = []

    if len(intervals) < 2:
        return gaps

    sorted_intervals = sorted(
        intervals,
        key=lambda item: (
            item["start_index"],
            item["end_index"]
        )
    )

    for i in range(len(sorted_intervals) - 1):

        current = sorted_intervals[i]
        next_interval = sorted_intervals[i + 1]

        # If the next employment starts after the current
        # employment ends, there may be a gap.
        if next_interval["start_index"] > current["end_index"] + 1:

            gap_months = (
                next_interval["start_index"]
                - current["end_index"]
                - 1
            )

            gaps.append({
                "record_a": current["record_index"],
                "record_b": next_interval["record_index"],
                "gap_months": gap_months
            })

    return gaps


def calculate_experience(employment_result):
    """
    Complete experience calculation.

    Returns:

        records
        total_calendar_experience
        merged_intervals
        overlaps
        gaps
        overlap_detected
        gap_detected
    """

    # ------------------------------------------------------------
    # INDIVIDUAL RECORD DURATIONS
    # ------------------------------------------------------------

    records = calculate_record_durations(
        employment_result
    )

    # ------------------------------------------------------------
    # INTERNAL INTERVALS
    # ------------------------------------------------------------

    intervals = build_intervals(
        employment_result
    )

    # ------------------------------------------------------------
    # OVERLAPS
    # ------------------------------------------------------------

    overlaps = detect_overlaps(
        intervals
    )

    # ------------------------------------------------------------
    # GAPS
    # ------------------------------------------------------------

    gaps = detect_gaps(
        intervals
    )

    # ------------------------------------------------------------
    # UNIQUE CALENDAR EXPERIENCE
    # ------------------------------------------------------------

    merged_intervals = merge_intervals(
        intervals
    )

    total_months = calculate_merged_total_months(
        merged_intervals
    )

    total_calendar_experience = months_to_duration(
        total_months
    )

    # ------------------------------------------------------------
    # RESULT
    # ------------------------------------------------------------

    return {
        "records": records,

        "total_calendar_experience":
            total_calendar_experience,

        "merged_intervals":
            merged_intervals,

        "overlaps":
            overlaps,

        "gaps":
            gaps,

        "overlap_detected":
            len(overlaps) > 0,

        "gap_detected":
            len(gaps) > 0
    }


def print_experience_summary(result):
    """
    Print a human-readable experience summary.
    """

    print()
    print("=" * 70)
    print("EXPERIENCE SUMMARY")
    print("=" * 70)

    for index, record in enumerate(
        result["records"],
        start=1
    ):

        duration = record["duration"]

        print()
        print(
            f"{index}. "
            f"{record['employer_raw']}"
        )

        print(
            f"   Role: "
            f"{record['job_title_raw']}"
        )

        if duration["total_months"] is None:

            print(
                "   Duration: "
                "Unable to calculate"
            )

        else:

            print(
                f"   Duration: "
                f"{duration['years']} years "
                f"{duration['months']} months"
            )

    total = result["total_calendar_experience"]

    print()
    print("-" * 70)

    print(
        "TOTAL CALENDAR EXPERIENCE: "
        f"{total['years']} years "
        f"{total['months']} months"
    )

    print(
        f"OVERLAP DETECTED: "
        f"{result['overlap_detected']}"
    )

    print(
        f"GAP DETECTED: "
        f"{result['gap_detected']}"
    )

    if result["overlaps"]:

        print()
        print("OVERLAPS")

        for overlap in result["overlaps"]:

            print(
                f"  Records "
                f"{overlap['record_a'] + 1} and "
                f"{overlap['record_b'] + 1}: "
                f"{overlap['overlap_months']} months"
            )

    if result["gaps"]:

        print()
        print("GAPS")

        for gap in result["gaps"]:

            print(
                f"  Gap between records "
                f"{gap['record_a'] + 1} and "
                f"{gap['record_b'] + 1}: "
                f"{gap['gap_months']} months"
            )