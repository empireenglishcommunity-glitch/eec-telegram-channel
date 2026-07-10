import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

MODEL = "/kaggle/working/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors"
LORA = "/kaggle/working/macal_empire_lora_output/macalempire_style_sdxl.safetensors"
OUT_DIR = "/kaggle/working/final_inference_test"

import os
os.makedirs(OUT_DIR, exist_ok=True)

print("Loading base pipeline from single file...")
pipe = StableDiffusionXLPipeline.from_single_file(
    MODEL, torch_dtype=torch.float16, use_safetensors=True
).to("cuda")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)

print("Loading LoRA weights...")
pipe.load_lora_weights(LORA)
pipe.fuse_lora(lora_scale=1.0)

NEGATIVE = (
    "cartoon, illustration, anime, low quality, blurry, oversaturated, "
    "watermark, text, logo, cluttered, bright daylight, pastel colors, "
    "cheap looking, plastic, low contrast, white background, light background"
)

prompts = [
    ("columns", "macalempire style, grand imperial columns bathed in warm golden light, deep shadow, cinematic, dark near-black background, moody low-key lighting, imperial luxury aesthetic"),
    ("staircase", "macalempire style, a spiral staircase in black marble with a gold handrail, dramatic overhead light, dark near-black background, moody low-key lighting, imperial luxury aesthetic"),
    ("silhouette", "macalempire style, portrait of a person in silhouette, rim-lit in gold against a dark imperial hallway, dark near-black background, moody low-key lighting, imperial luxury aesthetic"),
]

for name, prompt in prompts:
    print(f"Generating: {name}")
    image = pipe(
        prompt=prompt,
        negative_prompt=NEGATIVE,
        num_inference_steps=30,
        guidance_scale=7.0,
        width=1024,
        height=1024,
        generator=torch.Generator("cuda").manual_seed(42),
    ).images[0]
    image.save(f"{OUT_DIR}/{name}.png")
    print(f"  saved {OUT_DIR}/{name}.png")

print("DONE")
