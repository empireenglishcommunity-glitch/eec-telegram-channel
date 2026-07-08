"""
Generates MACAL_Empire_Setup.ipynb from plain Python cell definitions.

Why a generator instead of hand-editing the .ipynb JSON directly: notebooks are
JSON with a lot of boilerplate (cell metadata, output arrays, execution counts).
Editing cell content here in plain Python strings is far less error-prone, and
this script is what's actually tracked/reviewed in git — the .ipynb is a build
artifact, regenerate it by re-running this script after any edit.

Usage:
    python generate_notebook.py
    # writes MACAL_Empire_Setup.ipynb in the same directory
"""
import json
import os

CELLS = []


def md(text: str):
    CELLS.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    })


def code(text: str):
    CELLS.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    })


# ---------------------------------------------------------------------------
# Cell 1 — Title / overview
# ---------------------------------------------------------------------------
md("""# MACAL Empire — Zero-Budget Image Generation Setup (Kaggle)

This notebook sets up **ComfyUI + SDXL** for generating MACAL Empire brand images,
entirely on Kaggle's free GPU tier (T4/P100, ~30 hrs/week quota).

**Before running:** read `image-gen/dataset/DATASET-SPEC.md` in the repo for the
full brand/dataset spec. This notebook does NOT train a LoRA yet — it sets up the
environment and generates the seed candidate images (Task in `dataset/seed_prompts.py`).
LoRA training setup is a separate notebook step (see repo `image-gen/training/`).

**Session limits to plan around:** Kaggle sessions have a ~9-12 hour ceiling and a
60-minute idle timeout. Save your outputs to `/kaggle/working/` (persisted) and
download anything important before the session ends — the environment does not
survive between sessions, so re-run the setup cells each time you start fresh.
""")


# ---------------------------------------------------------------------------
# Cell 2 — GPU check
# ---------------------------------------------------------------------------
md("""## 1. Verify GPU is available

Make sure the notebook's **Accelerator** setting (right sidebar) is set to
**GPU T4 x2** or **GPU P100** before running this cell. If this shows no GPU,
stop and fix the accelerator setting first — everything below assumes CUDA.
""")

code("""!nvidia-smi
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
""")

# ---------------------------------------------------------------------------
# Cell 3 — Install ComfyUI
# ---------------------------------------------------------------------------
md("""## 2. Install ComfyUI

Clones ComfyUI into `/kaggle/working/ComfyUI` and installs its Python
dependencies. This takes a few minutes.
""")

code("""%cd /kaggle/working
!git clone https://github.com/comfyanonymous/ComfyUI.git
%cd ComfyUI
!pip install -q -r requirements.txt
print("ComfyUI installed.")
""")

# ---------------------------------------------------------------------------
# Cell 4 — Custom nodes (upscale + image composite/watermark support)
# ---------------------------------------------------------------------------
md("""## 3. Install custom nodes

- **ComfyUI-Manager** — lets you install/manage further nodes from the UI later
- **ComfyUI_essentials** — provides reliable image composite/overlay nodes used
  for watermarking in the generation workflow (Task 6)
- **ComfyUI-Impact-Pack** — provides additional upscale utilities used for the
  4K tiled upscale step
""")

code("""%cd /kaggle/working/ComfyUI/custom_nodes
!git clone https://github.com/ltdrdata/ComfyUI-Manager.git
!git clone https://github.com/cubiq/ComfyUI_essentials.git
!git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git

%cd ComfyUI-Impact-Pack
!python install.py
%cd /kaggle/working/ComfyUI
print("Custom nodes installed.")
""")


# ---------------------------------------------------------------------------
# Cell 5 — Download SDXL base model
# ---------------------------------------------------------------------------
md("""## 4. Download the base model (SDXL 1.0)

Downloads the SDXL 1.0 base checkpoint into ComfyUI's model folder. This is
~6.9 GB and will take a few minutes depending on Kaggle's network speed.

**Note:** SDXL is the recommended starting model for this pipeline (see
`docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md` Section 3) because it trains
LoRAs faster and iterates quicker than FLUX — ideal for the free-tier, session-
limited workflow. FLUX can be added later once the SDXL brand LoRA is validated.
""")

code("""%cd /kaggle/working/ComfyUI/models/checkpoints
!wget -q --show-progress -O sd_xl_base_1.0.safetensors \\
    https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
print("SDXL base model downloaded.")
!ls -lh /kaggle/working/ComfyUI/models/checkpoints/
""")

# ---------------------------------------------------------------------------
# Cell 6 — Download a realism checkpoint (optional but recommended)
# ---------------------------------------------------------------------------
md("""## 5. (Recommended) Download a realism-tuned SDXL checkpoint

Base SDXL is decent but a community realism checkpoint (e.g., RealVisXL) gets
much closer to the "premium realism" brand requirement out of the box, before
the LoRA is even applied. This step is optional — skip it if you want to move
faster, the base checkpoint above works fine for testing the pipeline end-to-end.

**Manual step required:** CivitAI requires an account/API key for some
downloads and its direct-link URLs change per model version, so this cell is
left as a placeholder — get the current direct download link from
https://civitai.com/models/139562 (RealVisXL) and paste it into the `wget`
command below.
""")

code("""# Uncomment and fill in the current direct-download URL from CivitAI, then run:
# %cd /kaggle/working/ComfyUI/models/checkpoints
# !wget -q --show-progress -O realvisxl.safetensors "PASTE_CIVITAI_DIRECT_LINK_HERE"
print("Skipped — optional step. Base SDXL checkpoint from Cell 5 is sufficient to proceed.")
""")

# ---------------------------------------------------------------------------
# Cell 7 — Launch ComfyUI with a public tunnel
# ---------------------------------------------------------------------------
md("""## 6. Launch ComfyUI and expose it via a public URL

Kaggle notebooks don't expose ports directly, so this launches ComfyUI in the
background and opens a **Cloudflare Tunnel** to get a temporary public URL you
can open in a new browser tab to use the ComfyUI web interface normally.

The tunnel URL prints below after a few seconds — click it to open ComfyUI.
Leave this cell running (it holds the ComfyUI server + tunnel alive) and do
your work in the tunnel URL tab.
""")

code("""import subprocess
import time
import re

%cd /kaggle/working/ComfyUI

# Start ComfyUI in the background, listening on all interfaces
comfy_proc = subprocess.Popen(
    ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)
print("ComfyUI starting... waiting 15s for it to boot")
time.sleep(15)

# Download and start a Cloudflare Tunnel (no account needed for quick tunnels)
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
!chmod +x cloudflared

tunnel_proc = subprocess.Popen(
    ["./cloudflared", "tunnel", "--url", "http://localhost:8188"],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
)

print("Waiting for tunnel URL...")
for _ in range(30):
    line = tunnel_proc.stdout.readline()
    match = re.search(r"https://[a-zA-Z0-9\\-]+\\.trycloudflare\\.com", line)
    if match:
        print(f"\\nComfyUI is live at: {match.group(0)}\\n")
        print("Open that URL in a new browser tab to use ComfyUI.")
        break
""")


# ---------------------------------------------------------------------------
# Cell 8 — (Later) Load the trained MACAL Empire LoRA once it exists
# ---------------------------------------------------------------------------
md("""## 7. (After training) Load your trained MACAL Empire LoRA

Once you've trained the brand LoRA (see `image-gen/training/`), copy the
resulting `.safetensors` file into ComfyUI's `models/loras/` folder so it
shows up in the LoRA loader node inside the ComfyUI web UI.

Skip this cell on your very first run — there's no LoRA yet until after you've
completed the seed generation, curation, and training steps.
""")

code("""import os

lora_path = "/kaggle/input/macal-empire-lora/macalempire_style.safetensors"  # adjust to your Kaggle dataset path
dest_dir = "/kaggle/working/ComfyUI/models/loras"
os.makedirs(dest_dir, exist_ok=True)

if os.path.exists(lora_path):
    !cp "{lora_path}" "{dest_dir}/"
    print("LoRA copied into ComfyUI models/loras/")
else:
    print("No trained LoRA found yet at that path — this is expected on your first run.")
    print("Come back to this cell after completing image-gen/training/.")
""")

# ---------------------------------------------------------------------------
# Cell 9 — Where to go next
# ---------------------------------------------------------------------------
md("""## 8. Next steps

1. Open the ComfyUI tunnel URL from Cell 6 in a new tab.
2. Load a default SDXL workflow (Workflow menu -> Load Default, or import
   `image-gen/comfyui/macal_empire_generate.json` from the repo).
3. Run the seed prompts from `image-gen/dataset/seed_prompts.py` through
   ComfyUI to generate your 100-150 candidate images (see
   `image-gen/dataset/DATASET-SPEC.md` for the curation process).
4. Download your favorite 40-80 candidates and follow
   `image-gen/dataset/prepare_dataset.py` to caption and organize them.
5. Move to `image-gen/training/` to train the actual brand LoRA.
6. Come back to Cell 7/8 above with your trained LoRA to generate real
   on-brand content.
""")


# ---------------------------------------------------------------------------
# Notebook assembly
# ---------------------------------------------------------------------------
NOTEBOOK = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.10"},
        "accelerator": "GPU",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main():
    out_path = os.path.join(os.path.dirname(__file__), "MACAL_Empire_Setup.ipynb")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(NOTEBOOK, f, indent=1)
    print(f"Wrote {out_path} ({len(CELLS)} cells)")


if __name__ == "__main__":
    main()
