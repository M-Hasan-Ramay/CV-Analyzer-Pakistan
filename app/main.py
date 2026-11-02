import sys
import os

from document_inspector import inspect_document
from pdf_processor import extract_pdf_text
from docx_processor import extract_docx_text
from pre_ai import run_pre_ai
from employment_extractor import extract_employment_history
from date_normalizer import normalize_employment_result
from experience_calculator import calculate_experience
from education_extractor import extract_education
from certification_extractor import (
    extract_certifications,
    print_certification_summary,
)


def print_separator(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def extract_document_text(file_path, document_info):

    if document_info["file_type"] == "PDF":
        return extract_pdf_text(file_path)

    if document_info["file_type"] == "DOCX":
        return extract_docx_text(file_path)

    raise ValueError(
        f"Unsupported document type: {document_info['file_type']}"
    )


def get_text_and_page_count(extracted):

    text = extracted.get("text", "")

    page_count = extracted.get("page_count")

    return text, page_count


def print_document_info(document_info, page_count, text):

    print_separator("DOCUMENT INFORMATION")

    print(f"File: {document_info['file_name']}")
    print(f"Type: {document_info['file_type']}")
    print(f"Extension: {document_info['extension']}")
    print(f"Size: {document_info['size_bytes']:,} bytes")
    print(f"Supported: {document_info['supported']}")

    if page_count is not None:
        print(f"Pages: {page_count}")

    print(f"Characters: {len(text):,}")
    print(f"Words: {len(text.split()):,}")


def print_pre_ai(pre_ai_result):

    print_separator("PRE-AI ANALYSIS")

    assessment = pre_ai_result.get("document_assessment", {})

    print("DOCUMENT ASSESSMENT")

    for key, value in assessment.items():
        print(f"{key}: {value}")

    contact = pre_ai_result.get("contact", {})

    print()
    print("CONTACT")

    print("Emails:")

    emails = contact.get("emails", [])

    if emails:
        for item in emails:
            print(f"  - {item}")
    else:
        print("  None detected")

    print("Phones:")

    phones = contact.get("phones", [])

    if phones:
        for item in phones:
            print(f"  - {item}")
    else:
        print("  None detected")

    print("LinkedIn:")

    linkedin = contact.get("linkedin", [])

    if linkedin:
        for item in linkedin:
            print(f"  - {item}")
    else:
        print("  None detected")

    print("URLs:")

    urls = contact.get("urls", [])

    if urls:
        for item in urls:
            print(f"  - {item}")
    else:
        print("  None detected")

    signals = pre_ai_result.get("signals", {})

    print()
    print("CERTIFICATIONS")

    certifications = signals.get("certifications", [])

    if certifications:
        for item in certifications:
            print(f"  - {item}")
    else:
        print("  None detected")

    print()
    print("DEGREE SIGNALS")

    degrees = signals.get("degrees", [])

    if degrees:
        for item in degrees:
            print(f"  - {item}")
    else:
        print("  None detected")

    print()
    print("TECHNOLOGY / ROLE SIGNALS")

    # IMPORTANT:
    # pre_ai.py returns signals["keywords"],
    # not signals["keyword_groups"].

    keywords = signals.get("keywords", {})

    found_any = False

    for group_name, values in keywords.items():

        if values:

            found_any = True

            print(f"[{group_name.upper()}]")

            for value in values:
                print(f"  - {value}")

    if not found_any:
        print("  None detected")


def print_employment(employment_result):

    print_separator("EMPLOYMENT EXTRACTION")

    section_found = employment_result.get(
        "section_found",
        False
    )

    print(
        f"Experience section found: "
        f"{section_found}"
    )

    records = employment_result.get(
        "records",
        []
    )

    print(
        f"Employment records: "
        f"{len(records)}"
    )

    for index, record in enumerate(records, start=1):

        print()
        print(f"RECORD {index}")

        print(
            f"Employer: "
            f"{record.get('employer_raw')}"
        )

        print(
            f"Job Title: "
            f"{record.get('job_title_raw')}"
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
            f"Date Range: "
            f"{record.get('date_range_raw')}"
        )

        print(
            f"Date Confidence: "
            f"{record.get('date_confidence')}"
        )


def print_date_normalization(normalized_result):

    print_separator("DATE NORMALIZATION")

    records = normalized_result.get(
        "records",
        []
    )

    if not records:

        print(
            "No employment records to normalize."
        )

        return

    for index, record in enumerate(
        records,
        start=1
    ):

        print()
        print(f"RECORD {index}")

        print(
            f"Employer: "
            f"{record.get('employer_raw')}"
        )

        print(
            f"Job Title: "
            f"{record.get('job_title_raw')}"
        )

        start_date = record.get(
            "start_date",
            {}
        )

        end_date = record.get(
            "end_date",
            {}
        )

        print("Start:")

        print(
            f"  Raw: "
            f"{start_date.get('raw')}"
        )

        print(
            f"  Year: "
            f"{start_date.get('year')}"
        )

        print(
            f"  Month: "
            f"{start_date.get('month')}"
        )

        print(
            f"  Precision: "
            f"{start_date.get('precision')}"
        )

        print(
            f"  Current: "
            f"{start_date.get('is_current')}"
        )

        print(
            f"  Confidence: "
            f"{start_date.get('confidence')}"
        )

        print("End:")

        print(
            f"  Raw: "
            f"{end_date.get('raw')}"
        )

        print(
            f"  Year: "
            f"{end_date.get('year')}"
        )

        print(
            f"  Month: "
            f"{end_date.get('month')}"
        )

        print(
            f"  Precision: "
            f"{end_date.get('precision')}"
        )

        print(
            f"  Current: "
            f"{end_date.get('is_current')}"
        )

        print(
            f"  Confidence: "
            f"{end_date.get('confidence')}"
        )


def print_experience(experience_result):

    print_separator("EXPERIENCE CALCULATION")

    records = experience_result.get(
        "records",
        []
    )

    for record in records:

        index = record.get(
            "record_index"
        )

        employer = record.get(
            "employer_raw"
        )

        role = record.get(
            "job_title_raw"
        )

        duration = record.get(
            "duration",
            {}
        )

        years = duration.get(
            "years",
            0
        )

        months = duration.get(
            "months",
            0
        )

        print()
        print(
            f"{index}. {employer}"
        )

        print(
            f"   Role: {role}"
        )

        print(
            f"   Duration: "
            f"{years} years {months} months"
        )

    total = experience_result.get(
        "total_calendar_experience",
        {}
    )

    print()

    total_years = total.get(
        "years",
        0
    )

    total_months = total.get(
        "months",
        0
    )

    print(
        f"TOTAL CALENDAR EXPERIENCE: "
        f"{total_years} years "
        f"{total_months} months"
    )

    print(
        f"OVERLAP DETECTED: "
        f"{experience_result.get('overlap_detected')}"
    )

    print(
        f"GAP DETECTED: "
        f"{experience_result.get('gap_detected')}"
    )

    overlaps = experience_result.get(
        "overlaps",
        []
    )

    if overlaps:

        print()
        print("OVERLAPS")

        for overlap in overlaps:

            record_a = overlap.get(
                "record_a"
            )

            record_b = overlap.get(
                "record_b"
            )

            overlap_months = overlap.get(
                "overlap_months"
            )

            print(
                f"  Records {record_a} "
                f"and {record_b}: "
                f"{overlap_months} months"
            )

    gaps = experience_result.get(
        "gaps",
        []
    )

    if gaps:

        print()
        print("GAPS")

        for gap in gaps:

            record_a = gap.get(
                "record_a"
            )

            record_b = gap.get(
                "record_b"
            )

            gap_months = gap.get(
                "gap_months"
            )

            print(
                f"  Gap between records "
                f"{record_a} and {record_b}: "
                f"{gap_months} months"
            )


def print_education(education_result):

    print_separator("EDUCATION EXTRACTION")

    section_found = education_result.get(
        "section_found",
        False
    )

    print(
        f"Education section found: "
        f"{section_found}"
    )

    records = education_result.get(
        "records",
        []
    )

    print(
        f"Education records: "
        f"{len(records)}"
    )

    for index, record in enumerate(
        records,
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

        print(
            f"Confidence: "
            f"{record.get('confidence')}"
        )


def process_file(file_path):

    print_separator("CV AI PROCESSOR")

    print(
        f"Processing: {file_path}"
    )

    # ---------------------------------------------------------
    # 1. DOCUMENT INSPECTION
    # ---------------------------------------------------------

    document_info = inspect_document(
        file_path
    )

    if not document_info["supported"]:

        print()
        print(
            f"ERROR: Unsupported file type: "
            f"{document_info['extension']}"
        )

        return

    # ---------------------------------------------------------
    # 2. TEXT EXTRACTION
    # ---------------------------------------------------------

    extracted = extract_document_text(
        file_path,
        document_info
    )

    text, page_count = get_text_and_page_count(
        extracted
    )

    print_document_info(
        document_info,
        page_count,
        text
    )

    if not text.strip():

        print()
        print(
            "ERROR: No text could be extracted "
            "from the document."
        )

        return

    print()
    print("Text successfully extracted.")

    # ---------------------------------------------------------
    # 3. PRE-AI
    # ---------------------------------------------------------

    pre_ai_result = run_pre_ai(
        text
    )

    print_pre_ai(
        pre_ai_result
    )

    # ---------------------------------------------------------
    # 4. EMPLOYMENT EXTRACTION
    # ---------------------------------------------------------

    employment_result = extract_employment_history(
        text
    )

    print_employment(
        employment_result
    )

    # ---------------------------------------------------------
    # 5. DATE NORMALIZATION
    # ---------------------------------------------------------

    normalized_employment = normalize_employment_result(
        employment_result
    )

    print_date_normalization(
        normalized_employment
    )

    # ---------------------------------------------------------
    # 6. EXPERIENCE CALCULATION
    # ---------------------------------------------------------

    experience_result = calculate_experience(
        normalized_employment
    )

    print_experience(
        experience_result
    )

    # ---------------------------------------------------------
    # 7. EDUCATION
    # ---------------------------------------------------------

    education_result = extract_education(
        text
    )

    print_education(
        education_result
    )
    
    certification_result = extract_certifications(
        text
    )

    print_certification_summary(
        certification_result
    )
    # ---------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------

    print_separator(
        "PROCESSING COMPLETE"
    )

    print(
        f"Successfully processed: "
        f"{document_info['file_name']}"
    )


def main():

    if len(sys.argv) != 2:

        print(
            "Usage:\n"
            "python main.py "
            "\"FULL_PATH_TO_CV\""
        )

        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):

        print(
            f"ERROR: File not found:\n"
            f"{file_path}"
        )

        sys.exit(1)

    try:

        process_file(
            file_path
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("PROCESSING ERROR")
        print("=" * 70)

        print(
            type(error).__name__
        )

        print(
            str(error)
        )

        print()
        print(
            "The original CV file "
            "has not been modified."
        )

        sys.exit(1)


if __name__ == "__main__":
    main()