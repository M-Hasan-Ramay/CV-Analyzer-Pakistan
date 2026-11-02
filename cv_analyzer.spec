from pathlib import Path

from PyInstaller.utils.hooks import collect_all


ROOT = Path(SPECPATH)
pdfium_datas, pdfium_binaries, pdfium_hiddenimports = collect_all("pypdfium2")

a = Analysis(
    [str(ROOT / "app" / "cv_analyzer_gui.py")],
    pathex=[str(ROOT / "app")],
    binaries=pdfium_binaries,
    datas=pdfium_datas,
    hiddenimports=pdfium_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pymupdf", "fitz", "pytesseract"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CV Analyzer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="CV Analyzer",
)
