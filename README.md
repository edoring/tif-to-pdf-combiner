# 📄 TIF to Single PDF Combiner

A Python script for combining sequential TIF or TIFF images into a single PDF.

This tool is designed for archival, digitization, scanning, preservation, and researcher access workflows where individual image files need to be combined into one readable PDF.

---

## ✨ Features

* Combines TIF/TIFF files into one PDF
* Supports `.tif` and `.tiff` files
* Sorts files by the final number in each filename
* Works with different filename styles, including:

  * `KIC Image 0001.tif`
  * `KIC Image 0002.tif`
  * `scan-0001.tiff`
  * `page0001.tif`
  * `Petition for Referendum_0001.tif`
  * `0001.tif`

* Checks for missing sequence numbers
* Warns about duplicate sequence numbers
* Creates a manifest listing the image order used in the PDF
* Creates a log file documenting included, skipped, missing, duplicate, and unreadable files
* Does **not** move, rename, delete, or alter the original TIF files
* Pauses before closing so errors can be read

---

## 🧰 Requirements

* Windows computer
* Python
* PowerShell or Command Prompt
* TIF/TIFF files stored in one folder
* Permission to write to the selected output location

This script also requires the following Python packages:

```powershell
python -m pip install pillow tqdm
