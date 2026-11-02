"""Resolve user data and bundled resource locations for source and frozen runs."""

import sys
import shutil
from pathlib import Path


def project_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def bundled_directory():
    return Path(getattr(sys, "_MEIPASS", project_directory()))


def config_file(filename):
    external_path = project_directory() / "09_CONFIG" / filename
    if external_path.is_file():
        return external_path
    return bundled_directory() / "09_CONFIG" / filename


def tessdata_directory():
    candidates = (
        project_directory() / "tesseract" / "tessdata",
        bundled_directory() / "tesseract" / "tessdata",
        project_directory() / "tessdata",
        bundled_directory() / "tessdata",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    executable = shutil.which("tesseract")
    if executable:
        candidate = Path(executable).resolve().parent / "tessdata"
        if candidate.is_dir():
            return candidate
    return None


def tesseract_executable():
    if getattr(sys, "frozen", False):
        bundled = project_directory() / "tesseract" / "tesseract.exe"
        if bundled.is_file():
            return bundled
    discovered = shutil.which("tesseract")
    return Path(discovered) if discovered else None
