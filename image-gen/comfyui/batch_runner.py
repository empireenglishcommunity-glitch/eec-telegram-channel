"""
MACAL Empire — ComfyUI Batch Runner.

Submits a list of prompts to a running ComfyUI instance (via its HTTP API),
waits for each job to complete, downloads the result, applies the brand
watermark, and saves organized output — the "n8n orchestration" role described
in docs/MACAL-EMPIRE-IMAGE-GEN-INFRASTRUCTURE.md Section 6, implemented here as
a standalone script so it can run directly inside a Kaggle session without
needing n8n itself (n8n integration comes later, once this is running on
always-on paid infrastructure — see the report's phased roadmap).

Two modes:
  1. Seed generation (no LoRA)  — bootstraps the training dataset (Task 2)
  2. Brand generation (with LoRA) — produces final on-brand content (after training)

------------------------------------------------------------------------------
USAGE (inside the Kaggle ComfyUI session, in a new cell or via terminal)
------------------------------------------------------------------------------

Seed generation (before any LoRA exists):
    python batch_runner.py \\
        --comfyui-url http://127.0.0.1:8188 \\
        --prompts-file ../dataset/seed_prompts_output.txt \\
        --output-dir ../dataset/raw_seed \\
        --no-lora

Brand generation (after training, LoRA copied into ComfyUI/models/loras/):
    python batch_runner.py \\
        --comfyui-url http://127.0.0.1:8188 \\
        --prompts-file my_content_prompts.txt \\
        --output-dir ../output \\
        --watermark

Generate the prompts file first with:
    python ../dataset/seed_prompts.py > seed_prompts_output.txt
------------------------------------------------------------------------------
"""
import argparse
import json
import random
import time
import urllib.request
import urllib.error
from pathlib import Path

from generate_workflow import build_workflow, DEFAULT_NEGATIVE_PROMPT

try:
    from PIL import Image
except ImportError:
    Image = None  # watermarking simply becomes unavailable; checked at runtime


def load_prompts(prompts_file: Path) -> list[str]:
    """Read one prompt per line, skipping blank lines and comment lines (#)."""
    lines = prompts_file.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def submit_job(comfyui_url: str, workflow: dict) -> str:
    """POST a workflow to ComfyUI's /prompt endpoint. Returns the prompt_id."""
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{comfyui_url}/prompt", data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_job(comfyui_url: str, prompt_id: str, timeout: int = 300, poll_interval: int = 3) -> dict:
    """
    Poll ComfyUI's /history endpoint until the job completes or times out.
    Returns the history entry for this prompt_id.
    """
    elapsed = 0
    while elapsed < timeout:
        req = urllib.request.Request(f"{comfyui_url}/history/{prompt_id}")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                history = json.loads(resp.read())
            if prompt_id in history:
                return history[prompt_id]
        except urllib.error.URLError:
            pass
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Job {prompt_id} did not complete within {timeout}s")


def download_image(comfyui_url: str, filename: str, subfolder: str, folder_type: str = "output") -> bytes:
    """Download a generated image from ComfyUI's /view endpoint."""
    params = f"filename={filename}&subfolder={subfolder}&type={folder_type}"
    req = urllib.request.Request(f"{comfyui_url}/view?{params}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()



def apply_watermark(image_bytes: bytes, watermark_path: Path) -> bytes:
    """
    Composite the brand watermark onto the bottom-right corner of the image.
    Returns new PNG bytes. Requires Pillow and an existing watermark.png
    (generate one first with make_watermark.py).
    """
    if Image is None:
        raise RuntimeError("Pillow not installed. Run: pip install pillow")
    if not watermark_path.exists():
        raise FileNotFoundError(
            f"Watermark not found at {watermark_path}. Run make_watermark.py first."
        )

    import io
    base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")

    # Scale watermark to ~30% of image width, preserving aspect ratio
    target_width = int(base.width * 0.3)
    scale = target_width / watermark.width
    watermark = watermark.resize((target_width, int(watermark.height * scale)), Image.LANCZOS)

    # Position: bottom-right with a margin proportional to image size
    margin = int(base.width * 0.03)
    position = (base.width - watermark.width - margin, base.height - watermark.height - margin)

    composited = base.copy()
    composited.alpha_composite(watermark, position)

    out = io.BytesIO()
    composited.convert("RGB").save(out, "PNG")
    return out.getvalue()


def run_batch(
    comfyui_url: str,
    prompts: list[str],
    output_dir: Path,
    use_lora: bool,
    apply_watermark_flag: bool,
    watermark_path: Path,
    negative_prompt: str,
    filename_prefix: str,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "batch_log.csv"
    log_rows = []

    print(f"Submitting {len(prompts)} jobs to {comfyui_url} ...")
    print(f"LoRA: {'ENABLED' if use_lora else 'DISABLED (seed generation mode)'}")
    print(f"Watermark: {'ON' if apply_watermark_flag else 'OFF'}")
    print()

    for i, prompt_text in enumerate(prompts, start=1):
        seed = random.randint(0, 2**32 - 1)
        workflow = build_workflow(
            positive_prompt=prompt_text,
            negative_prompt=negative_prompt,
            seed=seed,
            filename_prefix=f"{filename_prefix}_{i:04d}",
        )

        if not use_lora:
            # Seed generation mode: skip the LoRA node entirely by rewiring
            # the sampler to read directly from the checkpoint loader.
            workflow["3"]["inputs"]["clip"] = ["1", 1]
            workflow["4"]["inputs"]["clip"] = ["1", 1]
            workflow["6"]["inputs"]["model"] = ["1", 0]
            del workflow["2"]  # LoraLoader node no longer referenced

        try:
            print(f"[{i}/{len(prompts)}] Submitting: {prompt_text[:70]}...")
            prompt_id = submit_job(comfyui_url, workflow)
            history_entry = wait_for_job(comfyui_url, prompt_id)

            outputs = history_entry.get("outputs", {})
            saved = outputs.get("10", {}).get("images", [])
            if not saved:
                raise RuntimeError("No output image found in job result")

            image_info = saved[0]
            image_bytes = download_image(
                comfyui_url, image_info["filename"], image_info.get("subfolder", "")
            )

            if apply_watermark_flag:
                image_bytes = apply_watermark(image_bytes, watermark_path)

            out_filename = f"{filename_prefix}_{i:04d}_seed{seed}.png"
            out_path = output_dir / out_filename
            out_path.write_bytes(image_bytes)

            log_rows.append({
                "index": i, "filename": out_filename, "seed": seed,
                "prompt": prompt_text, "status": "success",
            })
            print(f"    -> saved {out_filename}")

        except Exception as e:
            log_rows.append({
                "index": i, "filename": "", "seed": seed,
                "prompt": prompt_text, "status": f"FAILED: {e}",
            })
            print(f"    -> FAILED: {e}")

    # Write the batch log — every job's outcome, success or failure, so
    # failed jobs can be identified and resubmitted (Section 6.3 error recovery)
    import csv
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "filename", "seed", "prompt", "status"])
        writer.writeheader()
        writer.writerows(log_rows)

    succeeded = sum(1 for r in log_rows if r["status"] == "success")
    print()
    print(f"Batch complete: {succeeded}/{len(prompts)} succeeded.")
    print(f"Log written to {log_path}")
    if succeeded < len(prompts):
        print(f"{len(prompts) - succeeded} job(s) failed — check {log_path} for details, "
              f"then resubmit just the failed prompts.")


def main():
    parser = argparse.ArgumentParser(description="MACAL Empire ComfyUI batch runner")
    parser.add_argument("--comfyui-url", default="http://127.0.0.1:8188",
                         help="ComfyUI API base URL (use the Cloudflare tunnel URL if calling from outside Kaggle)")
    parser.add_argument("--prompts-file", required=True, type=Path,
                         help="Text file with one prompt per line")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--no-lora", action="store_true",
                         help="Skip the LoRA node (use for seed/bootstrap generation before training)")
    parser.add_argument("--watermark", action="store_true",
                         help="Apply the brand watermark to outputs (use for final content, not seed generation)")
    parser.add_argument("--watermark-path", default=Path(__file__).parent / "watermark.png", type=Path)
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT)
    parser.add_argument("--filename-prefix", default="macal_empire")
    args = parser.parse_args()

    prompts = load_prompts(args.prompts_file)
    if not prompts:
        print(f"No prompts found in {args.prompts_file}")
        return

    run_batch(
        comfyui_url=args.comfyui_url,
        prompts=prompts,
        output_dir=args.output_dir,
        use_lora=not args.no_lora,
        apply_watermark_flag=args.watermark,
        watermark_path=args.watermark_path,
        negative_prompt=args.negative_prompt,
        filename_prefix=args.filename_prefix,
    )


if __name__ == "__main__":
    main()
