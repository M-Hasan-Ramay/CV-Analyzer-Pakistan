from docx import Document


def extract_docx_text(file_path):
    """
    Extract text from a DOCX file, including paragraphs and tables.
    """

    doc = Document(file_path)

    paragraphs = []
    tables = []

    # Extract normal paragraphs
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    # Extract tables
    for table in doc.tables:

        for row in table.rows:

            cells = []

            for cell in row.cells:
                cell_text = cell.text.strip()

                if cell_text:
                    cells.append(cell_text)

            if cells:
                tables.append(" | ".join(cells))

    # Combine everything
    all_text = paragraphs + tables

    return {
        "text": "\n".join(all_text),
        "paragraphs": paragraphs,
        "tables": tables
    }