from pathlib import Path
from PIL import Image
from tqdm import tqdm
import re
import sys
from datetime import datetime


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message: str, log_lines: list[str], also_print: bool = False) -> None:
    line = f"[{timestamp()}] {message}"
    log_lines.append(line)
    if also_print:
        print(message)


def extract_sequence_number(filename: str) -> int | None:
    """
    Extract trailing sequence number from filenames like:
    file_001.tif
    boxfolder_127.tiff
    """
    match = re.search(r"_(\d+)\.(tif|tiff)$", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def find_tif_files(folder: Path) -> list[Path]:
    return list(folder.glob("*.tif")) + list(folder.glob("*.tiff"))


def validate_and_sort_files(files: list[Path], log_lines: list[str]) -> tuple[list[tuple[int, Path]], list[str]]:
    numbered_files = []
    skipped_files = []

    for file in files:
        seq = extract_sequence_number(file.name)
        if seq is None:
            skipped_files.append(file.name)
            log(f"Skipped non-matching filename: {file.name}", log_lines)
        else:
            numbered_files.append((seq, file))

    numbered_files.sort(key=lambda x: x[0])
    return numbered_files, skipped_files


def write_manifest(manifest_path: Path, numbered_files: list[tuple[int, Path]]) -> None:
    with manifest_path.open("w", encoding="utf-8") as f:
        f.write("sequence_number\tfilename\n")
        for seq, path in numbered_files:
            f.write(f"{seq:03d}\t{path.name}\n")


def check_sequence(numbered_files: list[tuple[int, Path]]) -> tuple[int, int, list[int]]:
    found_numbers = [seq for seq, _ in numbered_files]
    min_seq = min(found_numbers)
    max_seq = max(found_numbers)

    expected_numbers = set(range(min_seq, max_seq + 1))
    actual_numbers = set(found_numbers)
    missing_numbers = sorted(expected_numbers - actual_numbers)

    return min_seq, max_seq, missing_numbers


def build_pdf(numbered_files: list[tuple[int, Path]], output_pdf: Path, log_lines: list[str]) -> int:
    images = []

    for seq, file_path in tqdm(
        numbered_files,
        desc="Building PDF",
        unit="file",
        ncols=90,
        colour="green"
    ):
        try:
            with Image.open(file_path) as img:
                rgb_img = img.convert("RGB")
                images.append(rgb_img.copy())
                log(f"Included {seq:03d}: {file_path.name}", log_lines)
        except Exception as e:
            log(f"ERROR processing {file_path.name}: {e}", log_lines)

    if not images:
        return 0

    first_image, remaining_images = images[0], images[1:]

    # Explicitly tell Pillow the format is PDF
    first_image.save(
        output_pdf,
        format="PDF",
        save_all=True,
        append_images=remaining_images
    )

    return len(images)


def main() -> None:
    print("\nTIFF to Single PDF Combiner")
    print("-" * 30)

    input_folder_str = input("Input folder with TIFFs: ").strip().strip('"')
    output_pdf_str = input("Output PDF path: ").strip().strip('"')

    input_folder = Path(input_folder_str)
    output_pdf = Path(output_pdf_str)

    # Auto-add .pdf if omitted
    if output_pdf.suffix.lower() != ".pdf":
        output_pdf = output_pdf.with_suffix(".pdf")

    if not input_folder.exists() or not input_folder.is_dir():
        print("\nInput folder does not exist or is not a folder.")
        sys.exit(1)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    log_file = output_pdf.with_suffix(".log.txt")
    manifest_file = output_pdf.with_suffix(".manifest.txt")
    log_lines: list[str] = []

    print("\nScanning files...")

    raw_files = find_tif_files(input_folder)
    numbered_files, skipped_files = validate_and_sort_files(raw_files, log_lines)

    if not numbered_files:
        print("No valid TIFF files ending in _###.tif or _###.tiff were found.")
        Path(log_file).write_text("\n".join(log_lines), encoding="utf-8")
        sys.exit(1)

    min_seq, max_seq, missing_numbers = check_sequence(numbered_files)

    first_file = numbered_files[0][1].name
    last_file = numbered_files[-1][1].name
    actual_count = len(numbered_files)
    expected_count = (max_seq - min_seq) + 1

    print("\nSummary")
    print("-" * 30)
    print(f"Found TIFFs:       {len(raw_files)}")
    print(f"Valid numbered:    {actual_count}")
    print(f"Sequence range:    {min_seq:03d}-{max_seq:03d}")
    print(f"Expected in range: {expected_count}")
    print(f"First in order:    {first_file}")
    print(f"Last in order:     {last_file}")
    print(f"Skipped filenames: {len(skipped_files)}")
    print(f"Missing numbers:   {len(missing_numbers)}")

    log(f"Input folder: {input_folder}", log_lines)
    log(f"Output PDF: {output_pdf}", log_lines)
    log(f"Total TIFF files discovered: {len(raw_files)}", log_lines)
    log(f"Valid numbered TIFF files: {actual_count}", log_lines)
    log(f"Sequence range discovered: {min_seq:03d}-{max_seq:03d}", log_lines)
    log(f"Expected count in discovered range: {expected_count}", log_lines)
    log(f"First file in order: {first_file}", log_lines)
    log(f"Last file in order: {last_file}", log_lines)
    log(f"Skipped filename count: {len(skipped_files)}", log_lines)
    log(f"Missing number count: {len(missing_numbers)}", log_lines)

    if missing_numbers:
        preview = ", ".join(f"{n:03d}" for n in missing_numbers[:20])
        if len(missing_numbers) > 20:
            preview += ", ..."
        print(f"Missing preview:   {preview}")
        log("Missing sequence numbers: " + ", ".join(f"{n:03d}" for n in missing_numbers), log_lines)
    else:
        print("Missing preview:   None")
        log("No missing sequence numbers detected in discovered range.", log_lines)

    write_manifest(manifest_file, numbered_files)
    log(f"Manifest written to: {manifest_file}", log_lines)

    print("\nCreating PDF...")
    processed_count = build_pdf(numbered_files, output_pdf, log_lines)

    print("\nResults")
    print("-" * 30)
    print(f"Pages processed:   {processed_count}")
    print(f"Output PDF:        {output_pdf}")
    print(f"Log file:          {log_file}")
    print(f"Manifest file:     {manifest_file}")

    log(f"Pages successfully processed: {processed_count}", log_lines)
    log(f"Output PDF written to: {output_pdf}", log_lines)

    if processed_count != actual_count:
        print("Status:            WARNING - processed count does not match valid file count")
        log("WARNING: Processed count does not match valid numbered file count.", log_lines)
    else:
        print("Status:            OK - processed count matches valid file count")
        log("Processed count matches valid numbered file count.", log_lines)

    if actual_count != expected_count:
        log("WARNING: Valid file count does not match expected count in discovered range.", log_lines)

    Path(log_file).write_text("\n".join(log_lines), encoding="utf-8")
    print("\nDone.")


if __name__ == "__main__":
    main()