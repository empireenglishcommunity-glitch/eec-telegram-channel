"""
MACAL Empire — Premium branded content generation with hi-res fix.

Upgrades over the first pass (gen_content.py):
  1. Higher base steps (40 vs 35) and tuned CFG for crisper base composition
  2. Hi-res fix: upscale the base 1024x1024 result to 1536x1536, then run a
     second img2img refinement pass at low denoise (0.4) through the SAME
     LoRA-fused pipeline. This is the standard technique for adding real
     fine detail (fabric weave, metal micro-reflections, marble veining)
     that a single low-res pass cannot produce — not a "trick", it's what
     serious SDXL production pipelines actually do.
  3. Fixed prompts: any concept that could be read as an open-air space
     (columns, gates) is now explicitly framed as an enclosed interior with
     "no sky visible, solid dark wall/ceiling" to prevent SDXL's bright-sky
     prior from leaking through, per the root-cause finding from the first
     content batch (architectural_01 showed a light grey sky between
     columns; every enclosed-interior prompt in that same batch was
     flawless).
  4. Stronger negative prompt additions targeting sky/daylight leakage.
"""
import os
os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")

import gc
import torch
import csv
import random
from pathlib import Path
from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    DPMSolverMultistepScheduler,
)
from PIL import Image

MODEL = "/kaggle/working/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors"
LORA = "/kaggle/working/macal_empire_lora_output/macalempire_style_sdxl.safetensors"
OUT_DIR = Path("/kaggle/working/macal_empire_content_hires")
WATERMARK_PATH = Path("/kaggle/working/watermark.png")

OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_SUFFIX = ", dark near-black background, moody low-key lighting, imperial luxury aesthetic, highly detailed, sharp focus, 8k uhd"

NEGATIVE = (
    "cartoon, illustration, anime, low quality, blurry, oversaturated, "
    "watermark, text, logo, cluttered, bright daylight, pastel colors, "
    "cheap looking, plastic, low contrast, white background, light background, "
    "sky, daylight sky, outdoor, blue sky, clouds, bright sky, overexposed, "
    "grainy, noisy, jpeg artifacts, low resolution, soft focus"
)

# Same categories as the first batch, but architectural prompts rewritten to
# explicitly close off the sky per the root-cause finding.
CONTENT_PROMPTS = [
    ("architectural_01", "macalempire style, grand imperial columns inside an enclosed dark hall, no sky visible, solid dark ceiling, bathed in warm golden light, deep shadow, cinematic" + STYLE_SUFFIX),
    ("architectural_02", "macalempire style, a spiral staircase in black marble with a gold handrail, enclosed dark stairwell, dramatic overhead light" + STYLE_SUFFIX),
    ("architectural_03", "macalempire style, empty imperial throne room, dark walls, gold trim catching a single light source" + STYLE_SUFFIX),
    ("object_01", "macalempire style, an antique gold compass on black velvet, cinematic macro shot" + STYLE_SUFFIX),
    ("object_02", "macalempire style, a gold signet ring on black leather, macro detail, shallow depth of field" + STYLE_SUFFIX),
    ("object_03", "macalempire style, a gold-rimmed obsidian goblet on a black table, single candle light" + STYLE_SUFFIX),
    ("portrait_01", "macalempire style, portrait of a person in silhouette, rim-lit in gold against a dark imperial hallway" + STYLE_SUFFIX),
    ("portrait_02", "macalempire style, a solitary figure walking away down a dark corridor toward a distant gold light" + STYLE_SUFFIX),
    ("abstract_01", "macalempire style, wisps of golden smoke curling against a near-black backdrop" + STYLE_SUFFIX),
    ("abstract_02", "macalempire style, gold embers floating upward into darkness, cinematic bokeh" + STYLE_SUFFIX),
]

BASE_RES = 1024
HIRES_SCALE = 1.5  # -> 1536x1536, a proven safe hi-res-fix ratio for SDXL (avoids the duplication/artifacting seen above ~2x without tiling)
HIRES_DENOISE = 0.4  # low enough to preserve base composition, high enough to add real detail


def apply_watermark(image: Image.Image, watermark_path: Path) -> Image.Image:
    if not watermark_path.exists():
        print(f"  WARNING: watermark not found at {watermark_path}, skipping watermark")
        return image
    base = image.convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")
    target_width = int(base.width * 0.22)  # slightly smaller relative to the larger final image
    scale = target_width / watermark.width
    watermark = watermark.resize((target_width, int(watermark.height * scale)), Image.LANCZOS)
    margin = int(base.width * 0.025)
    position = (base.width - watermark.width - margin, base.height - watermark.height - margin)
    composited = base.copy()
    composited.alpha_composite(watermark, position)
    return composited.convert("RGB")


print("Loading base txt2img pipeline...")
pipe = StableDiffusionXLPipeline.from_single_file(
    MODEL, torch_dtype=torch.float16, use_safetensors=True
).to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)

print("Loading LoRA weights...")
pipe.load_lora_weights(LORA)
pipe.fuse_lora(lora_scale=0.85)

# VAE slicing/tiling cuts peak VRAM during the 1536x1536 decode step
# significantly at negligible quality cost -- needed because the first
# unpatched version of this script OOM'd on the SECOND image in a batch
# (first image succeeded, confirming the 1536px pass itself fits in 15GB,
# but repeated allocations across a loop fragmented/accumulated memory).
pipe.enable_vae_slicing()
pipe.enable_vae_tiling()

# StableDiffusionXLPipeline (txt2img) does NOT accept image=/strength= for a
# refinement pass -- that requires the separate Img2Img pipeline class. Build
# it via from_pipe() so it REUSES the already-loaded (and LoRA-fused) UNet,
# VAE, and text encoders in memory rather than reloading the 6.5GB checkpoint
# and LoRA a second time.
refiner_pipe = StableDiffusionXLImg2ImgPipeline.from_pipe(pipe).to("cuda")
refiner_pipe.enable_vae_slicing()
refiner_pipe.enable_vae_tiling()

log_rows = []
# Resume support: skip any concept name that already has a saved output file
# from a prior (possibly crashed) run, so a mid-batch OOM doesn't waste the
# GPU time already spent on earlier images in the batch.
already_done = {p.name.split("_seed")[0] for p in OUT_DIR.glob("*.png")}
if already_done:
    print(f"Found {len(already_done)} already-completed image(s), will skip: {sorted(already_done)}")

for name, prompt in CONTENT_PROMPTS:
    if name in already_done:
        print(f"[{name}] SKIP -- already completed in a prior run")
        continue

    seed = random.randint(0, 2**32 - 1)
    generator = torch.Generator("cuda").manual_seed(seed)

    print(f"[{name}] Base pass (seed={seed})...")
    base_image = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        num_inference_steps=40,
        guidance_scale=7.5,
        width=BASE_RES,
        height=BASE_RES,
        generator=generator,
    ).images[0]

    hires_size = int(BASE_RES * HIRES_SCALE)
    print(f"[{name}] Upscaling to {hires_size}x{hires_size} and running hi-res refinement pass...")
    upscaled = base_image.resize((hires_size, hires_size), Image.LANCZOS)

    refined_image = refiner_pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        image=upscaled,
        strength=HIRES_DENOISE,
        num_inference_steps=30,
        guidance_scale=7.5,
        generator=generator,
    ).images[0]

    watermarked = apply_watermark(refined_image, WATERMARK_PATH)
    out_path = OUT_DIR / f"{name}_seed{seed}.png"
    watermarked.save(out_path, "PNG")
    print(f"  saved {out_path} ({watermarked.size})")
    log_rows.append({
        "name": name, "filename": out_path.name, "seed": seed,
        "base_res": BASE_RES, "hires_res": hires_size, "hires_denoise": HIRES_DENOISE,
        "prompt": prompt, "status": "success",
    })

    # Explicit cleanup between iterations -- this is the actual fix for the
    # OOM crash seen on image #2 of the unpatched script. Intermediate
    # tensors (base_image, upscaled, refined_image) and their autograd/cuda
    # allocator state don't always get freed promptly just because the
    # Python objects go out of scope at the top of the next loop iteration;
    # forcing gc + emptying the CUDA allocator cache here reclaims that
    # memory deterministically before the next image's base pass starts.
    del base_image, upscaled, refined_image, watermarked
    gc.collect()
    torch.cuda.empty_cache()
    mem_used = torch.cuda.memory_allocated() / 1e9
    print(f"  [cleanup] CUDA memory allocated after cleanup: {mem_used:.2f} GB")

with open(OUT_DIR / "content_batch_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "filename", "seed", "base_res", "hires_res", "hires_denoise", "prompt", "status"])
    writer.writeheader()
    writer.writerows(log_rows)

print(f"\nDONE. {len(log_rows)} hi-res images generated in {OUT_DIR}")
