from datetime import datetime
from pathlib import Path


def create_document_record(
    file_path,
    document_type,
    text,
    pages,
    page_count,
    ocr_used=False
):

    path = Path(file_path)

    return {
        "schema_version": "1.0",

        "document": {
            "filename": path.name,
            "extension": path.suffix.lower(),
            "document_type": document_type,
            "size_bytes": path.stat().st_size,
            "page_count": page_count,
            "ocr_used": ocr_used,
            "processed_at": datetime.now().isoformat()
        },

        "content": {
            "full_text": text,
            "pages": pages
        }
    }