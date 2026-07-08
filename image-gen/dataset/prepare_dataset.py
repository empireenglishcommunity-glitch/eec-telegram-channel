"""
MACAL Empire — Dataset Preparation Script.

Takes the curated seed images (the 40-80 best candidates you manually picked
from the ~100-150 generated seeds — see DATASET-SPEC.md) and turns them into a
Kohya SS-ready training folder: validated, resized, captioned, and manifested.

This script does NOT generate images or call any AI model — it's a pure local
file-processing step. Run it either on Kaggle (in the same session) or on your
own machine with just `pip install pillow`.

------------------------------------------------------------------------------
USAGE
------------------------------------------------------------------------------

1. Put your manually-curated best images (40-80 of them) into:
       image-gen/dataset/raw_seed/
   (any common image format: .png, .jpg, .jpeg, .webp)

2. Edit `manifest_template.csv` — OR just run this script with --auto-caption
   to generate placeholder captions you then hand-edit afterward (recommended:
   auto-caption gives you a starting point, but you should still read every
   caption and correct it — see DATASET-SPEC.md Section 7).

3. Run:
       python prepare_dataset.py --input raw_seed/ --output curated/ --auto-caption

4. Check `curated/` — it will contain:
       curated/
       ├── 0001.png  0001.txt
       ├── 0002.png  0002.txt
       ...
       └── manifest.csv   (final record of what went into training)

   Each .txt file is the exact caption Kohya SS reads during training
   (filename-matched to its .png, which is the convention Kohya SS expects).

------------------------------------------------------------------------------
"""
import argparse
import csv
import os
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Missing dependency. Run: pip install pillow")
    sys.exit(1)

TRIGGER_WORD = "macalempire style"
TARGET_RESOLUTION = 1024  # SDXL native training resolution (DATASET-SPEC.md Section 6)
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

# Generic placeholder caption fragments used by --auto-caption as a STARTING
# POINT ONLY. DATASET-SPEC.md is explicit: auto-captions are a time-saver, not
# a substitute for manual review. Always read and correct every caption.
PLACEHOLDER_SUBJECT = "a MACAL Empire brand image"


def find_images(input_dir: Path) -> list[Path]:
    images = sorted([
        p for p in input_dir.iterdir()
        if p.suffix.lower() in VALID_EXTENSIONS
    ])
    return images


def validate_image(path: Path) -> tuple[bool, str]:
    """Check resolution and basic integrity. Returns (is_valid, reason)."""
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            w, h = img.size
            if w < TARGET_RESOLUTION or h < TARGET_RESOLUTION:
                return False, f"too small ({w}x{h}, need >= {TARGET_RESOLUTION}x{TARGET_RESOLUTION})"
            return True, "ok"
    except Exception as e:
        return False, f"corrupt or unreadable: {e}"


def resize_and_save(src: Path, dest: Path, size: int = TARGET_RESOLUTION):
    """Center-crop to square, then resize to the target training resolution."""
    with Image.open(src) as img:
        img = img.convert("RGB")
        w, h = img.size
        # Center crop to square
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        # Resize to target resolution
        img = img.resize((size, size), Image.LANCZOS)
        img.save(dest, "PNG")



def write_caption(dest_txt: Path, subject_description: str):
    """Write a caption file in Kohya SS's expected format: trigger word first."""
    caption = f"{TRIGGER_WORD}, {subject_description}"
    dest_txt.write_text(caption, encoding="utf-8")


def load_manual_captions(manifest_path: Path) -> dict:
    """
    Load manually-written captions from a CSV if one exists, keyed by filename.
    Expected columns: filename, caption, category, source, curated
    (matches manifest_template.csv format)
    """
    captions = {}
    if not manifest_path.exists():
        return captions
    with open(manifest_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row.get("filename", "").strip()
            caption = row.get("caption", "").strip()
            if fname and caption:
                captions[fname] = caption
    return captions


def process_dataset(input_dir: Path, output_dir: Path, auto_caption: bool, manifest_path: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    images = find_images(input_dir)

    if not images:
        print(f"No images found in {input_dir}. Nothing to do.")
        print(f"Supported extensions: {', '.join(sorted(VALID_EXTENSIONS))}")
        return

    manual_captions = load_manual_captions(manifest_path)

    accepted = []
    rejected = []

    for idx, src_path in enumerate(images, start=1):
        is_valid, reason = validate_image(src_path)
        if not is_valid:
            rejected.append((src_path.name, reason))
            print(f"  SKIP  {src_path.name}: {reason}")
            continue

        new_name = f"{idx:04d}"
        dest_png = output_dir / f"{new_name}.png"
        dest_txt = output_dir / f"{new_name}.txt"

        resize_and_save(src_path, dest_png)

        # Caption priority: manual manifest entry > auto-caption placeholder
        if src_path.name in manual_captions:
            caption_body = manual_captions[src_path.name]
            # Strip trigger word if the manual caption already includes it,
            # to avoid double-prefixing — write_caption always adds it fresh.
            if caption_body.lower().startswith(TRIGGER_WORD.lower()):
                caption_body = caption_body[len(TRIGGER_WORD):].lstrip(", ")
            write_caption(dest_txt, caption_body)
        elif auto_caption:
            write_caption(dest_txt, f"{PLACEHOLDER_SUBJECT} ({src_path.stem})")
            print(f"  NOTE  {dest_txt.name}: placeholder caption written — "
                  f"EDIT THIS BY HAND before training (see DATASET-SPEC.md Section 7)")
        else:
            write_caption(dest_txt, "REPLACE_THIS_CAPTION")
            print(f"  NOTE  {dest_txt.name}: no caption available — "
                  f"placeholder written, must be edited before training")

        accepted.append({
            "filename": f"{new_name}.png",
            "original_source": src_path.name,
            "caption": dest_txt.read_text(encoding="utf-8"),
        })
        print(f"  OK    {src_path.name} -> {dest_png.name}")

    # Write the final manifest recording exactly what went into training
    final_manifest = output_dir / "manifest.csv"
    with open(final_manifest, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "original_source", "caption"])
        writer.writeheader()
        writer.writerows(accepted)

    print()
    print(f"Done. {len(accepted)} images accepted, {len(rejected)} rejected.")
    print(f"Output folder: {output_dir}")
    print(f"Manifest: {final_manifest}")

    if len(accepted) < 40:
        print()
        print(f"WARNING: only {len(accepted)} images accepted. DATASET-SPEC.md")
        print("recommends 40-80 curated images for a reliable style LoRA.")
        print("Consider generating more seed candidates before training.")

    if any(row["caption"].startswith(f"{TRIGGER_WORD}, REPLACE_THIS_CAPTION") or
           "placeholder" in row["caption"] or
           PLACEHOLDER_SUBJECT in row["caption"]
           for row in accepted):
        print()
        print("REMINDER: some captions are still placeholders. Open each .txt file")
        print("in curated/ and write a real description before running training.")


def main():
    parser = argparse.ArgumentParser(description="Prepare MACAL Empire LoRA training dataset")
    parser.add_argument("--input", default="raw_seed", help="Folder with curated source images")
    parser.add_argument("--output", default="curated", help="Folder to write the training-ready dataset")
    parser.add_argument("--manifest", default="manifest_template.csv",
                         help="CSV with manual captions (filename,caption,...) — used if present")
    parser.add_argument("--auto-caption", action="store_true",
                         help="Write placeholder captions for images with no manual entry "
                              "(you MUST edit these by hand afterward)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    input_dir = (script_dir / args.input).resolve()
    output_dir = (script_dir / args.output).resolve()
    manifest_path = (script_dir / args.manifest).resolve()

    print(f"Input:    {input_dir}")
    print(f"Output:   {output_dir}")
    print(f"Manifest: {manifest_path}")
    print()

    process_dataset(input_dir, output_dir, args.auto_caption, manifest_path)


if __name__ == "__main__":
    main()
