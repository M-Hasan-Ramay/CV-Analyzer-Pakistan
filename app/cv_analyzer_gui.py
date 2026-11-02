"""Desktop interface for processing batches of CVs."""

import queue
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

if __package__:
    from .app_paths import tessdata_directory, tesseract_executable
    from .cv_analyzer import INBOX_DIR, LOG_DIR, OUTPUT_DIR, process_batch
else:
    from app_paths import tessdata_directory, tesseract_executable
    from cv_analyzer import INBOX_DIR, LOG_DIR, OUTPUT_DIR, process_batch


def summarize_records(records):
    """Return batch totals and a row for each processed document."""
    successful = sum(
        record.get("evidence", {}).get("processing_result") == "SUCCESS"
        for record in records
    )
    errors = len(records) - successful
    needs_review = sum(
        record.get("public", {}).get("Status") == "Needs review"
        for record in records
    )
    rows = []
    for record in records:
        evidence = record.get("evidence", {})
        public = record.get("public", {})
        error = evidence.get("error_message", "")
        reasons = "; ".join(evidence.get("review_reasons", []))
        rows.append(
            (
                evidence.get("source_filename", ""),
                evidence.get("processing_result", "ERROR"),
                public.get("Candidate", ""),
                public.get("Status", ""),
                error or reasons,
            )
        )
    return successful, errors, needs_review, rows


class CVAnalyzerApp:
    """Tkinter front end for the existing batch-processing engine."""

    def __init__(self, root):
        self.root = root
        self.root.title("CV Analyzer")
        self.root.geometry("1020x720")
        self.root.minsize(820, 580)
        self.events = queue.Queue()
        self.is_processing = False

        self.inbox_var = tk.StringVar(value=str(INBOX_DIR))
        self.output_var = tk.StringVar(value=str(OUTPUT_DIR))
        self.logs_var = tk.StringVar(value=str(LOG_DIR))
        self.status_var = tk.StringVar(
            value="Choose your CV inbox folder, then start processing."
        )
        self.summary_var = tk.StringVar(value="No batch has been run yet.")
        self.report_paths = {}

        self._build_ui()
        self.root.after(100, self._poll_events)

    def _build_ui(self):
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Run.TButton", font=("Segoe UI", 11, "bold"), padding=8)

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ttk.Label(header, text="CV Analyzer", style="Title.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            header,
            text="Extract, classify, and organize CVs into reviewable reports.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        folders = ttk.LabelFrame(
            container,
            text="Folders",
            padding=12,
            style="Section.TLabelframe",
        )
        folders.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        folders.columnconfigure(1, weight=1)
        self._add_folder_row(folders, 0, "CV inbox", self.inbox_var)
        self._add_folder_row(folders, 1, "Reports", self.output_var)
        self._add_folder_row(folders, 2, "Logs", self.logs_var)

        controls = ttk.Frame(container)
        controls.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.run_button = ttk.Button(
            controls,
            text="Analyze CVs",
            style="Run.TButton",
            command=self.start_processing,
        )
        self.run_button.pack(side="left")
        self.open_reports_button = ttk.Button(
            controls,
            text="Open reports folder",
            command=lambda: self._open_path(self.output_var.get()),
        )
        self.open_reports_button.pack(side="left", padx=(8, 0))
        ttk.Label(
            controls,
            textvariable=self.status_var,
            wraplength=560,
        ).pack(side="left", fill="x", expand=True, padx=(14, 0))

        self.progress = ttk.Progressbar(
            container,
            mode="determinate",
            maximum=100,
        )
        self.progress.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        results = ttk.LabelFrame(
            container,
            text="Batch results",
            padding=10,
            style="Section.TLabelframe",
        )
        results.grid(row=4, column=0, sticky="nsew")
        results.columnconfigure(0, weight=1)
        results.rowconfigure(1, weight=1)
        ttk.Label(results, textvariable=self.summary_var).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8),
        )

        table_frame = ttk.Frame(results)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("file", "result", "candidate", "review", "details")
        self.results_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        headings = {
            "file": ("CV file", 220),
            "result": ("Processing", 100),
            "candidate": ("Candidate", 160),
            "review": ("Record status", 120),
            "details": ("Review notes / error", 320),
        }
        for column, (heading, width) in headings.items():
            self.results_table.heading(column, text=heading)
            self.results_table.column(column, width=width, minwidth=80)
        self.results_table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.results_table.yview,
        )
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.results_table.xview,
        )
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        self.results_table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )

        report_actions = ttk.Frame(results)
        report_actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.open_excel_button = ttk.Button(
            report_actions,
            text="Open Excel report",
            command=lambda: self._open_report("workbook_path"),
            state="disabled",
        )
        self.open_excel_button.pack(side="left")
        self.open_csv_button = ttk.Button(
            report_actions,
            text="Open CSV report",
            command=lambda: self._open_report("csv_path"),
            state="disabled",
        )
        self.open_csv_button.pack(side="left", padx=(8, 0))

    @staticmethod
    def _add_folder_row(parent, row, label, variable):
        ttk.Label(parent, text=label).grid(
            row=row,
            column=0,
            sticky="w",
            padx=(0, 10),
            pady=4,
        )
        ttk.Entry(parent, textvariable=variable).grid(
            row=row,
            column=1,
            sticky="ew",
            pady=4,
        )
        ttk.Button(
            parent,
            text="Browse...",
            command=lambda: CVAnalyzerApp._choose_folder(variable),
        ).grid(row=row, column=2, padx=(8, 0), pady=4)

    @staticmethod
    def _choose_folder(variable):
        selected = filedialog.askdirectory(
            title="Select folder",
            initialdir=variable.get() or str(Path.home()),
        )
        if selected:
            variable.set(selected)

    def start_processing(self):
        if self.is_processing:
            return
        inbox = Path(self.inbox_var.get()).expanduser()
        if not inbox.is_dir():
            messagebox.showerror(
                "Inbox not found",
                f"The selected inbox folder does not exist:\n{inbox}",
                parent=self.root,
            )
            return

        self._clear_results()
        self.is_processing = True
        self.run_button.configure(state="disabled")
        self.progress.configure(value=0, maximum=100)
        self.status_var.set("Preparing CV batch...")
        self.summary_var.set("Processing. Reports will appear when complete.")
        thread = threading.Thread(
            target=self._process_in_background,
            args=(inbox, Path(self.output_var.get()), Path(self.logs_var.get())),
            daemon=True,
        )
        thread.start()

    def _process_in_background(self, inbox, output, logs):
        def report_progress(index, total, filename, status):
            self.events.put(("progress", index, total, filename, status))

        try:
            result = process_batch(
                inbox_dir=inbox,
                output_dir=output,
                log_dir=logs,
                progress_callback=report_progress,
            )
        except Exception as exc:
            self.events.put(("failed", f"{type(exc).__name__}: {exc}"))
            return
        self.events.put(("completed", result))

    def _poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    _, index, total, filename, status = event
                    self.progress.configure(maximum=total, value=index)
                    self.status_var.set(
                        f"{index}/{total} - {filename} - {status}"
                    )
                elif event[0] == "failed":
                    self._finish_with_error(event[1])
                elif event[0] == "completed":
                    self._finish_batch(event[1])
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _finish_batch(self, result):
        self.is_processing = False
        self.run_button.configure(state="normal")
        if not result:
            self.status_var.set("No PDF or DOCX files found in the selected inbox.")
            self.summary_var.set("Nothing was processed; no report was created.")
            self.progress.configure(value=0)
            return

        records = result["records"]
        successful, errors, needs_review, rows = summarize_records(records)
        self.summary_var.set(
            f"Files: {len(records)}    Processed: {successful}    "
            f"Errors: {errors}    Needs review: {needs_review}"
        )
        for row in rows:
            self.results_table.insert("", "end", values=row)

        self.report_paths = result
        self.open_excel_button.configure(state="normal")
        self.open_csv_button.configure(state="normal")
        self.status_var.set(
            f"Batch complete. Reports saved to {result['workbook_path'].parent}"
        )

    def _finish_with_error(self, details):
        self.is_processing = False
        self.run_button.configure(state="normal")
        self.status_var.set("Batch processing could not be completed.")
        self.summary_var.set(details)
        messagebox.showerror(
            "CV analysis failed",
            details,
            parent=self.root,
        )

    def _clear_results(self):
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        self.report_paths = {}
        self.open_excel_button.configure(state="disabled")
        self.open_csv_button.configure(state="disabled")

    def _open_report(self, key):
        path = self.report_paths.get(key)
        if path:
            self._open_path(path)

    def _open_path(self, path):
        target = Path(path).expanduser()
        if not target.exists():
            messagebox.showerror(
                "Path not found",
                f"The selected path does not exist:\n{target}",
                parent=self.root,
            )
            return
        try:
            import os

            os.startfile(str(target))
        except OSError as exc:
            messagebox.showerror(
                "Could not open path",
                f"{type(exc).__name__}: {exc}",
                parent=self.root,
            )


def main():
    if sys.argv[1:] == ["--self-test"]:
        return run_self_test()
    root = tk.Tk()
    CVAnalyzerApp(root)
    root.mainloop()
    return 0


def run_self_test():
    """Verify bundled settings, PDFium rendering, and English Tesseract OCR."""
    if __package__:
        from . import certification_extractor, classification_engine
        from . import technology_extractor
    else:
        import certification_extractor
        import classification_engine
        import technology_extractor

    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw, ImageFont

    if not classification_engine.RULES:
        raise RuntimeError("Classification rules did not load.")
    if not technology_extractor.TECHNOLOGY_CATALOG:
        raise RuntimeError("Technology catalog did not load.")
    if not certification_extractor.CERTIFICATION_CATALOG:
        raise RuntimeError("Certification catalog did not load.")

    document = pdfium.PdfDocument.new()
    try:
        page = document.new_page(width=100, height=100)
        bitmap = page.render(scale=1)
        bitmap.close()
        page.close()
    finally:
        document.close()

    executable = tesseract_executable()
    tessdata = tessdata_directory()
    if executable is None or tessdata is None:
        raise RuntimeError("Bundled Tesseract or its language data is missing.")
    if not (tessdata / "eng.traineddata").is_file():
        raise RuntimeError("The English Tesseract language data is missing.")

    with tempfile.TemporaryDirectory(prefix="cv_analyzer_self_test_") as folder:
        image_path = Path(folder) / "ocr_test.png"
        image = Image.new("RGB", (900, 160), "white")
        draw = ImageDraw.Draw(image)
        draw.text(
            (30, 45),
            "CV ANALYZER READY",
            font=ImageFont.load_default(size=60),
            fill="black",
        )
        image.save(image_path)
        result = subprocess.run(
            [
                str(executable),
                str(image_path),
                "stdout",
                "-l",
                "eng",
                "--psm",
                "6",
                "--tessdata-dir",
                str(tessdata),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode or "READY" not in result.stdout.upper():
        raise RuntimeError(
            "Bundled Tesseract OCR self-test failed: "
            f"{result.stderr.strip() or 'Expected OCR text was not recognized.'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
