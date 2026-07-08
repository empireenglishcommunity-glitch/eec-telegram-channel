"""
Generates macal_empire_generate.json — a ComfyUI API-format workflow graph.

This is NOT the same JSON format as a workflow saved from the ComfyUI web UI
("workflow export"). This is the API-submission format: a flat dict of
node_id -> {class_type, inputs}, exactly what you POST to ComfyUI's
`/prompt` endpoint. batch_runner.py loads this file, fills in the prompt
text per job, and submits it.

Graph (only core ComfyUI nodes — no custom-node class names guessed):

    CheckpointLoaderSimple (SDXL base)
            |
    LoraLoader (MACAL Empire brand LoRA, once trained)
            |
    CLIPTextEncode (positive)   CLIPTextEncode (negative)
            \\                    /
              EmptyLatentImage -> KSampler
                                     |
                                 VAEDecode
                                     |
                         UpscaleModelLoader -> ImageUpscaleWithModel (4x)
                                     |
                                 SaveImage

Watermarking is deliberately NOT done inside this ComfyUI graph — it's
applied as a Pillow post-processing step in batch_runner.py after the image
is downloaded. This is a pragmatic deviation from a "everything in one
ComfyUI graph" ideal: it avoids depending on a specific third-party
compositing node's exact class name (which varies by custom-node version and
can't be verified without a running ComfyUI instance), while still keeping
the entire pipeline fully automated end-to-end.

Usage:
    python generate_workflow.py
    # writes macal_empire_generate.json in this directory
"""
import json
import os

# ---------------------------------------------------------------------------
# Defaults — overridden per-job by batch_runner.py, but valid on their own
# so this file can also be POSTed as-is for a quick manual test.
# ---------------------------------------------------------------------------
DEFAULT_CHECKPOINT = "sd_xl_base_1.0.safetensors"
DEFAULT_LORA = "macalempire_style_sdxl.safetensors"
DEFAULT_LORA_STRENGTH = 0.8
# 0.8 rather than 1.0 per DATASET-SPEC.md Section 5.4: full strength can
# over-stylize; 0.6-1.0 is the tuning range, 0.8 is a sensible default.
DEFAULT_UPSCALE_MODEL = "RealESRGAN_x4plus.pth"
DEFAULT_NEGATIVE_PROMPT = (
    "cartoon, illustration, anime, low quality, blurry, oversaturated, "
    "watermark, text, logo, cluttered, bright daylight, pastel colors, "
    "cheap looking, plastic, low contrast"
)
DEFAULT_POSITIVE_PROMPT = (
    "macalempire style, a marble column bathed in warm golden light against "
    "a near-black background, cinematic shadow"
)


def build_workflow(
    positive_prompt: str = DEFAULT_POSITIVE_PROMPT,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    checkpoint_name: str = DEFAULT_CHECKPOINT,
    lora_name: str = DEFAULT_LORA,
    lora_strength: float = DEFAULT_LORA_STRENGTH,
    upscale_model_name: str = DEFAULT_UPSCALE_MODEL,
    seed: int = -1,
    steps: int = 30,
    cfg: float = 7.0,
    width: int = 1024,
    height: int = 1024,
    filename_prefix: str = "macal_empire",
) -> dict:
    """
    Build the ComfyUI API-format node graph as a Python dict.
    seed=-1 means "randomize" — batch_runner.py replaces this with a real
    random seed per job so results are both reproducible and logged.
    """
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": checkpoint_name},
        },
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0],
                "clip": ["1", 1],
                "lora_name": lora_name,
                "strength_model": lora_strength,
                "strength_clip": lora_strength,
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 1], "text": positive_prompt},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 1], "text": negative_prompt},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        },
        "8": {
            "class_type": "UpscaleModelLoader",
            "inputs": {"model_name": upscale_model_name},
        },
        "9": {
            "class_type": "ImageUpscaleWithModel",
            "inputs": {"upscale_model": ["8", 0], "image": ["7", 0]},
        },
        "10": {
            "class_type": "SaveImage",
            "inputs": {"images": ["9", 0], "filename_prefix": filename_prefix},
        },
    }


def main():
    workflow = build_workflow()
    out_path = os.path.join(os.path.dirname(__file__), "macal_empire_generate.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print(f"Wrote {out_path} ({len(workflow)} nodes)")


if __name__ == "__main__":
    main()
