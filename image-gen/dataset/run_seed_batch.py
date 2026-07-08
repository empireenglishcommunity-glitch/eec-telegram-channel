"""
Runs the full seed prompt batch against a live ComfyUI instance (via its
public tunnel URL) and downloads every result into raw_seed/.

This is a standalone, dependency-light version of comfyui/batch_runner.py
built to run directly against the Kaggle tunnel from outside Kaggle (e.g.,
from this sandbox), without needing to import comfyui/generate_workflow.py
across the two separate script locations.

Usage:
    python run_seed_batch.py --comfyui-url https://YOUR-TUNNEL.trycloudflare.com
"""
import argparse
import csv
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

NEGATIVE_PROMPT = (
    "cartoon, illustration, anime, low quality, blurry, oversaturated, "
    "watermark, text, logo, cluttered, bright daylight, pastel colors, "
    "cheap looking, plastic, low contrast"
)


def build_workflow(positive_prompt: str, seed: int, filename_prefix: str) -> dict:
    """Minimal base-SDXL workflow (no LoRA, no upscale) for seed generation."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": positive_prompt},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": NEGATIVE_PROMPT},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0], "positive": ["3", 0], "negative": ["4", 0],
                "latent_image": ["5", 0], "seed": seed, "steps": 25, "cfg": 7.0,
                "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "10": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix},
        },
    }


def load_prompts(prompts_file: Path) -> list[str]:
    lines = prompts_file.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def submit_job(comfyui_url: str, workflow: dict) -> str:
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{comfyui_url}/prompt", data=payload,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["prompt_id"]


def wait_for_job(comfyui_url: str, prompt_id: str, timeout: int = 120, poll_interval: int = 2) -> dict:
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


def is_tunnel_alive(comfyui_url: str, timeout: int = 8) -> bool:
    try:
        req = urllib.request.Request(f"{comfyui_url}/system_stats")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def wait_for_tunnel_recovery(comfyui_url: str, max_wait: int = 600, check_interval: int = 10) -> bool:
    """
    When the tunnel drops, it sometimes comes back on its own within a minute
    or two (transient Cloudflare edge blip) without needing a manual restart.
    Poll for up to max_wait seconds before giving up and asking the user to
    restart Kaggle's launch cell. Returns True if it recovered on its own.
    """
    print(f"  Tunnel unreachable. Waiting up to {max_wait}s for automatic recovery "
          f"before giving up (checking every {check_interval}s)...")
    waited = 0
    while waited < max_wait:
        if is_tunnel_alive(comfyui_url):
            print(f"  Tunnel recovered on its own after {waited}s.")
            return True
        time.sleep(check_interval)
        waited += check_interval
    return False


def download_image(comfyui_url: str, filename: str, subfolder: str = "") -> bytes:
    params = f"filename={filename}&subfolder={subfolder}&type=output"
    req = urllib.request.Request(f"{comfyui_url}/view?{params}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfyui-url", required=True)
    parser.add_argument("--prompts-file", default="seed_prompts_output.txt", type=Path)
    parser.add_argument("--output-dir", default="raw_seed", type=Path)
    parser.add_argument("--start-index", type=int, default=1, help="Resume from this prompt number (1-indexed)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    prompts_file = (script_dir / args.prompts_file).resolve() if not args.prompts_file.is_absolute() else args.prompts_file
    output_dir = (script_dir / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = load_prompts(prompts_file)
    print(f"Loaded {len(prompts)} prompts from {prompts_file}")
    print(f"Output dir: {output_dir}")
    print(f"Starting at index {args.start_index}")
    print()

    log_path = output_dir / "seed_batch_log.csv"
    log_rows = []
    if log_path.exists() and args.start_index > 1:
        with open(log_path, newline="", encoding="utf-8") as f:
            log_rows = list(csv.DictReader(f))

    consecutive_tunnel_failures = 0

    for i, prompt_text in enumerate(prompts, start=1):
        if i < args.start_index:
            continue

        seed = 1000 + i  # deterministic per-index seed, reproducible and log-friendly
        prefix = f"seed_{i:03d}"
        workflow = build_workflow(prompt_text, seed, prefix)

        # Before submitting, check the tunnel is alive. If not, wait for it to
        # recover on its own rather than immediately failing and burning a
        # retry-cycle with the user.
        if not is_tunnel_alive(args.comfyui_url):
            recovered = wait_for_tunnel_recovery(args.comfyui_url)
            if not recovered:
                print()
                print("=" * 70)
                print("TUNNEL DOWN — did not recover automatically within the wait window.")
                print(f"Resume with: --start-index {i}  (once you have a fresh tunnel URL)")
                print("=" * 70)
                break

        max_attempts = 2
        last_error = None
        succeeded = False

        for attempt in range(1, max_attempts + 1):
            try:
                suffix = "" if attempt == 1 else f" (retry {attempt}/{max_attempts})"
                print(f"[{i}/{len(prompts)}] Submitting{suffix}: {prompt_text[:80]}...")
                prompt_id = submit_job(args.comfyui_url, workflow)
                history_entry = wait_for_job(args.comfyui_url, prompt_id)

                outputs = history_entry.get("outputs", {})
                saved = outputs.get("10", {}).get("images", [])
                if not saved:
                    raise RuntimeError("No output image in job result")

                image_info = saved[0]
                image_bytes = download_image(args.comfyui_url, image_info["filename"], image_info.get("subfolder", ""))

                out_filename = f"{prefix}.png"
                (output_dir / out_filename).write_bytes(image_bytes)

                log_rows.append({"index": i, "filename": out_filename, "seed": seed, "prompt": prompt_text, "status": "success"})
                print(f"    -> saved {out_filename} ({len(image_bytes)} bytes)")
                succeeded = True
                break

            except Exception as e:
                last_error = e
                print(f"    -> attempt {attempt} failed: {e}")
                if attempt < max_attempts:
                    # Brief pause + tunnel health check before retrying the same prompt
                    time.sleep(3)
                    if not is_tunnel_alive(args.comfyui_url):
                        wait_for_tunnel_recovery(args.comfyui_url, max_wait=120)

        if not succeeded:
            log_rows.append({"index": i, "filename": "", "seed": seed, "prompt": prompt_text, "status": f"FAILED: {last_error}"})
            print(f"    -> giving up on index {i} after {max_attempts} attempts")

        # Write the log after every job so progress is never lost if this
        # script is interrupted partway through.
        with open(log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["index", "filename", "seed", "prompt", "status"])
            writer.writeheader()
            writer.writerows(log_rows)

    succeeded = sum(1 for r in log_rows if r["status"] == "success")
    print()
    print(f"Batch complete: {succeeded}/{len(log_rows)} succeeded.")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()
