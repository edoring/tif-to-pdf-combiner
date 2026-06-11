from pathlib import Path
import re
import sys
import traceback
from datetime import datetime


def pause_before_exit():
    input("\nPress Enter to close...")


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message, log_lines):
    log_lines.append(f"[{timestamp()}] {message}")


def extract_sequence_number(filename):
    """
    Finds the final number in the filename before the extension.

    Works with:
    KIC Image 0001.tif
    KIC Image 0002.tiff
    Petition for Referendum_0001.tif
    scan-0001.tif
    page0001.tif
    0001.tif
    """
    stem = Path(filename).stem
    matches = re.findall(r"\d+", stem)

    if matches:
        return int(matches[-1])

    return None


def main():
    print("\nTIF to Single PDF Combiner")
    print("-" * 30)

    try:
        from PIL import Image
    except ModuleNotFoundError:
        print("\nERROR: Pillow is not installed.")
        print("Run this in PowerShell:")
        print("python -m pip install pillow")
        pause_before_exit()
        sys.exit(1)

    try:
        from tqdm import tqdm
    except ModuleNotFoundError:
        print("\nERROR: tqdm is not installed.")
        print("Run this in PowerShell:")
        print("python -m pip install tqdm")
        pause_before_exit()
        sys.exit(1)

    input_folder = Path(input("\nInput folder with TIFs: ").strip().strip('"'))
    output_pdf = Path(input("Output PDF path: ").strip().strip('"'))

    if output_pdf.suffix.lower() != ".pdf":
        output_pdf = output_pdf.with_suffix(".pdf")

    if not input_folder.exists():
        print("\nERROR: Input folder does not exist.")
        print(f"You entered: {input_folder}")
        pause_before_exit()
        sys.exit(1)

    if not input_folder.is_dir():
        print("\nERROR: Input path is not a folder.")
        print(f"You entered: {input_folder}")
        pause_before_exit()
        sys.exit(1)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    log_file = output_pdf.with_suffix(".log.txt")
    manifest_file = output_pdf.with_suffix(".manifest.txt")
    log_lines = []

    print("\nScanning files...")

    files = [
        file for file in input_folder.iterdir()
        if file.is_file() and file.suffix.lower() in [".tif", ".tiff"]
    ]

    numbered_files = []
    skipped = []

    for file in files:
        seq = extract_sequence_number(file.name)

        if seq is None:
            skipped.append(file.name)
            log(f"Skipped non-numbered filename: {file.name}", log_lines)
        else:
            numbered_files.append((seq, file))

    numbered_files.sort(key=lambda x: x[0])

    if not numbered_files:
        print("\nERROR: No valid TIF files found.")
        print("This script needs filenames with some kind of number, like:")
        print("KIC Image 0001.tif")
        print("scan-0001.tif")
        print("page0001.tif")
        pause_before_exit()
        sys.exit(1)

    found_numbers = [seq for seq, _ in numbered_files]
    min_seq = min(found_numbers)
    max_seq = max(found_numbers)

    missing = sorted(set(range(min_seq, max_seq + 1)) - set(found_numbers))

    duplicate_numbers = sorted(
        number for number in set(found_numbers)
        if found_numbers.count(number) > 1
    )

    print("\nSummary")
    print("-" * 30)
    print(f"Found TIFs:         {len(files)}")
    print(f"Valid numbered:     {len(numbered_files)}")
    print(f"Sequence range:     {min_seq:04d}-{max_seq:04d}")
    print(f"Skipped filenames:  {len(skipped)}")
    print(f"Missing numbers:    {len(missing)}")
    print(f"Duplicate numbers:  {len(duplicate_numbers)}")

    if missing:
        preview = ", ".join(f"{n:04d}" for n in missing[:20])
        if len(missing) > 20:
            preview += ", ..."
        print(f"Missing preview:    {preview}")
        log("Missing numbers: " + ", ".join(f"{n:04d}" for n in missing), log_lines)
    else:
        print("Missing preview:    None")
        log("No missing numbers detected.", log_lines)

    if duplicate_numbers:
        preview = ", ".join(f"{n:04d}" for n in duplicate_numbers[:20])
        if len(duplicate_numbers) > 20:
            preview += ", ..."
        print(f"Duplicate preview:  {preview}")
        log("Duplicate numbers: " + ", ".join(f"{n:04d}" for n in duplicate_numbers), log_lines)

        print("\nWARNING: Duplicate sequence numbers were found.")
        print("The PDF can still be created, but you may want to check these first.")

    with manifest_file.open("w", encoding="utf-8") as f:
        f.write("sequence_number\tfilename\n")
        for seq, path in numbered_files:
            f.write(f"{seq:04d}\t{path.name}\n")

    pdf_images = []

    print("\nPreparing PDF...")

    for seq, path in tqdm(numbered_files, desc="Checking files", unit="file", ncols=90):
        try:
            image = Image.open(path)

            # If the TIF has multiple frames/pages, use the first frame.
            image.seek(0)

            # PDF output needs RGB images.
            if image.mode != "RGB":
                image = image.convert("RGB")

            pdf_images.append(image.copy())
            image.close()

            log(f"Included {seq:04d}: {path.name}", log_lines)

        except Exception as e:
            skipped.append(path.name)
            log(f"ERROR reading {path.name}: {e}", log_lines)
            print(f"\nWARNING: Could not read {path.name}. It will be skipped.")

    if not pdf_images:
        print("\nERROR: No readable TIF files could be added to the PDF.")
        Path(log_file).write_text("\n".join(log_lines), encoding="utf-8")
        pause_before_exit()
        sys.exit(1)

    print("\nWriting PDF...")

    first_image = pdf_images[0]
    remaining_images = pdf_images[1:]

    first_image.save(
        output_pdf,
        "PDF",
        resolution=300.0,
        save_all=True,
        append_images=remaining_images
    )

    log(f"Output PDF written to: {output_pdf}", log_lines)
    log(f"Total TIFs included: {len(pdf_images)}", log_lines)

    Path(log_file).write_text("\n".join(log_lines), encoding="utf-8")

    print("\nResults")
    print("-" * 30)
    print(f"TIFs included:      {len(pdf_images)}")
    print(f"Output PDF:         {output_pdf}")
    print(f"Log file:           {log_file}")
    print(f"Manifest file:      {manifest_file}")
    print("Status:             OK")
    print("\nDone.")

    pause_before_exit()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\nUNEXPECTED ERROR")
        print("-" * 30)
        traceback.print_exc()
        pause_before_exit()
        sys.exit(1)
