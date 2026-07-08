"""
Generates MACAL_Empire_Train_LoRA.ipynb — the Kaggle notebook that trains the
brand style LoRA using Kohya SS (sd-scripts), consuming the dataset produced
by image-gen/dataset/prepare_dataset.py and the configs in this folder.

Usage:
    python generate_training_notebook.py
    # writes MACAL_Empire_Train_LoRA.ipynb in this directory
"""
import json
import os

CELLS = []


def md(text: str):
    CELLS.append({"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)})


def code(text: str):
    CELLS.append({
        "cell_type": "code", "execution_count": None, "metadata": {},
        "outputs": [], "source": text.splitlines(keepends=True),
    })


md("""# MACAL Empire — Train the Brand Style LoRA (Kaggle)

Trains an SDXL LoRA that locks in the MACAL Empire "Dark Luxury / Imperial /
Cinematic" look, using the curated dataset you prepared with
`image-gen/dataset/prepare_dataset.py`.

**Prerequisites (do these BEFORE running this notebook):**
1. Run `MACAL_Empire_Setup.ipynb` (or at minimum have SDXL base model downloaded)
2. Generate seed images, curate your best 40-80, run `prepare_dataset.py`
3. Upload the resulting `curated/` folder to this Kaggle session (as a Kaggle
   Dataset, or via the file upload panel) — this notebook expects it at
   `/kaggle/working/macal_empire_dataset/curated/`
4. Read every `.txt` caption file in `curated/` and confirm none are still
   placeholders (see DATASET-SPEC.md Section 7)

**Time estimate:** ~1-3 hours on a T4/P100 for the full 1800-step run
(comfortably within Kaggle's ~9-12hr session limit and 30hr/week quota).
""")

code("""!nvidia-smi
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
""")

md("""## 1. Install Kohya SS (sd-scripts)

Clones the sd-scripts repository and installs its dependencies. This is the
same underlying engine the Kohya SS GUI uses — we drive it directly via CLI
here since Kaggle has no display for the GUI.
""")

code("""%cd /kaggle/working
!git clone https://github.com/kohya-ss/sd-scripts.git
%cd sd-scripts
!pip install -q -r requirements.txt
!pip install -q xformers bitsandbytes
print("sd-scripts installed.")
""")



md("""## 2. Verify the curated dataset is in place

Checks that `/kaggle/working/macal_empire_dataset/curated/` exists, contains
matched `.png`/`.txt` pairs, and flags any caption file that still looks like
an unedited placeholder before you burn GPU hours training on bad captions.
""")

code("""import os
from pathlib import Path

dataset_dir = Path("/kaggle/working/macal_empire_dataset/curated")
assert dataset_dir.exists(), (
    f"Dataset folder not found at {dataset_dir}. Upload your curated/ folder "
    f"from image-gen/dataset/prepare_dataset.py first (see notebook intro)."
)

pngs = sorted(dataset_dir.glob("*.png"))
txts = sorted(dataset_dir.glob("*.txt"))
print(f"Found {len(pngs)} images and {len(txts)} caption files.")

assert len(pngs) == len(txts), "Mismatched image/caption count — every .png needs a matching .txt"

if len(pngs) < 40:
    print(f"WARNING: only {len(pngs)} images. DATASET-SPEC.md recommends 40-80 for a reliable style LoRA.")
    print("Training will still run, but consider adding more curated images.")

placeholder_flags = ["REPLACE_THIS_CAPTION", "placeholder", "a MACAL Empire brand image"]
bad_captions = []
for txt in txts:
    content = txt.read_text(encoding="utf-8")
    if any(flag in content for flag in placeholder_flags):
        bad_captions.append(txt.name)
    if not content.lower().startswith("macalempire style"):
        print(f"WARNING: {txt.name} does not start with the trigger word 'macalempire style' — check it.")

if bad_captions:
    print(f"\\nSTOP: {len(bad_captions)} caption(s) still look like unedited placeholders:")
    for name in bad_captions:
        print(f"  - {name}")
    print("\\nGo back and write real captions for these before training (DATASET-SPEC.md Section 7).")
else:
    print("\\nAll captions look edited. Ready to train.")
""")

md("""## 3. Copy training configs from the repo

If you've cloned the `eec-telegram-channel` repo into this Kaggle session,
this copies the configs from `image-gen/training/`. Otherwise, upload
`dataset_config.toml` and `train_config.toml` manually and skip this cell.
""")

code("""import shutil
from pathlib import Path

repo_config_dir = Path("/kaggle/working/eec-telegram-channel/image-gen/training")
target_dir = Path("/kaggle/working/training_config")
target_dir.mkdir(exist_ok=True)

if repo_config_dir.exists():
    for fname in ["dataset_config.toml", "train_config.toml"]:
        shutil.copy(repo_config_dir / fname, target_dir / fname)
    print(f"Configs copied to {target_dir}")
else:
    print(f"Repo not found at {repo_config_dir}.")
    print(f"Manually upload dataset_config.toml and train_config.toml into {target_dir}")
""")



md("""## 4. Create sample prompts for training-time previews

Writes a small prompt file so sd-scripts generates preview images at each
checkpoint (every 300 steps, per `train_config.toml`) — this lets you watch
the MACAL Empire style emerge without leaving the training session.
""")

code("""sample_prompts = [
    "macalempire style, a marble column bathed in warm golden light, cinematic shadow --w 1024 --h 1024",
    "macalempire style, an ornate gold crown resting on black stone, dramatic lighting --w 1024 --h 1024",
    "macalempire style, portrait of a person in silhouette rim-lit in gold --w 1024 --h 1024",
]

with open("/kaggle/working/sample_prompts.txt", "w") as f:
    f.write("\\n".join(sample_prompts))

print("Sample prompts written:")
for p in sample_prompts:
    print(f"  - {p}")
""")

md("""## 5. Launch training

Runs `sdxl_train_network.py` with the two config files. This is the actual
training run — expect ~1-3 hours on a T4/P100 for 1800 steps.

**Kaggle session tip:** this cell will run for a long time. Keep the browser
tab open (or check back periodically) — Kaggle's 60-minute *idle* timeout
tracks browser/kernel inactivity, not GPU usage, so an actively-running training
cell should not trigger it, but don't rely on walking away for hours unchecked.
""")

code("""%cd /kaggle/working/sd-scripts

!accelerate launch --num_cpu_threads_per_process 2 sdxl_train_network.py \\
    --config_file /kaggle/working/training_config/train_config.toml \\
    --dataset_config /kaggle/working/training_config/dataset_config.toml
""")

md("""## 6. Check your results

Lists the trained LoRA checkpoints and sample preview images. Compare the
samples across checkpoints (every 300 steps) — pick the checkpoint that looks
most consistently "on-brand" without artifacting, which is not always the
very last one (see DATASET-SPEC.md Section 5.3 on overfitting).
""")

code("""from pathlib import Path

output_dir = Path("/kaggle/working/macal_empire_lora_output")
print("Trained LoRA checkpoints:")
for f in sorted(output_dir.glob("*.safetensors")):
    print(f"  {f.name}  ({f.stat().st_size / 1e6:.1f} MB)")

sample_dir = output_dir / "sample"
if sample_dir.exists():
    print("\\nSample preview images:")
    for f in sorted(sample_dir.glob("*.png")):
        print(f"  {f.name}")
    print("\\nDownload these from the Kaggle file browser to visually compare checkpoints.")
""")

md("""## 7. Download your trained LoRA

Zips the output folder so you can download it from Kaggle's output panel and
either re-upload it as a Kaggle Dataset (for reuse in the generation notebook)
or download it locally.
""")

code("""%cd /kaggle/working
!zip -r macal_empire_lora_output.zip macal_empire_lora_output/
print("Zipped. Download macal_empire_lora_output.zip from the Kaggle output panel.")
print("Next: go to MACAL_Empire_Setup.ipynb Cell 8 to load this LoRA into ComfyUI for generation.")
""")


NOTEBOOK = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main():
    out_path = os.path.join(os.path.dirname(__file__), "MACAL_Empire_Train_LoRA.ipynb")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(NOTEBOOK, f, indent=1)
    print(f"Wrote {out_path} ({len(CELLS)} cells)")


if __name__ == "__main__":
    main()
