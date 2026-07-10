"""
MACAL Empire — Real branded content generation using the trained LoRA.
Uses a proper diffusers inference pipeline (proven working, unlike Kohya's
built-in low-fidelity preview sampler) + the real brand watermark.
"""
import torch
import io
import csv
import random
from pathlib import Path
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image

MODEL = "/kaggle/working/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors"
LORA = "/kaggle/working/macal_empire_lora_output/macalempire_style_sdxl.safetensors"
OUT_DIR = Path("/kaggle/working/macal_empire_content")
WATERMARK_PATH = Path("/kaggle/working/watermark.png")

OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_SUFFIX = ", dark near-black background, moody low-key lighting, imperial luxury aesthetic"

NEGATIVE = (
    "cartoon, illustration, anime, low quality, blurry, oversaturated, "
    "watermark, text, logo, cluttered, bright daylight, pastel colors, "
    "cheap looking, plastic, low contrast, white background, light background"
)

# A representative spread across the brand's established categories
CONTENT_PROMPTS = [
    ("architectural_01", "macalempire style, grand imperial columns bathed in warm golden light, deep shadow, cinematic" + STYLE_SUFFIX),
    ("architectural_02", "macalempire style, a spiral staircase in black marble with a gold handrail, dramatic overhead light" + STYLE_SUFFIX),
    ("architectural_03", "macalempire style, empty imperial throne room, dark walls, gold trim catching a single light source" + STYLE_SUFFIX),
    ("object_01", "macalempire style, an antique gold compass on black velvet, cinematic macro shot" + STYLE_SUFFIX),
    ("object_02", "macalempire style, a gold signet ring on black leather, macro detail, shallow depth of field" + STYLE_SUFFIX),
    ("object_03", "macalempire style, a gold-rimmed obsidian goblet on a black table, single candle light" + STYLE_SUFFIX),
    ("portrait_01", "macalempire style, portrait of a person in silhouette, rim-lit in gold against a dark imperial hallway" + STYLE_SUFFIX),
    ("portrait_02", "macalempire style, a solitary figure walking away down a dark corridor toward a distant gold light" + STYLE_SUFFIX),
    ("abstract_01", "macalempire style, wisps of golden smoke curling against a near-black backdrop" + STYLE_SUFFIX),
    ("abstract_02", "macalempire style, gold embers floating upward into darkness, cinematic bokeh" + STYLE_SUFFIX),
]

def apply_watermark(image: Image.Image, watermark_path: Path) -> Image.Image:
    if not watermark_path.exists():
        print(f"  WARNING: watermark not found at {watermark_path}, skipping watermark")
        return image
    base = image.convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")
    target_width = int(base.width * 0.3)
    scale = target_width / watermark.width
    watermark = watermark.resize((target_width, int(watermark.height * scale)), Image.LANCZOS)
    margin = int(base.width * 0.03)
    position = (base.width - watermark.width - margin, base.height - watermark.height - margin)
    composited = base.copy()
    composited.alpha_composite(watermark, position)
    return composited.convert("RGB")


print("Loading base pipeline...")
pipe = StableDiffusionXLPipeline.from_single_file(
    MODEL, torch_dtype=torch.float16, use_safetensors=True
).to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)

print("Loading LoRA weights...")
pipe.load_lora_weights(LORA)
pipe.fuse_lora(lora_scale=0.85)  # slightly below max strength per DATASET-SPEC.md tuning guidance

log_rows = []
for name, prompt in CONTENT_PROMPTS:
    seed = random.randint(0, 2**32 - 1)
    print(f"Generating: {name} (seed={seed})")
    image = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        num_inference_steps=35,
        guidance_scale=7.0,
        width=1024,
        height=1024,
        generator=torch.Generator("cuda").manual_seed(seed),
    ).images[0]

    watermarked = apply_watermark(image, WATERMARK_PATH)
    out_path = OUT_DIR / f"{name}_seed{seed}.png"
    watermarked.save(out_path, "PNG")
    print(f"  saved {out_path}")
    log_rows.append({"name": name, "filename": out_path.name, "seed": seed, "prompt": prompt, "status": "success"})

with open(OUT_DIR / "content_batch_log.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "filename", "seed", "prompt", "status"])
    writer.writeheader()
    writer.writerows(log_rows)

print(f"\nDONE. {len(log_rows)} images generated in {OUT_DIR}")
