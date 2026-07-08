# MACAL Empire Image Generation — Master Run Guide

> Follow this document top to bottom on your first run. Everything referenced
> here already exists in this `image-gen/` folder — this guide just tells you
> the order to use it in and what to expect at each step.
>
> **Cost: $0.** Everything below runs on Kaggle's free GPU tier (30 hrs/week,
> no credit card). See `docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md` Section
> 2.5 for the full reasoning behind this approach and when to eventually move
> to paid infrastructure.

## Folder map (what you're about to use)

```
image-gen/
├── RUN_GUIDE.md                          ← you are here
├── dataset/
│   ├── DATASET-SPEC.md                   ← read this first (full spec)
│   ├── seed_prompts.py                   ← Step 2: generates bootstrap prompts
│   ├── prepare_dataset.py                ← Step 4: processes your curated picks
│   └── manifest_template.csv             ← Step 4: manual caption source
├── kaggle/
│   └── MACAL_Empire_Setup.ipynb          ← Step 1: environment + ComfyUI
├── comfyui/
│   ├── generate_workflow.py              ← builds the generation graph
│   ├── batch_runner.py                   ← Steps 3 & 6: runs batches
│   └── make_watermark.py                 ← generates the brand watermark
└── training/
    ├── dataset_config.toml               ← Step 5: Kohya SS dataset config
    ├── train_config.toml                 ← Step 5: Kohya SS hyperparameters
    └── MACAL_Empire_Train_LoRA.ipynb      ← Step 5: trains the LoRA
```

---

## Step 0 — One-time account setup

1. Create a free Kaggle account at kaggle.com (no credit card required).
2. Verify your phone number if prompted (Kaggle requires this to enable GPU access).

---

## Step 1 — Environment setup (~20 min, one-time per session)

1. Go to kaggle.com → Create → New Notebook.
2. Upload `image-gen/kaggle/MACAL_Empire_Setup.ipynb` (File → Upload Notebook),
   or copy its cells in manually.
3. In the right sidebar, set **Accelerator → GPU T4 x2** (or P100 if offered).
4. Run all cells top to bottom. This installs ComfyUI, custom nodes, and
   downloads the SDXL base model (~7GB, takes a few minutes).
5. The last setup cell prints a **Cloudflare tunnel URL** — open it in a new
   browser tab. This is your live ComfyUI web interface.

**Keep this session running** for the next two steps — you'll come back to it.

---

## Step 2 — Generate seed prompts (~1 min)

On your own machine (or in a Kaggle code cell):

```bash
cd image-gen/dataset
python seed_prompts.py > seed_prompts_output.txt
```

This writes ~105 prompts across 5 categories (abstract, architectural, object,
portrait, wildcard) — see `DATASET-SPEC.md` Section 5 for why this mix.
Upload `seed_prompts_output.txt` into your Kaggle session's working directory.

---

## Step 3 — Generate seed candidates (~30-60 min, uses GPU quota)

Back in your Kaggle notebook (new cell, or a terminal if Kaggle offers one):

```bash
cd /kaggle/working/eec-telegram-channel/image-gen/comfyui  # adjust path as needed
python batch_runner.py \
    --comfyui-url http://127.0.0.1:8188 \
    --prompts-file /kaggle/working/seed_prompts_output.txt \
    --output-dir /kaggle/working/raw_seed \
    --no-lora
```

`--no-lora` is essential here — there's no trained LoRA yet, this step is
generating raw candidates from base SDXL to build your training set from.

This generates ~105 images (a few minutes each on T4, so budget most of an
hour). Check `batch_log.csv` in the output folder afterward — if any jobs
failed, note which prompts and consider rerunning just those.

**Download the `raw_seed/` folder** (zip it first: `!zip -r raw_seed.zip raw_seed/`)
before your session ends.

---

## Step 4 — Curate and prepare the training dataset (~1-2 hours, manual, no GPU needed)

This is the most important step — take your time here.

1. Look through all ~105 generated images. Pick your **best 40-80** that most
   consistently feel like "MACAL Empire" — Dark Luxury, Imperial, Cinematic.
   Discard anything muddy, off-palette, or low quality.
2. Put your chosen images into `image-gen/dataset/raw_seed/` (only the ones
   you're keeping).
3. For each kept image, write a real caption. Either:
   - Add a row to `manifest_template.csv` (filename, caption, ...), or
   - Run with `--auto-caption` and hand-edit every resulting `.txt` file
     afterward (do not skip the hand-editing — see `DATASET-SPEC.md` Section 7)
4. Run:
   ```bash
   cd image-gen/dataset
   python prepare_dataset.py --input raw_seed --output curated --auto-caption
   ```
5. Confirm the script reports 40-80 accepted images and no leftover placeholder
   warnings. Fix anything it flags before moving on.

---

## Step 5 — Train the brand LoRA (~1-3 hours GPU time)

1. Upload your `curated/` folder into a **new** Kaggle session at
   `/kaggle/working/macal_empire_dataset/curated/` (as a Kaggle Dataset is
   cleanest, so you don't re-upload it every session).
2. Upload/run `image-gen/training/MACAL_Empire_Train_LoRA.ipynb`.
3. Set Accelerator to GPU T4 x2 or P100 again.
4. Run all cells top to bottom. The dataset-verification cell will stop you
   if any captions still look like placeholders — fix those first if flagged.
5. Training runs ~1-3 hours for 1800 steps. Sample previews save every 300
   steps — watch them appear and get a feel for how the style is converging.
6. At the end, download `macal_empire_lora_output.zip` — this contains your
   trained LoRA checkpoints (`.safetensors` files) and all sample previews.

**Picking the best checkpoint:** don't assume the last one is best. Compare
the sample previews across checkpoints (every 300 steps) and pick whichever
looks most consistently on-brand without visible artifacting (DATASET-SPEC.md
Section 5.3 — more training steps is not automatically better).

---

## Step 6 — Generate real branded content (~ongoing, whenever you need images)

1. Back in a ComfyUI session (Step 1's notebook, run fresh if it's a new
   session), copy your chosen LoRA checkpoint into
   `/kaggle/working/ComfyUI/models/loras/macalempire_style_sdxl.safetensors`
   (Setup notebook Cell 8 has a ready-made cell for this).
2. Generate your brand watermark once (only needs doing once, reuse the file):
   ```bash
   cd image-gen/comfyui
   python make_watermark.py
   ```
3. Write your real content prompts (one per line, always starting with
   `macalempire style,` to activate the trained look) into a text file, e.g.
   `my_content_prompts.txt`.
4. Run the batch runner with the LoRA enabled and watermark on:
   ```bash
   python batch_runner.py \
       --comfyui-url http://127.0.0.1:8188 \
       --prompts-file my_content_prompts.txt \
       --output-dir /kaggle/working/output \
       --watermark
   ```
5. Download your finished, watermarked, on-brand images from `output/`.

Repeat Step 6 as often as you need new content — this is your recurring
"content generation day" workflow until/unless you move to always-on paid
infrastructure (see the infrastructure report's Section 2.5 "graduating" criteria).

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `CUDA available: False` in the setup notebook | Accelerator not set to GPU — check the right sidebar setting, restart the session |
| ComfyUI tunnel URL never appears | Cloudflared download may have been rate-limited; re-run the launch cell, or check `comfy_proc.stdout` for a Python error during ComfyUI startup |
| `batch_runner.py` times out waiting for a job | ComfyUI may have crashed (check for an OOM in its logs) — try reducing `steps` in `generate_workflow.py`'s defaults, or confirm only one job runs at a time (the script is already sequential) |
| Kohya SS training fails with an out-of-memory error | Confirm `train_config.toml` still has `gradient_checkpointing = true`, `mixed_precision = "fp16"`, and `train_batch_size = 1` — these are required to fit training in 16GB VRAM |
| Watermark looks like boxes/tofu characters instead of text | No serif `.ttf` font was found — see the warning `make_watermark.py` prints; install a font or accept the fallback bitmap font |
| Generated images don't look "on brand" at all, even with the LoRA | Check the LoRA actually loaded (ComfyUI console will show a load message); try increasing `lora_strength` in `generate_workflow.py` toward 1.0; if still off, the dataset curation in Step 4 likely needs a stronger, more consistent selection |
| Kaggle session disconnects mid-batch | This is why `batch_runner.py` logs every job's status to `batch_log.csv` — check which prompts succeeded, and resubmit only the failed ones in a new session |

---

## When you're ready to automate (paid path)

Everything above is a **manual, session-based** workflow by design (Step 0 in
`docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md` Section 2.5). Once you want
this running unattended — triggered by n8n, no one at the keyboard — that's
when you move to a rented or owned always-on GPU (Section 2.3 of that report)
and wire `batch_runner.py`'s logic into an n8n workflow calling the same
ComfyUI API, just on a server that never turns off.
