
import os
import subprocess
import sys
import tempfile
from pathlib import Path

if __package__:
    from .app_paths import tessdata_directory, tesseract_executable
else:
    from app_paths import tessdata_directory, tesseract_executable


if getattr(sys, "frozen", False):
    bundled_tessdata = tessdata_directory()
    if bundled_tessdata:
        os.environ["TESSDATA_PREFIX"] = str(bundled_tessdata)


def _ocr_page(page, page_number):
    executable = tesseract_executable()
    if executable is None:
        raise FileNotFoundError(
            "Tesseract was not found. Install Tesseract or include it "
            "with the portable application."
        )

    bitmap = page.render(scale=300 / 72)
    try:
        with tempfile.TemporaryDirectory(prefix="cv_analyzer_ocr_") as folder:
            image_path = Path(folder) / f"page_{page_number}.png"
            bitmap.to_pil().save(image_path)
            tessdata = tessdata_directory()
            recognized_text = ""
            for page_segmentation_mode in ("3", "11"):
                command = [
                    str(executable),
                    str(image_path),
                    "stdout",
                    "-l",
                    "eng",
                    "--psm",
                    page_segmentation_mode,
                ]
                if tessdata:
                    command.extend(["--tessdata-dir", str(tessdata)])
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode:
                    raise RuntimeError(
                        f"Tesseract OCR failed on PDF page {page_number}: "
                        f"{result.stderr.strip() or 'No error details were returned.'}"
                    )
                if len("".join(result.stdout.split())) > len(
                    "".join(recognized_text.split())
                ):
                    recognized_text = result.stdout
                if len("".join(recognized_text.split())) >= 30:
                    break
    finally:
        bitmap.close()

    return recognized_text


def extract_pdf_text(file_path, use_ocr=False):
    """
    Extract text from a PDF.

    Returns:
        {
            "text": "...",
            "pages": [...],
            "page_count": int,
            "has_text": bool
        }
    """

    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(file_path))
    try:
        pages = []
        all_text = []

        for page_number in range(1, len(doc) + 1):
            page = doc[page_number - 1]
            try:
                if use_ocr:
                    text = _ocr_page(page, page_number)
                else:
                    text_page = page.get_textpage()
                    try:
                        text = text_page.get_text_range()
                    finally:
                        text_page.close()
            finally:
                page.close()

            pages.append({"page": page_number, "text": text})
            all_text.append(text)

        page_count = len(doc)
        full_text = "\n".join(all_text)

    finally:
        doc.close()

    # Require a minimum amount of actual text before skipping OCR.
    # This helps identify scanned PDFs and PDFs with only a few characters.
    usable_text = len("".join(full_text.split())) >= 30

    return {
        "text": full_text,
        "pages": pages,
        "page_count": page_count,
        "has_text": usable_text
    }
