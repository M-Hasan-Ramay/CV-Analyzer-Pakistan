import os


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf": "PDF",
    ".docx": "DOCX",
}


# ============================================================
# DOCUMENT INSPECTION
# ============================================================

def inspect_document(file_path):
    """
    Inspect a document before processing.

    Returns:

        {
            "file_name": str,
            "file_path": str,
            "extension": str,
            "file_type": str,
            "size_bytes": int,
            "supported": bool,
            "page_count": None
        }

    Page count is deliberately not determined here because
    PDF/DOCX processors are responsible for reading documents.
    """

    if not os.path.isfile(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    file_name = os.path.basename(
        file_path
    )

    extension = os.path.splitext(
        file_name
    )[1].lower()

    size_bytes = os.path.getsize(
        file_path
    )

    supported = (
        extension in SUPPORTED_EXTENSIONS
    )

    if supported:

        file_type = SUPPORTED_EXTENSIONS[
            extension
        ]

    else:

        file_type = "UNKNOWN"

    return {
        "file_name": file_name,
        "file_path": file_path,
        "extension": extension,
        "file_type": file_type,
        "size_bytes": size_bytes,
        "supported": supported,
        "page_count": None,
    }


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Document Inspector OK"
    )