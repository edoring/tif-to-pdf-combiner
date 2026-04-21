# TIFF to Single PDF Combiner

A lightweight Python script for combining large batches of numbered TIFF files into a single PDF, with built-in validation, logging, and progress tracking.

---

## ✨ Features

* Combines hundreds of `.tif` / `.tiff` files into one PDF
* Preserves order using `_###` filename pattern
* Detects missing sequence numbers
* Progress bar for long-running jobs
* Generates:

  * log file
  * manifest file (exact file list in order)
* Automatically fixes missing `.pdf` extension in output

---

## 📁 Expected Filename Format

Files should end with a sequence number:

```
document_001.tif
document_002.tif
...
```

---

## 🚀 Installation

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python combine_tifs_to_pdf.py
```

You will be prompted for:

* Input folder containing TIFF files
* Output PDF path

---

## 📊 Output Files

* `combined.pdf` → final PDF
* `combined.log.txt` → full processing log
* `combined.manifest.txt` → ordered file list

---

## 🔍 Validation

The script checks:

* Sequence range (e.g. 001–542)
* Missing numbers within range
* Total files processed vs expected

---

## 🏛️ Use Case

Designed for digital archives and large-scale digitization workflows where:

* TIFFs are preservation masters
* PDFs are access copies
* File order must be preserved and verifiable

---

## ⚠️ Notes

* Each TIFF is assumed to be single-page
* Large batches may produce very large PDFs

---

## 💡 Future Improvements

* Option to stop if sequence gaps are detected
* GUI wrapper for non-technical users
* Metadata embedding into PDF

## 🧠 Workflow Philosophy

This script is designed to support archival best practices:

- Preservation files remain untouched (TIFF)
- Access copies are generated separately (PDF)
- File integrity is verified through sequence validation
- Outputs include documentation for audit and reproducibility
