import argparse
import csv
import json
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

if __package__:
    from .app_paths import project_directory
    from .candidate_records import OUTPUT_COLUMNS, build_candidate_record
    from .docx_processor import extract_docx_text
    from .process_pdf import process_pdf
else:
    from app_paths import project_directory
    from candidate_records import OUTPUT_COLUMNS, build_candidate_record
    from docx_processor import extract_docx_text
    from process_pdf import process_pdf


APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = project_directory()
INBOX_DIR = PROJECT_DIR / "01_INBOX"
OUTPUT_DIR = PROJECT_DIR / "07_DATABASE"
LOG_DIR = PROJECT_DIR / "08_LOGS"
SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

EVIDENCE_COLUMNS = [
    "Original filename",
    "Source path",
    "Processing result",
    "Document status",
    "Characters",
    "Words",
    "Pages",
    "OCR used",
    "Review reasons",
    "Error",
]


def _safe_spreadsheet_value(value):
    """Prevent CV-controlled text from being interpreted as a spreadsheet formula."""
    if not isinstance(value, str):
        return value
    if value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _escape_vcard_value(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def _fold_vcard_line(line, limit=75):
    """Fold a vCard content line without splitting a UTF-8 character."""
    chunks = []
    current = ""
    current_bytes = 0

    for character in line:
        encoded_size = len(character.encode("utf-8"))
        if current_bytes + encoded_size > limit and current:
            chunks.append(current)
            current = " " + character
            current_bytes = 1 + encoded_size
        else:
            current += character
            current_bytes += encoded_size

    chunks.append(current)
    return "\r\n".join(chunks)


def export_vcards(records, output_dir, timestamp=None):
    """Export extracted contact fields as an importable vCard 3.0 file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    vcard_path = output_dir / f"cv_contacts_{timestamp}.vcf"
    cards = []

    for record in records:
        public = record.get("public", {})
        name = public.get("Candidate", "").strip()
        emails = [
            item.strip()
            for item in public.get("Email", "").split(";")
            if item.strip()
        ]
        phones = [
            item.strip()
            for item in public.get("Phone", "").split(";")
            if item.strip()
        ]

        if not (name or emails or phones):
            continue

        display_name = name or (emails[0] if emails else phones[0])
        source = record.get("evidence", {}).get("source_path", "")
        uid_source = "|".join([source, display_name, *emails, *phones])
        uid = uuid.uuid5(uuid.NAMESPACE_URL, uid_source)
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"UID:{uid}",
            f"FN:{_escape_vcard_value(display_name)}",
            f"N:;{_escape_vcard_value(display_name)};;;",
        ]
        lines.extend(
            f"EMAIL;TYPE=INTERNET:{_escape_vcard_value(email)}"
            for email in emails
        )
        lines.extend(
            f"TEL;TYPE=CELL:{_escape_vcard_value(phone)}"
            for phone in phones
        )
        lines.append("END:VCARD")
        cards.extend(_fold_vcard_line(line) for line in lines)

    with vcard_path.open("w", encoding="utf-8", newline="") as file:
        if cards:
            file.write("\r\n".join(cards) + "\r\n")
    return vcard_path


def process_candidate_file(file_path):
    """Extract one supported document into a public record and audit evidence."""
    file_path = Path(file_path)
    evidence = {
        "source_filename": file_path.name,
        "source_path": str(file_path.resolve()),
        "processing_result": "ERROR",
        "error_message": "",
        "review_reasons": [],
    }

    try:
        if file_path.suffix.lower() == ".pdf":
            with tempfile.TemporaryDirectory(prefix="cv_pre_ai_") as temp_dir:
                temporary_pdf = Path(temp_dir) / file_path.name
                shutil.copy2(file_path, temporary_pdf)
                document_record = process_pdf(temporary_pdf)

            text = document_record["content"]["full_text"]
            document_metadata = document_record.get("document", {})
        elif file_path.suffix.lower() == ".docx":
            docx_result = extract_docx_text(file_path)
            text = docx_result.get("text", "")
            document_metadata = {
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "document_type": "DOCX",
                "size_bytes": file_path.stat().st_size,
                "page_count": None,
                "ocr_used": False,
            }
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        record = build_candidate_record(
            file_path,
            text,
            document_metadata=document_metadata,
        )
        return record
    except Exception as exc:
        public = {column: "" for column in OUTPUT_COLUMNS}
        public["Status"] = "Error"
        evidence["error_message"] = f"{type(exc).__name__}: {exc}"
        evidence["review_reasons"] = ["Document processing failed"]
        return {"public": public, "evidence": evidence}


def _write_csv(records, csv_path):
    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    column: _safe_spreadsheet_value(
                        record["public"].get(column, "")
                    )
                    for column in OUTPUT_COLUMNS
                }
            )


def _write_workbook(records, workbook_path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.worksheet.table import Table, TableStyleInfo
    except ImportError as exc:
        raise RuntimeError(
            "Excel export requires openpyxl. Install it in this "
            "environment, then run the batch again."
        ) from exc

    workbook = Workbook()
    candidates = workbook.active
    candidates.title = "Candidates"
    candidates.append(OUTPUT_COLUMNS)

    for record in records:
        row = [
            _safe_spreadsheet_value(record["public"].get(column, ""))
            for column in OUTPUT_COLUMNS
        ]
        candidates.append(row)

        source_path = record.get("evidence", {}).get("source_path")
        if source_path and record["public"].get("Candidate"):
            candidates.cell(
                row=candidates.max_row,
                column=1,
            ).hyperlink = Path(source_path).as_uri()
            candidates.cell(
                row=candidates.max_row,
                column=1,
            ).style = "Hyperlink"

    candidates.freeze_panes = "A2"
    candidates.auto_filter.ref = candidates.dimensions
    candidates.row_dimensions[1].height = 30
    candidates.sheet_view.showGridLines = False

    for cell in candidates[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.alignment = Alignment(vertical="center", wrap_text=True)

    for column_cells in candidates.columns:
        column_letter = column_cells[0].column_letter
        values = [
            len(str(cell.value or ""))
            for cell in column_cells[1:101]
        ]
        width = max([len(str(column_cells[0].value))] + values) + 2
        candidates.column_dimensions[column_letter].width = min(
            max(width, 14), 42
        )

    if candidates.max_row > 1:
        table = Table(
            displayName="CandidateRecords",
            ref=candidates.dimensions,
        )
        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False,
        )
        candidates.add_table(table)

    evidence_sheet = workbook.create_sheet("Processing Details")
    evidence_sheet.append(EVIDENCE_COLUMNS)
    for record in records:
        evidence = record.get("evidence", {})
        document = evidence.get("document_assessment", {})
        metadata = evidence.get("document_metadata", {})
        evidence_sheet.append([
            _safe_spreadsheet_value(
                evidence.get("source_filename", "")
            ),
            _safe_spreadsheet_value(evidence.get("source_path", "")),
            _safe_spreadsheet_value(
                evidence.get("processing_result", "ERROR")
            ),
            _safe_spreadsheet_value(document.get("status", "")),
            _safe_spreadsheet_value(
                document.get("character_count", "")
            ),
            _safe_spreadsheet_value(document.get("word_count", "")),
            _safe_spreadsheet_value(metadata.get("page_count", "")),
            _safe_spreadsheet_value(metadata.get("ocr_used", "")),
            _safe_spreadsheet_value(
                " ; ".join(evidence.get("review_reasons", []))
            ),
            _safe_spreadsheet_value(evidence.get("error_message", "")),
        ])
        source = evidence.get("source_path")
        if source:
            evidence_sheet.cell(
                row=evidence_sheet.max_row,
                column=1,
            ).hyperlink = Path(source).as_uri()
            evidence_sheet.cell(
                row=evidence_sheet.max_row,
                column=1,
            ).style = "Hyperlink"

    evidence_sheet.freeze_panes = "A2"
    evidence_sheet.auto_filter.ref = evidence_sheet.dimensions
    evidence_sheet.sheet_view.showGridLines = False
    for cell in evidence_sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for column_cells in evidence_sheet.columns:
        column_letter = column_cells[0].column_letter
        evidence_sheet.column_dimensions[column_letter].width = min(
            max(
                len(str(column_cells[0].value)),
                *(
                    len(str(cell.value or ""))
                    for cell in column_cells[1:101]
                ),
            )
            + 2,
            55,
        )

    workbook.save(workbook_path)


def export_batch(records, output_dir, timestamp=None):
    """Write the user-facing exports and complete evidence sidecar."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    base = output_dir / f"cv_database_{timestamp}"
    csv_path = base.with_suffix(".csv")
    workbook_path = base.with_suffix(".xlsx")
    evidence_path = output_dir / f"cv_database_{timestamp}_evidence.json"

    _write_csv(records, csv_path)
    _write_workbook(records, workbook_path)
    vcard_path = export_vcards(records, output_dir, timestamp=timestamp)
    with evidence_path.open("w", encoding="utf-8") as file:
        json.dump(
            [record.get("evidence", {}) for record in records],
            file,
            ensure_ascii=False,
            indent=2,
        )

    return csv_path, workbook_path, evidence_path, vcard_path


def process_batch(
    inbox_dir=INBOX_DIR,
    output_dir=OUTPUT_DIR,
    log_dir=LOG_DIR,
    progress_callback=None,
):
    """Process all supported inbox documents; reusable by a future GUI."""
    inbox_dir = Path(inbox_dir)
    output_dir = Path(output_dir)
    log_dir = Path(log_dir)

    if not inbox_dir.is_dir():
        raise FileNotFoundError(f"Inbox folder does not exist: {inbox_dir}")

    files = sorted(
        file_path
        for file_path in inbox_dir.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not file_path.stem.casefold().endswith("_ocr")
    )
    if not files:
        return []

    records = []
    for index, file_path in enumerate(files, start=1):
        record = process_candidate_file(file_path)
        records.append(record)
        if progress_callback:
            progress_callback(
                index,
                len(files),
                file_path.name,
                record["public"].get("Status", ""),
            )

    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path, workbook_path, evidence_path, vcard_path = export_batch(
        records,
        output_dir,
        timestamp=timestamp,
    )
    log_path = log_dir / f"cv_database_log_{timestamp}.txt"
    with log_path.open("w", encoding="utf-8") as file:
        for record in records:
            evidence = record.get("evidence", {})
            file.write(
                f"{evidence.get('source_filename', '')}\t"
                f"{evidence.get('processing_result', 'ERROR')}\t"
                f"{record['public'].get('Status', '')}\t"
                f"{evidence.get('error_message', '')}\n"
            )

    return {
        "records": records,
        "csv_path": csv_path,
        "workbook_path": workbook_path,
        "evidence_path": evidence_path,
        "vcard_path": vcard_path,
        "log_path": log_path,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Analyze CVs and export reviewable candidate reports."
    )
    parser.add_argument(
        "--inbox",
        type=Path,
        default=INBOX_DIR,
        help="Folder containing the PDF/DOCX files to process.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Folder for the CSV, Excel, and evidence exports.",
    )
    parser.add_argument(
        "--logs",
        type=Path,
        default=LOG_DIR,
        help="Folder for processing logs.",
    )
    args = parser.parse_args(argv)

    if not args.inbox.is_dir():
        parser.error(f"Inbox folder does not exist: {args.inbox}")

    print("=" * 65)
    print("CV / RESUME ANALYZER")
    print("=" * 65)
    print(f"Input folder : {args.inbox}")

    def show_progress(index, total, filename, status):
        print(f"[{index}/{total}] {filename} — {status}")

    result = process_batch(
        inbox_dir=args.inbox,
        output_dir=args.output,
        log_dir=args.logs,
        progress_callback=show_progress,
    )
    if not result:
        print("No PDF or DOCX files found in the inbox.")
        print(f"Place your CVs here:\n{INBOX_DIR}")
        return

    records = result["records"]
    successful = sum(
        record["evidence"].get("processing_result") == "SUCCESS"
        for record in records
    )
    errors = len(records) - successful
    needs_review = sum(
        record["public"].get("Status") == "Needs review"
        for record in records
    )

    print()
    print("=" * 65)
    print("BATCH COMPLETE")
    print("=" * 65)
    print(f"Total files         : {len(records)}")
    print(f"Processed           : {successful}")
    print(f"Processing errors   : {errors}")
    print(f"Records needing review: {needs_review}")
    print(f"\nExcel report:\n{result['workbook_path']}")
    print(f"\nCSV report:\n{result['csv_path']}")
    print(f"\nEvidence data:\n{result['evidence_path']}")
    print(f"\nContact vCards:\n{result['vcard_path']}")
    print(f"\nProcessing log:\n{result['log_path']}")


if __name__ == "__main__":
    main()
