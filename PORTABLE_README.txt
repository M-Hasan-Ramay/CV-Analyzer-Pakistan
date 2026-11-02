CV Analyzer - portable Windows release

QUICK START
1. Extract the complete "CV Analyzer" folder from the ZIP.
2. Put PDF and DOCX resumes in the 01_INBOX folder.
3. Double-click START CV ANALYZER.bat.
4. Choose folders in the app if you do not want the default locations.
5. Reports are written to 07_DATABASE; processing logs go to 08_LOGS.

The portable application includes its Python runtime, PDFium PDF engine,
English Tesseract OCR, and editable classification catalogs. Python and an
internet connection are not required on the destination Windows PC.

The original CV files are read, not modified. Processing is local; CV
documents are not uploaded by the analyzer.

FOLDER CONTENTS
- CV Analyzer.exe: desktop application
- 01_INBOX: default CV input folder
- 07_DATABASE: Excel, CSV, evidence JSON, and vCard exports
- 08_LOGS: processing logs
- 09_CONFIG: editable classification, technology, and certification catalogs
- tesseract: bundled OCR engine and English language data
- licenses: third-party license texts and notices
- START CV ANALYZER.bat: convenient launcher

NOTES
- Keep the complete application folder together after extraction.
- Run the app from a writable folder; avoid protected folders such as
  Program Files unless you have the required permissions.
- If Windows SmartScreen warns about an unsigned application, verify the
  ZIP source before allowing it to run.
- Classification is evidence-based and intended to organize CVs. It is not
  an automated candidate ranking or verification of credential validity.
- Review generated records and evidence, especially OCR output, before use.

For third-party attribution and license details, see THIRD_PARTY_NOTICES.txt
and the licenses folder.
