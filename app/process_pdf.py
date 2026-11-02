from pathlib import Path

if __package__:
    from .pdf_processor import extract_pdf_text
    from .canonical_document import create_document_record
else:
    from pdf_processor import extract_pdf_text
    from canonical_document import create_document_record


def process_pdf(pdf_path):

    pdf_path = Path(pdf_path)

    print(f"\nProcessing: {pdf_path.name}")

    # -------------------------------------------------
    # STEP 1: Try normal text extraction
    # -------------------------------------------------

    result = extract_pdf_text(pdf_path)

    if result["has_text"]:

        print("Text layer detected.")
        print("OCR not required.")

        return create_document_record(
            file_path=pdf_path,
            document_type="PDF",
            text=result["text"],
            pages=result["pages"],
            page_count=result["page_count"],
            ocr_used=False
        )

    # -------------------------------------------------
    # STEP 2: OCR required
    # -------------------------------------------------

    print("Insufficient text detected.")
    print("OCR required.")

    result = extract_pdf_text(pdf_path, use_ocr=True)

    if len("".join(result["text"].split())) < 10:

        raise RuntimeError(
            "OCR completed but usable text "
            "was not detected."
        )

    print("OCR successful.")
    print(
        f"Extracted {len(result['text']):,} characters."
    )

    return create_document_record(
        file_path=pdf_path,
        document_type="PDF",
        text=result["text"],
        pages=result["pages"],
        page_count=result["page_count"],
        ocr_used=True
    )