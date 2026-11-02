"""Build a self-contained Windows x64 portable ZIP for CV Analyzer."""

import os
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from zipfile import ZipFile

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
APP_DIR = DIST_DIR / "CV Analyzer"
ZIP_PATH = DIST_DIR / "CV-Analyzer-portable-windows-x64.zip"
PDFIUM2_VERSION = "5.14.0"


def _copy_python_licenses(destination):
    pypdfium_version = metadata.version("pypdfium2")
    if pypdfium_version != PDFIUM2_VERSION:
        raise RuntimeError(
            f"pypdfium2 {PDFIUM2_VERSION} is required for this release build; "
            f"found {pypdfium_version}."
        )

    roots = {"pypdfium2", "pillow", "openpyxl", "python-docx"}
    pending = list(roots)
    included = set()

    while pending:
        name = canonicalize_name(pending.pop())
        if name in included:
            continue
        included.add(name)
        try:
            distribution = metadata.distribution(name)
        except metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"Required package is not installed in the build environment: {name}"
            ) from exc

        for requirement_text in distribution.requires or []:
            requirement = Requirement(requirement_text)
            if requirement.marker is None or requirement.marker.evaluate():
                dependency = canonicalize_name(requirement.name)
                if dependency not in included:
                    pending.append(dependency)

        for item in distribution.files or []:
            relative = Path(str(item))
            license_index = next(
                (
                    index
                    for index, part in enumerate(relative.parts)
                    if "license" in part.casefold()
                    or "licence" in part.casefold()
                    or "copying" in part.casefold()
                ),
                None,
            )
            if license_index is None:
                continue
            source = Path(distribution.locate_file(item))
            if source.is_file():
                license_relative = Path(*relative.parts[license_index + 1 :])
                target = destination / name / license_relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


def _copy_python_runtime_licenses(destination):
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise RuntimeError(
            f"Python runtime license was not found: {python_license}"
        )
    shutil.copy2(python_license, destination / "CPython-LICENSE.txt")

    tcl_directory = Path(sys.base_prefix) / "tcl"
    tcl_licenses = destination / "Tcl-Tk"
    tcl_licenses.mkdir(parents=True, exist_ok=True)
    copied = 0
    for archive_name, prefix in (
        ("libtcl*.zip", "Tcl"),
        ("libtk*.zip", "Tk"),
    ):
        for archive in tcl_directory.glob(archive_name):
            with ZipFile(archive) as source:
                for member in source.namelist():
                    if Path(member).name.casefold() != "license.terms":
                        continue
                    target = tcl_licenses / f"{prefix}-license.terms"
                    target.write_bytes(source.read(member))
                    copied += 1
    if copied != 2:
        raise RuntimeError(
            "Could not locate both Tcl and Tk license terms in the Python "
            "runtime."
        )


def _copy_pyinstaller_license(destination):
    distribution = metadata.distribution("pyinstaller")
    for item in distribution.files or []:
        if Path(str(item)).name.casefold() == "copying.txt":
            source = Path(distribution.locate_file(item))
            shutil.copy2(source, destination / "PyInstaller-COPYING.txt")
            return
    raise RuntimeError("Could not locate PyInstaller's bootloader license.")


def _copy_tesseract(app_directory, licenses_directory):
    executable = shutil.which("tesseract")
    if not executable:
        raise RuntimeError(
            "Tesseract was not found on PATH. Install Tesseract OCR "
            "before building the portable release."
        )

    source_directory = Path(executable).resolve().parent
    tessdata_source = source_directory / "tessdata"
    if not (tessdata_source / "eng.traineddata").is_file():
        raise RuntimeError(
            f"English Tesseract data was not found in {tessdata_source}."
        )

    target_directory = app_directory / "tesseract"
    target_directory.mkdir(parents=True, exist_ok=True)
    shutil.copy2(executable, target_directory / "tesseract.exe")
    for library in source_directory.glob("*.dll"):
        shutil.copy2(library, target_directory / library.name)
    shutil.copytree(tessdata_source, target_directory / "tessdata")

    documentation = source_directory / "doc"
    if documentation.is_dir():
        shutil.copytree(
            documentation,
            licenses_directory / "Tesseract-OCR",
        )


def _write_notices(app_directory):
    versions = {
        name: metadata.version(name)
        for name in ("pypdfium2", "Pillow", "openpyxl", "python-docx")
    }
    lines = [
        "CV Analyzer - third-party notices",
        "",
        "This portable distribution contains open-source software. "
        "The applicable license texts are in the licenses directory.",
        "",
        "PDFium / pypdfium2",
        f"- pypdfium2 version: {versions['pypdfium2']}",
        "- pypdfium2: Apache-2.0 and BSD-3-Clause.",
        "- PDFium and bundled Windows dependency notices are under "
        "licenses/Python/pypdfium2.",
        "- Source: https://github.com/pypdfium2-team/pypdfium2",
        "",
        "Tesseract OCR",
        "- Tesseract and its installation documentation are included under "
        "licenses/Tesseract-OCR.",
        "- Source: https://github.com/tesseract-ocr/tesseract",
        "",
        "Python and desktop runtime",
        "- CPython, Tcl, and Tk license texts are in licenses and "
        "licenses/Tcl-Tk.",
        "- PyInstaller bootloader license and exception are in "
        "licenses/PyInstaller-COPYING.txt.",
        "",
        "Python dependencies",
    ]
    for name, version in versions.items():
        lines.append(f"- {name} {version}; see licenses/Python for notices.")
    lines.extend(
        [
            "- PyInstaller bootloader is distributed under GPL-2.0-or-later "
            "with its bootloader exception.",
            "- PyInstaller source: https://github.com/pyinstaller/pyinstaller",
            "",
            "Include this file and the licenses directory with any copy "
            "of this portable application.",
        ]
    )
    (app_directory / "THIRD_PARTY_NOTICES.txt").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def build():
    if os.name != "nt":
        raise RuntimeError("Build this portable package on Windows.")
    if sys.maxsize <= 2**32:
        raise RuntimeError("A 64-bit Python interpreter is required.")
    if APP_DIR.exists() or ZIP_PATH.exists():
        raise FileExistsError(
            f"Build output already exists. Move it out of the way first: "
            f"{APP_DIR if APP_DIR.exists() else ZIP_PATH}"
        )

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(ROOT / "build" / "pyinstaller"),
            str(ROOT / "cv_analyzer.spec"),
        ],
        cwd=ROOT,
        check=True,
    )

    if not (APP_DIR / "CV Analyzer.exe").is_file():
        raise RuntimeError("PyInstaller did not produce CV Analyzer.exe.")

    licenses_directory = APP_DIR / "licenses"
    licenses_directory.mkdir()
    (licenses_directory / "Python").mkdir()
    _copy_python_licenses(licenses_directory / "Python")
    _copy_python_runtime_licenses(licenses_directory)
    _copy_pyinstaller_license(licenses_directory)
    _copy_tesseract(APP_DIR, licenses_directory)

    shutil.copytree(ROOT / "09_CONFIG", APP_DIR / "09_CONFIG")
    for folder in ("01_INBOX", "07_DATABASE", "08_LOGS"):
        (APP_DIR / folder).mkdir()
    shutil.copy2(
        ROOT / "START CV ANALYZER.bat",
        APP_DIR / "START CV ANALYZER.bat",
    )
    shutil.copy2(
        ROOT / "PORTABLE_README.txt",
        APP_DIR / "PORTABLE_README.txt",
    )
    _write_notices(APP_DIR)
    required_pdfium_licenses = (
        licenses_directory / "Python" / "pypdfium2" / "LICENSES"
    )
    if not (
        (required_pdfium_licenses / "Apache-2.0.txt").is_file()
        and (required_pdfium_licenses / "BSD-3-Clause.txt").is_file()
        and (
            licenses_directory
            / "Python"
            / "pypdfium2"
            / "data"
            / "windows_x64"
            / "BUILD_LICENSES"
            / "pdfium.txt"
        ).is_file()
    ):
        raise RuntimeError(
            "The Windows PDFium binary license set was not fully packaged."
        )

    archive_path = shutil.make_archive(
        str(ZIP_PATH.with_suffix("")),
        "zip",
        root_dir=DIST_DIR,
        base_dir=APP_DIR.name,
    )
    print(f"Portable application folder: {APP_DIR}")
    print(f"Portable ZIP: {archive_path}")
    print("The package contains no inbox CVs or generated candidate records.")


if __name__ == "__main__":
    build()
