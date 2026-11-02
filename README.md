# CV Analyzer Pakistan

A Windows desktop tool for Pakistani recruiters to process batches of CVs and resumes. It extracts contact and career information, classifies skills and experience, and organizes the results for recruiter review.

The analyzer supports PDF and DOCX files. Scanned PDFs can be processed with the bundled Tesseract OCR engine. It helps with information extraction and organization; it does **not** rank candidates or make hiring decisions. Extracted information and classifications may be incomplete or incorrect, so review them before use.

## Download

Download the latest **CV-Analyzer-portable-windows-x64.zip** from the [latest release](../../releases/latest).

This is a portable Windows x64 application; no installer is required.

## Quick start

Follow these steps to run your first batch:

### 1. 📥 Download and extract

Download `CV-Analyzer-portable-windows-x64.zip` from the [latest release](../../releases/latest), then extract it to a folder you can access.

> [!IMPORTANT]
> Extract the ZIP before starting the app. Do not run it from inside the compressed file.

### 2. 📂 Add CVs

Open the extracted `CV Analyzer` folder and copy the CVs you want to process into:

```text
CV Analyzer/
└── 01_INBOX/
```

For safety, add copies of your CVs so the originals remain untouched.

### 3. 🚀 Start the analyzer

Run **`START CV ANALYZER.bat`** from the `CV Analyzer` folder. Alternatively, open **`CV Analyzer.exe`** directly.

### 4. ⚙️ Check the folders

In the app, confirm the folder selections:

| App setting | Default folder | Used for |
|---|---|---|
| **CV inbox** | `01_INBOX` | CVs to process |
| **Reports** | `07_DATABASE` | Excel, CSV, vCard, and evidence files |
| **Logs** | `08_LOGS` | Processing logs |

You can select different folders in the app if needed.

### 5. 🔎 Analyze the batch

Select **Analyze CVs** and let processing finish. Scanned PDFs may take longer because they require OCR.

### 6. 📊 Review your reports

When the batch is complete, select **Open reports folder** to view the generated files. Check the review notes and verify extracted details against the original CVs.

> [!TIP]
> Keep the original CVs available during review. OCR and automated extraction can miss or misread information.

## Output files

Each batch creates timestamped files in the selected reports folder:

- **Excel workbook (`.xlsx`)** — candidate records in a filterable worksheet, plus processing details and review notes.
- **CSV (`.csv`)** — candidate records for spreadsheets and database imports.
- **vCard (`.vcf`)** — extracted names, email addresses, and phone numbers for contact apps.
- **Evidence JSON (`_evidence.json`)** — per-document processing metadata, review reasons, and errors where applicable. This is not a full JSON export of the candidate table.

Fields that cannot be confidently extracted may be blank or marked for review. The vCard includes only contact details that were extracted.

## Privacy and responsible use

CVs and the generated reports contain personal information. Store them securely, limit access to people who need it, and follow your organization's data-retention and privacy requirements. Verify extracted details with the original CV before contacting candidates or sharing records.

## Credits

Created with assistance from free versions of ChatGPT, Claude, Copilot, and Gemini, and with support from my employer and my family.
