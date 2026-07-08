# MACAL Empire — Self-Hosted AI Image Generation Infrastructure
## Technical Research Report & Implementation Plan

> **Prepared for:** Empire English Community (EEC) — MACAL Empire brand visual system
> **Prepared by:** Kiro (AI Infrastructure Architecture research)
> **Date:** July 8, 2026
> **Status:** DRAFT FOR REVIEW — no implementation started yet
> **Scope:** Fully self-hosted, high-volume, cinematic-quality image generation for MACAL Empire brand identity (Dark Luxury / Imperial / Cinematic)

---

## 0. How to Use This Document

This is a decision-support document, not a build log. Nothing described here has been
implemented. Read top-to-bottom, then go to **Section 11 (Final Recommendations)** and
**Section 12 (Immediate Next Steps)** to approve a direction before any infrastructure
is provisioned or money is spent.



---

## 1. Executive Summary

**The core finding: your current infrastructure has zero GPU capacity.** The only
server in production (Hetzner VPS 77.42.43.250, running the Telegram bot, n8n, and
Kokoro TTS) is CPU-only. Today's channel images are generated via **Cloudflare
Workers AI (FLUX.1 Schnell)** — a free, serverless, *rented* API, not a self-hosted
model. This is the opposite of the goal stated in this brief (full ownership,
no per-image paid APIs).

Building the MACAL Empire visual system as described requires **new infrastructure**,
not a repurposing of what exists. That's not a blocker — it's a clean slate, and this
report is written to get from zero to a production-grade, self-owned pipeline with
the least wasted money and the fewest dead ends.

**Recommended direction in one paragraph:** Rent a 24GB-VRAM GPU (RunPod or Vast.ai)
for 2-4 weeks to develop and validate the pipeline and train the first
brand LoRA — do not buy hardware yet. Run **ComfyUI in API mode** as the generation
engine, with **FLUX.1 [dev]** as the primary model for hero/cinematic brand shots and
**SDXL 1.0** as a secondary fast/high-volume model with deep LoRA/ControlNet support.
Train a **MACAL Empire style LoRA** (40-80 curated images) using **Kohya SS** or
**AI-Toolkit**. Orchestrate everything through the **n8n instance you already run** —
do not adopt a new orchestration stack. Chain upscaling, watermarking, and file
management as ComfyUI nodes in the same workflow graph. Once volume and usage
patterns are proven on rented hardware, convert to owned hardware (RTX 4090, or a
Hetzner GEX44 dedicated server) for the best long-term cost-per-image.

**Estimated one-time cost range:** $0 (rental-only, ongoing opex) up to ~$2,200
(owned RTX 4090 + peripherals) once you commit to permanent hardware. Recommended
starting monthly opex during validation: **$50-150/month** (rented GPU, ~100-300
hours of usage).

**Can't spend anything right now? You don't have to.** Section 2.5 covers a true
**$0 path**: train the brand LoRA and run manual generation batches on free Kaggle
GPU sessions (30 hrs/week, no credit card). The only thing this can't do is run
fully automated and unattended — that's the one piece that requires paid, always-on
compute. Everything else in this report can be prototyped for free first.

---

## 2. Research Findings & Server Capability Assessment

### 2.1 Current Infrastructure (as documented in this repo)

| Component | Current State |
|---|---|
| Server | Hetzner VPS, 77.42.43.250, `/opt/eec-channel-bot/` |
| GPU | **None.** No GPU is provisioned, mentioned, or available on this server. |
| Role today | Telethon bot (Telegram automation), n8n (workflow engine), Kokoro TTS (voice, stopped between uses to save RAM) |
| Current image generation | Cloudflare Workers AI, FLUX.1 Schnell, serverless, free tier (10,000 neurons/day) — see `docs/06-AUTOMATION-ENGINE.md` and `docs/05-DECISIONS.md` decision #27 |
| Implication | The existing server **cannot** run SDXL or FLUX locally — there is no CUDA-capable GPU. Standard Hetzner Cloud VPS instances are CPU + RAM only; GPU is a separate dedicated server product line (see 2.2). |

**Conclusion: this is a greenfield GPU build.** Nothing needs to be migrated away
from — the current Cloudflare-based system can keep running the Telegram channel's
day-to-day content while the new MACAL Empire pipeline is built in parallel, then
cut over when ready. Zero risk to the live bot during this build.

### 2.2 What "enough hardware" actually means for this workload

For SDXL and FLUX.1 inference plus LoRA training, the deciding factor is **VRAM**,
not CPU or general RAM (though 32GB+ system RAM and NVMe storage are recommended
supporting specs). Rough VRAM requirements:

| Task | Minimum VRAM | Comfortable VRAM |
|---|---|---|
| SDXL inference | 8 GB | 12 GB+ |
| FLUX.1 [schnell] inference (distilled, 4-step) | ~12 GB | 16 GB |
| FLUX.1 [dev] inference, quantized (fp8/GGUF) | 12-16 GB | 16-24 GB |
| FLUX.1 [dev] inference, full fp16 | 24 GB | 24 GB+ |
| SDXL LoRA training (Kohya SS, fused backward pass, 2025+) | ~10 GB | 16-24 GB |
| FLUX.1 LoRA training | 16 GB | 24 GB |
| 4K tiled upscaling (ControlNet tile) | 8-12 GB (tiled, resolution-independent) | 16 GB+ |

Sources: [SDXL vs FLUX local VRAM comparison](https://localaimaster.com/blog/sdxl-vs-flux-local),
[Kohya SS fused backward pass VRAM reduction](https://sanj.dev/post/lora-training-2025-ultimate-guide/),
[FLUX Schnell VRAM ~12GB](https://techsifted.hashnode.dev/flux-vs-stable-diffusion-open-source-ai-image-battle).

**Bottom line: a 24GB card is the sweet spot.** It runs SDXL and FLUX.1 [dev]
comfortably at full precision, trains LoRAs for both without workarounds, and has
headroom for 4K upscaling passes. Anything below 16GB forces permanent compromises
(quantized models only, smaller batch sizes, slower training). Anything above 24GB
(e.g., 48GB+ professional cards) is not needed for this brand's volume and adds cost
without proportional benefit — reserve that tier only if you later train
FLUX-full-parameter fine-tunes (not LoRAs) or run multiple concurrent GPU workers on
one card via slicing.

### 2.3 Hardware options compared

| Option | VRAM | Cost | Speed (SDXL/FLUX, relative) | Ownership | Best for |
|---|---|---|---|---|---|
| **RunPod / Vast.ai rented RTX 4090** | 24 GB | $0.34-0.69/hr (~$50-100/mo at moderate use) | Fastest consumer tier | None (rental) | Validation phase, LoRA training bursts, spiky/unpredictable volume |
| **RunPod rented A6000** | 48 GB | ~$0.89/hr | Similar to 4090 for this workload, more VRAM headroom | None (rental) | If you want training headroom without buying hardware |
| **Hetzner GEX44 (dedicated)** | 20 GB (RTX 4000 SFF Ada) | €184/mo + €79 one-time setup | Good for inference; tight for full-precision FLUX training | Rented dedicated server, same provider as existing bot | Predictable-cost inference workhorse, same-ecosystem ops simplicity |
| **Hetzner GEX131 (dedicated)** | 96 GB (RTX PRO 6000 Blackwell Max-Q) | €889/mo | Massive headroom, overkill for LoRA-only workloads | Rented dedicated server | Only justified if training full fine-tunes or running heavy concurrent load |
| **Purchased RTX 4090 (24GB), colocated or on-prem** | 24 GB | ~$1,600-2,000 one-time (used market has tightened; new is the safer buy) | Fastest consumer card | Fully owned | Long-term lowest cost-per-image once volume is proven |
| **Purchased used RTX 3090 (24GB)** | 24 GB | ~$700-1,050 one-time | ~30-46% slower than 4090, same VRAM ceiling | Fully owned | Best value-per-VRAM-dollar; ideal budget-conscious permanent option |

Sources: [Hetzner GEX44 official page](https://www.hetzner.com/dedicated-rootserver/gex44/),
[Hetzner GEX131 official page](https://www.hetzner.com/dedicated-rootserver/gex131/),
[Hetzner GPU server pricing announcement](https://www.hetzner.com/pressroom/new-gpu-server/),
[RTX 4090 vs 3090 benchmarks](https://www.trooper.ai/benchmarks-compare-RTX-4090-with-RTX-3090),
[RTX 4090 vs 3090 2026 pricing](https://cdn.localaimaster.com/blog/rtx-4090-vs-3090-local-ai),
[RunPod/Vast.ai pricing 2026](https://blog.clore.ai/gpu-cloud-pricing-comparison/),
[RunPod RTX 4090 community pricing](https://www.spheron.network/blog/vastai-alternatives).

### 2.4 Hardware recommendation

**Do not buy hardware yet.** Rent first, buy once volume is proven:

1. **Phase 1 (Validation, 2-4 weeks):** Rent an RTX 4090 or A6000 on RunPod
   ($50-150 total for the validation window). Stand up ComfyUI, test FLUX.1 [dev]
   and SDXL, train the first MACAL Empire brand LoRA, build the automation
   pipeline end-to-end. This proves the workflow with zero capex risk.
2. **Phase 2 (Production decision):** Once you know your actual monthly image
   volume, choose between:
   - **Hetzner GEX44** (€184/mo) if you want to stay inside your current provider's
     ecosystem and prefer predictable opex over capex, OR
   - **Purchase an RTX 4090** (~$1,600-2,000 one-time, then only pay for
     colocation/hosting or run it on a home/office machine with a static IP + VPN
     tunnel to the existing Hetzner box) for the lowest long-term cost-per-image, OR
   - **Purchase a used RTX 3090** (~$700-1,050) as the most budget-conscious owned
     option — 30-46% slower, but 24GB VRAM parity with the 4090 for a third of the
     price.

This phased approach avoids the single biggest risk in this kind of project:
spending $1,600-2,000+ upfront on hardware before confirming the model choice,
workflow, and brand LoRA actually produce the desired "Dark Luxury / Imperial /
Cinematic" look.

### 2.5 Zero-Budget Path — Start Here If You Cannot Spend Anything Right Now

**Be direct about what's actually true: a fully automated, always-on, 24/7 pipeline
cannot be $0** — some GPU has to be running continuously, and continuous compute
always costs something, even at the cheapest rented tier (~$50-150/month, Section 2.3).
There is no way around this for an unattended production system.

**But the two most valuable early steps — training the brand LoRA and generating
image batches — CAN be done at $0**, using free-tier GPU platforms. The tradeoff is
that it becomes a *manual, session-based* workflow instead of an automated one.

#### Free GPU platform comparison

| Platform | Free GPU | Weekly quota | Session limit | ComfyUI support |
|---|---|---|---|---|
| **Kaggle** | Tesla T4 or P100 (16GB VRAM) | ~30 hours/week, resets weekly | ~9-12 hours, 60-min idle timeout | Works — run ComfyUI as a background process in a notebook cell with a tunnel (e.g., Cloudflare Tunnel, ngrok) for web UI access |
| **Google Colab (free)** | T4 (variable availability, not guaranteed), 15GB VRAM | No fixed weekly quota, but usage-based throttling if overused | ~12 hours, frequent disconnects, lower priority than paid tiers | Works — several maintained "ComfyUI on Colab" notebooks exist. **Note: AUTOMATIC1111 is explicitly blocked on Colab's free tier — use ComfyUI instead, which is unaffected.** |

Sources: [Kaggle GPU usage docs — 30 hrs/week quota](https://www.kaggle.com/docs/efficient-gpu-usage),
[Free GPU access guide 2026 — Colab vs Kaggle hours/session limits](https://www.gmicloud.ai/en/blog/best-free-gpu-cloud-options-for-ai-startups-and-researchers),
[Kaggle LoRA fine-tuning — 30 hrs/week T4 confirmed sufficient](http://huggingface.co/spaces/joehiggi/g-gen/raw/main/docs/finetune-on-kaggle.md),
[Colab blocks AUTOMATIC1111 on free tier](https://stable-diffusion-art.com/automatic1111-colab),
[Run ComfyUI on Google Colab — confirmed working on free T4](https://stable-diffusion-art.com/comfyui-colab/),
[ComfyUI-On-Colab GitHub project](https://github.com/nazdridoy/ComfyUI-On-Colab).

**Recommendation for the zero-budget path: use Kaggle, not Colab, as the primary
free platform.** Kaggle's 30 hrs/week is a guaranteed quota (not "if capacity
allows" like Colab), and its GPU allocation has historically been more reliable.
Colab is a reasonable backup or supplement when Kaggle's weekly quota runs out.

#### What this looks like in practice

| Step | Zero-budget approach |
|---|---|
| Train the MACAL Empire brand LoRA | Run Kohya SS or AI-Toolkit inside a Kaggle notebook. A style LoRA (Section 5) takes 1-3 hours of GPU time — comfortably inside one Kaggle session, well inside the 30 hrs/week quota. **One-time cost: $0**, just your time to set it up. |
| Generate a batch of brand images | Run ComfyUI inside a Kaggle or Colab notebook (with a tunnel for the web UI, or drive it via the API from a local script). Load your trained LoRA + FLUX/SDXL, submit a batch of prompts, download the results before the session ends. |
| Post-processing (upscale, watermark) | Same ComfyUI session — chain the same nodes described in Section 6.4. Nothing extra needed. |
| Ongoing content needs | Repeat the batch-generation session whenever you need new images — e.g., once a week, aligned with your existing weekly content calendar. This becomes a manual "content generation day" instead of an automated background job. |
| What you give up vs. the paid path | No 24/7 automation (no n8n auto-triggering jobs while you sleep), sessions can disconnect mid-run (plan for shorter batches, ~10-20 images at a time), no guaranteed instant availability (Colab especially can queue you for a GPU during peak hours) |

#### When to graduate off the free tier

Move to a paid rented GPU (Section 2.3) once **any** of these becomes true:
- You need more than ~30 hours of GPU time in a given week (Kaggle's ceiling)
- You want the pipeline to run unattended (n8n-triggered, no one at the keyboard)
- Session disconnects are costing you more time/frustration than $50-150/month is
  worth
- You're ready to commit to the brand LoRA and want training/generation to be
  instant rather than session-scheduled

**Bottom line: yes, you can start today for $0.** Train the LoRA on Kaggle this
week, run your first manual batch, and see the MACAL Empire look before spending
a single dollar. The paid infrastructure in the rest of this report is what turns
that proven workflow into something automated — it's an upgrade you make once
you've validated the creative direction for free, not a prerequisite to getting
started.



---

## 3. Core Model Selection

### 3.1 Comparative analysis

| Criterion | FLUX.1 [dev] | SDXL 1.0 | FLUX.1 [schnell] |
|---|---|---|---|
| Human realism | Best-in-class among open models | Very good, needs realism-tuned checkpoints (e.g., Juggernaut, RealVisXL) to match FLUX | Good, slightly behind [dev] |
| Facial consistency (with LoRA) | Excellent | Excellent — largest LoRA ecosystem for faces/characters | Good |
| Detail quality | Excellent, especially skin/fabric/lighting | Good, checkpoint-dependent | Good, some detail loss from distillation |
| Prompt adherence | Best of the three — handles complex, multi-clause prompts and in-image text well | Moderate — often needs prompt engineering / negative prompts | Best speed/adherence tradeoff |
| Composition / cinematic rendering | Excellent — natively favors photographic, cinematic lighting | Good, style-dependent on checkpoint | Good |
| Generation speed (24GB card, 1024px) | ~45-60s (full dev) / ~15-20s (schnell-distilled) | Fastest: ~13s | Fastest of the FLUX family: ~13-19s |
| VRAM requirement | 16-24 GB (12-16GB quantized) | 8 GB minimum, 12GB+ comfortable | ~12 GB |
| Community/LoRA ecosystem | Growing fast, catching up | **Largest by far** — thousands of LoRAs/ControlNets on CivitAI | Smaller, shares some FLUX-dev LoRAs |
| License | Non-commercial for [dev] weights (commercial use requires a license from Black Forest Labs) — verify current terms before commercial deployment | Fully open, commercial-use permitted | Apache 2.0, commercial-use permitted |
| Future sustainability | Actively developed (Black Forest Labs), rapid ecosystem growth | Mature, stable, less cutting-edge development but rock-solid tooling | Actively developed, positioned as the "fast" tier of FLUX |

Sources: [Best Local AI Image Models 2026](https://localaimaster.com/blog/best-local-image-models-compared),
[SDXL vs FLUX VRAM/quality comparison](https://localaimaster.com/blog/sdxl-vs-flux-local),
[Flux vs SDXL Quality/Speed/Hardware](https://pxz.ai/blog/flux-vs-sdxl),
[Open-Source AI Image Battle — VRAM specifics](https://techsifted.hashnode.dev/flux-vs-stable-diffusion-open-source-ai-image-battle),
[Flux vs SDXL vs Midjourney 2025](https://apatero.com/blog/flux-vs-sdxl-vs-midjourney-comparison-2025).

> ⚠️ **License flag for legal review:** FLUX.1 [dev] weights are distributed under a
> non-commercial license by Black Forest Labs as of the sources reviewed. If MACAL
> Empire images generated with [dev] are used in paid marketing, ads, or product
> assets, verify current licensing terms directly on Black Forest Labs' site, or use
> FLUX.1 [schnell] (Apache 2.0, commercial-safe) / SDXL (fully open) for anything
> customer-facing until this is confirmed. This is the single most important
> non-technical risk in this entire report — it costs nothing to check and can be
> expensive to get wrong.

### 3.2 Recommendation: dual-model approach

Run **both** models rather than choosing one — they serve different jobs in the same
brand pipeline:

- **FLUX.1 [dev]** (or [schnell] pending the license check above) — primary model
  for **hero content**: cinematic brand images, campaign visuals, anything where
  photorealism and lighting quality matter most and volume is low (a handful of
  images per campaign/week).
- **SDXL 1.0 + realism checkpoint** (e.g., RealVisXL, Juggernaut XL) — secondary
  model for **high-volume, fast-turnaround** content: daily/social assets, variations,
  A/B testing compositions, anything needing the deep LoRA/ControlNet ecosystem for
  precise pose/composition control.

Both models can share the same brand LoRA training pipeline conceptually, but LoRAs
are architecture-specific — you will train **one LoRA per base model** (see Section 5).



---

## 4. Workflow & User Interface Selection

### 4.1 Comparative analysis

| Criterion | ComfyUI | AUTOMATIC1111 / Forge | Fooocus |
|---|---|---|---|
| Automation capability | **Native** — node graphs export as JSON and run headlessly via REST/WebSocket API | Has an API mode (`--api`) but bolted-on, less flexible | Minimal — designed for manual/interactive use only |
| Pipeline flexibility | Highest — every step (load model, sample, upscale, watermark, save) is an editable node | Extension-dependent, less composable | Very limited, opinionated presets |
| Batch processing | Strong — queue system + Python/JSON scripting for 1000+ image runs | Possible via scripts, less native | Basic |
| Scalability (multi-worker/production) | Designed for it — documented patterns for Redis/Celery queue + multiple GPU workers behind a gateway | Not designed for this; requires significant custom engineering | Not viable |
| Ease of maintenance | Moderate learning curve, but stable and modular (custom nodes are isolated) | Simple to start, but extension conflicts are a known pain point | Easiest, but you can't grow into anything more advanced |
| Performance | **10-30% faster, ~14% less VRAM** than A1111 on the same hardware (2026 benchmark) | Solid but consistently behind ComfyUI on efficiency | Comparable to A1111 under the hood (it's built on it) |
| New model support | Gets FLUX and other cutting-edge releases **first** | Lags behind ComfyUI for new architectures | Lags further behind |
| API support | REST + WebSocket, well documented, large community tooling (n8n nodes exist — see Section 6) | REST API exists but community tooling is thinner | None meaningful |
| Suitability for production | **Yes — this is the standard choice for production image pipelines in 2025-2026** | No — built for interactive single-user sessions | No |

Sources: [ComfyUI vs AUTOMATIC1111 2025](https://apatero.com/blog/comfyui-vs-automatic1111-comparison-2025),
[ComfyUI 10-30% faster, 14% less VRAM benchmark](https://appscribed.com/automatic1111-vs-comfyui/),
[ComfyUI vs A1111 vs Fooocus](https://droid4x.com/comfyui-vs-automatic1111-vs-fooocus-comparison/),
[ComfyUI Production Architecture](https://markaicode.com/architecture/comfyui-production-system-design-architecture/),
[ComfyUI Batch Processing 1000+ images](https://apatero.com/blog/comfyui-batch-processing-1000-images-automation-2026).

### 4.2 Recommendation

**ComfyUI, run in API/headless mode, is the correct choice with no serious
competitor for this use case.** It is the only one of the three built to be
automated, scaled, and integrated into a larger pipeline rather than used as a
manual creative tool. The node-graph model also maps directly onto the brand
pipeline requirement: *generate → apply brand LoRA → upscale to 4K → watermark →
frame → save with metadata* is naturally expressed as one ComfyUI workflow graph,
executed via API call per job.



---

## 5. Brand Identity Locking — LoRA Training Strategy

**Goal:** train a LoRA (or a small family of LoRAs) that makes the MACAL Empire
aesthetic — Dark Luxury, Imperial, cinematic lighting, premium realism, elegant
minimalism — the *default* output, without re-typing a long style description in
every prompt.

### 5.1 What kind of LoRA this is

This is a **style LoRA**, not a **character/face LoRA**. That distinction changes
the dataset strategy significantly:

- A character LoRA needs 15-30 images *of the same subject* from varied angles.
- A **style LoRA** needs 40-80 images that all share the same *visual language*
  (color palette, lighting, materials, composition, mood) but can depict **different
  subjects/scenes** — e.g., a portrait, a product shot, an architectural interior,
  an abstract textile close-up — all rendered in the MACAL Empire dark-luxury style.

If MACAL Empire also has a recurring visual mascot/character (a specific emperor
figure, logo mark, or consistent human model), train a **second, separate LoRA**
for that subject and combine both LoRAs at inference time (ComfyUI supports
stacking multiple LoRAs with independent weights).

### 5.2 Dataset collection methodology

| Step | Recommendation |
|---|---|
| Size | **40-80 images** for the style LoRA (character LoRA, if needed separately: 15-30 images) |
| Sourcing | Commission/curate original photography or high-end stock (dark luxury interiors, gold/black textures, cinematic portraiture) — avoid low-resolution scraped images; licensing matters if this brand will be public-facing |
| Resolution | 1024×1024 minimum per image (matches SDXL/FLUX native training resolution); higher source resolution is fine, the training tool will center-crop/bucket automatically |
| Variety within consistency | Vary subject, framing, and composition; keep lighting mood, color grade, and material palette (black, gold, deep jewel tones, marble, velvet) constant — this is what teaches the model "style" rather than "one specific scene" |
| Cleaning | Remove watermarks, logos, low-quality/blurry images, and anything with an inconsistent aesthetic before captioning |
| Captioning | Use detailed, consistent captions with a fixed **trigger word** (e.g., `macalempire style`) at the start of every caption, followed by a natural-language description of what's actually in that specific image (subject, lighting, composition) — do **not** re-describe the style itself in every caption, since that's what the LoRA is meant to learn implicitly |
| Tagging tools | BLIP or WD14 auto-captioning inside Kohya SS / AI-Toolkit as a first pass, then **manually correct every caption** — auto-captions are a time-saver, not a substitute for review |

Sources: [Flux LoRA Dataset Preparation](https://apatero.com/blog/flux-lora-dataset-preparation-complete-guide-2025),
[Ultimate Guide to LoRA Training 2025](https://apatero.com/blog/ultimate-guide-lora-training-2025),
[Train Cartoon/Style LoRA Guide](https://www.apatero.com/blog/train-cartoon-lora-complete-guide-2025).

### 5.3 Training workflow & tools

| Component | Recommendation |
|---|---|
| Primary tool | **Kohya SS (sd-scripts + bmaltais GUI)** — the standard for SDXL and FLUX.1 LoRA training; v0.9+ (Jan 2025) introduced a *fused backward pass* that cut VRAM needs roughly in half |
| Alternative tool | **AI-Toolkit (Ostris)** — actively used and recommended specifically for FLUX LoRA training, slightly more modern UX |
| LoRA rank | 16-32 for FLUX.1, 32-64 for SDXL |
| Learning rate | ~1e-4 as a starting point (both tools ship sensible defaults; adjust based on sample-image checkpoints during training) |
| Training steps | 1,500-2,000 steps is a reasonable range for a style LoRA at this dataset size |
| Hardware/time | 1-3 hours per LoRA on a 24GB card (RTX 3090/4090 class) |
| Validation | Generate sample images from checkpoints every 200-300 steps; stop training once outputs look consistently "on-brand" without artifacting — more steps is not automatically better (overfitting risk) |

Sources: [LoRA Training Guide 2026 — Kohya SS, VRAM optimization](https://sanj.dev/post/lora-training-2025-ultimate-guide/),
[Train Image LoRA Locally 2026](https://localaimaster.com/blog/image-lora-training-local-guide),
[Flux 2 LoRA Training Guide](http://apatero.com/blog/flux-2-lora-training-complete-guide-2025).

### 5.4 Best practices specific to a *brand* LoRA (vs. a hobbyist character LoRA)

1. **Lock the trigger word early and document it** — e.g., `macalempire style` — and
   never change it once production prompts depend on it.
2. **Train one LoRA per base model** (a FLUX LoRA and an SDXL LoRA), since weights
   are architecture-specific.
3. **Re-train periodically as the brand evolves**, not once-and-forget. Budget for
   a retrain (~1-3 hours of GPU time) whenever the art direction shifts meaningfully.
4. **Keep the curated dataset under version control** (see Section 6) — it's the
   single most valuable asset in this entire system, more valuable than any specific
   trained LoRA file, because it lets you retrain/improve indefinitely.
5. **Test LoRA weight (strength) at inference time**, typically 0.6-1.0 — a style
   LoRA at full strength can sometimes over-stylize; this is a per-prompt tuning
   knob, not a training-time decision.



---

## 6. Automated Production Pipeline

### 6.1 The key architectural decision: reuse n8n, don't adopt a new orchestrator

Production ComfyUI deployments are typically described in the industry as needing a
REST API gateway + a task queue (Redis/Celery or RabbitMQ) to decouple incoming
requests from GPU workers, preventing out-of-memory crashes and cutting idle GPU
time by as much as 40%. **However, your organization already runs n8n as a
self-hosted workflow engine** (documented in `docs/06-AUTOMATION-ENGINE.md`), and
mature community integrations already exist connecting n8n directly to ComfyUI's
API (`n8n-nodes-comfyui`, `n8n-nodes-comfyui-toolkit`, and documented patterns for
n8n + ComfyUI running on Vast.ai/RunPod).

**Recommendation: use n8n as the orchestration layer instead of introducing
Celery/RabbitMQ.** This avoids adding a new piece of infrastructure your team has
to learn and maintain, and directly reuses proven, already-running tooling. Revisit
this decision only if/when volume grows large enough that n8n's queueing becomes a
bottleneck (a "good problem to have" that's easy to solve later by adding Redis in
front of the ComfyUI API at that point).

Sources: [ComfyUI Production Architecture — queue patterns](https://markaicode.com/architecture/comfyui-production-system-design-architecture/),
[n8n + ComfyUI integration guide](https://growwstacks.com/blog/how-n8n-connects-to-comfyui-automating-ai-workflows/),
[n8n-nodes-comfyui GitHub](https://github.com/mason276752/n8n-nodes-comfyui),
[n8n-comfyui-integration on Vast.ai](https://github.com/enemy100/n8n-comfyui-integration).

### 6.2 End-to-end pipeline design

```
[Prompt/content idea input]
        │  (n8n: Google Sheet, Airtable, or simple JSON queue file)
        ▼
[n8n workflow trigger] ──► [ComfyUI REST API call]
        │                          │
        │                          ▼
        │                 [ComfyUI workflow graph runs on GPU worker]
        │                    1. Load base model (FLUX.1 [dev] or SDXL)
        │                    2. Apply MACAL Empire brand LoRA
        │                    3. Sample/generate at base resolution
        │                    4. Tiled 4K upscale node
        │                    5. Watermark/frame overlay node
        │                    6. Save with structured filename + metadata
        │                          │
        ◄──────────────────────────┘
        ▼
[n8n receives completion webhook/poll result]
        │
        ▼
[Organize output: move to dated/campaign folder, log to sheet, notify Telegram/Slack]
```

### 6.3 Batch generation, queue management, and error recovery

| Requirement | How it's satisfied |
|---|---|
| Receive large batches of prompts | n8n reads a queue source (spreadsheet row, JSON list, or webhook) and iterates, submitting one ComfyUI API job per prompt |
| Process sequentially / respect GPU limits | ComfyUI's built-in queue naturally serializes jobs on a single GPU; n8n's "Split in Batches" node controls submission pacing |
| Generate automatically in the background | ComfyUI API mode + n8n scheduled/triggered workflows require no manual UI interaction once configured |
| Save into organized folders | Final ComfyUI "Save Image" node writes to a structured path (e.g., `/output/{campaign}/{date}/{seed}.png`); n8n can additionally copy/sort post-generation |
| Error recovery | n8n's native error-workflow feature retries or alerts on failed HTTP calls to ComfyUI (e.g., OOM, model load failure); log every failure with the prompt + seed so it can be resubmitted |
| Logging | n8n execution history provides a built-in audit log; optionally append a row to a tracking sheet per generated image (prompt, seed, model, LoRA weight, output path, timestamp) |
| Scheduling | n8n's cron trigger can run scheduled batch jobs (e.g., "generate this week's content batch every Sunday night") exactly like the existing Telegram posting schedule already does |

### 6.4 Post-processing: yes, all of it can be automated in the same pipeline

| Task | Implementation |
|---|---|
| 4K upscaling | ComfyUI tiled upscale (ControlNet Tile or a dedicated upscale model node such as ComfyUI_SuperScaler) chained directly after generation — no separate tool needed |
| Brand watermark | A ComfyUI "Image Composite"/overlay node applies a pre-made transparent PNG watermark at a fixed position — trivial to template once |
| Predefined frame | Same technique as watermark — an overlay/border asset composited in the same node chain |
| File naming | ComfyUI's Save Image node supports templated filenames (date, seed, prompt hash); n8n can rename/move afterward if a different convention is needed |
| Folder organization | Handled by either the ComfyUI save path template or an n8n step immediately after generation |
| Metadata handling | ComfyUI embeds generation metadata (prompt, seed, model, LoRA) into PNG info by default — useful for reproducibility and audit; n8n can also log this to an external sheet/database |

Sources: [ComfyUI 4K Upscale Workflow docs](https://docs.comfy.org/tutorials/basic/upscale),
[ComfyUI Upscaling Handbook](https://blog.comfy.org/p/upscaling-in-comfyui),
[ComfyUI_SuperScaler custom node](https://comfyai.run/custom_node/ComfyUI_SuperScaler),
[ComfyUI 4K tiled upscale workflow](https://lilys.ai/en/notes/d5-render-20260219/comfyui-4k-upscale-workflow).

**Conclusion: no separate post-processing tool (e.g., ChaiNNer, Photoshop scripting)
is required.** Everything from generation through 4K delivery can live in a single
ComfyUI workflow graph, triggered and monitored by n8n.



---

## 7. Recommended Technology Stack

| Layer | Recommendation | Justification |
|---|---|---|
| GPU compute | RunPod (validation) → Hetzner GEX44 or owned RTX 4090/3090 (production) | Zero-capex validation, then lowest cost-per-image once volume is known (Section 2) |
| Core generation engine | ComfyUI (API mode, Dockerized) | Fastest, most VRAM-efficient, most automatable option (Section 4) |
| Primary model — quality tier | FLUX.1 [dev] *(pending commercial license confirmation)* or [schnell] | Best prompt adherence + cinematic realism for hero brand content (Section 3) |
| Primary model — volume tier | SDXL 1.0 + realism checkpoint (e.g., RealVisXL) | Fastest, cheapest, deepest LoRA/ControlNet ecosystem for daily content (Section 3) |
| Brand identity layer | Custom-trained MACAL Empire style LoRA (one per base model) | Locks in Dark Luxury/Imperial aesthetic without prompt repetition (Section 5) |
| LoRA training tool | Kohya SS (sd-scripts + GUI) — AI-Toolkit as alternative for FLUX | Industry-standard, actively maintained, VRAM-optimized as of 2025 (Section 5) |
| Orchestration / automation | **n8n (already self-hosted)** | Reuses existing infrastructure and skills; avoids introducing Celery/RabbitMQ prematurely (Section 6) |
| Post-processing (upscale, watermark, frame) | Native ComfyUI nodes (tiled upscale, image composite/overlay) | Keeps the entire pipeline in one workflow graph, no extra tools (Section 6) |
| File/metadata handling | ComfyUI Save Image node (templated paths, embedded PNG metadata) + n8n logging | Built-in reproducibility and auditability |
| Storage | Local NVMe SSD on the GPU box for active generation + models; periodic sync of final outputs to the existing Hetzner VPS or an object store (e.g., Backblaze B2 / S3-compatible) for long-term archival | Models/checkpoints are large (SDXL ~7GB, FLUX ~24GB fp16/~12GB fp8) and benefit from fast local storage; final images are small and archive cheaply |
| Version control | Git repository (this repo or a new `macal-image-gen` repo) for: ComfyUI workflow JSON exports, LoRA training configs, brand prompt templates, dataset manifests (not raw training images — see note below) | Keeps the *recipe* reproducible even though large binary assets (models, datasets) live outside Git |
| Monitoring | n8n execution history (job-level) + basic GPU monitoring (`nvidia-smi` cron logging, or a lightweight dashboard like Netdata) | Matches the "passive alerts only" monitoring philosophy already established for this bot ecosystem (`docs/05-DECISIONS.md` decision #29) |
| Python libraries (if custom scripting is needed beyond n8n/ComfyUI nodes) | `requests`/`websocket-client` for ComfyUI API calls, `Pillow` for any custom image post-processing, `pandas` for prompt/batch management | Lightweight, well-supported, no exotic dependencies |
| Deployment | Docker Compose on the GPU box (ComfyUI container + custom nodes), n8n stays where it is on the existing Hetzner VPS, connected over a private network/VPN (e.g., Tailscale) between the two servers | Matches existing deployment style in this repo (systemd + Docker Compose per `bot/DEPLOY.md`), minimizes new tooling |

> **Note on Git and datasets:** do not commit raw training images or model weight
> files (`.safetensors`, `.ckpt`) to Git — they are large binary assets. Track
> *manifests* (a CSV/JSON listing filenames + captions) in Git, and store the actual
> image files and model weights on the GPU server's disk or a dedicated object
> store bucket.



---

## 8. Technical Challenges & Risk Assessment

| Challenge | Risk Level | Mitigation |
|---|---|---|
| **No existing GPU hardware** | High (blocks everything until resolved) | Addressed directly by the phased rent-then-buy plan in Section 2.4 |
| **VRAM bottlenecks** (FLUX full-precision needs 24GB) | Medium | Use quantized FLUX (fp8/GGUF) on <24GB cards, or standardize on a 24GB card from the start; SDXL is a safe fallback that runs on far less |
| **LoRA training complexity** (getting the "Dark Luxury" look to converge correctly) | Medium | Start with a small, tightly curated 40-image dataset rather than a large messy one; iterate — the guides referenced in Section 5 confirm caption quality matters more than dataset size |
| **FLUX.1 [dev] commercial licensing** | **High if unaddressed** — could block commercial use of generated brand assets | Confirm current Black Forest Labs licensing terms before any customer-facing use; default to [schnell] or SDXL (both commercial-safe) if there's any doubt |
| **Storage growth** (models are large; 4K outputs accumulate) | Low-Medium | NVMe for active models (~50-100GB reserved), periodic archival of final images to cheap object storage; raw/intermediate generations can be pruned on a retention policy |
| **Performance/throughput at scale** | Low initially, Medium at high volume | n8n + ComfyUI's native queue handles moderate volume fine; if MACAL Empire scales to very high image volume, revisit Section 6.1's note on adding Redis/multiple GPU workers |
| **Model/tooling compatibility drift** (FLUX, ComfyUI, Kohya SS all update frequently) | Medium | Pin versions in the Docker setup; test updates in a staging copy before touching the production pipeline, exactly as this repo already does for the Telegram bot |
| **Single point of failure** (one GPU box) | Medium | Acceptable at this project's current scale (this is a content-generation pipeline, not a real-time customer-facing service); revisit only if uptime SLAs are ever required for image generation itself |
| **Team skill gap** (ComfyUI node graphs, LoRA training are new skills) | Medium | The phased validation approach (Section 2.4) doubles as a hands-on learning period before any production commitment; extensive community documentation exists for every tool recommended here |
| **Future model upgrades** (FLUX.2, SDXL successors, etc.) | Low | The architecture (ComfyUI + swappable model files + LoRA) is designed to absorb new base models without a pipeline rewrite — only the model file and possibly a retrained LoRA change |



---

## 9. Proposed System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  EXISTING INFRASTRUCTURE (Hetzner VPS 77.42.43.250 — unchanged)          │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────────────────┐     │
│  │ Telethon Bot   │  │ n8n (workflow │  │ Kokoro TTS (voice, on-    │     │
│  │ (Telegram      │  │ engine —      │  │ demand, stopped when      │     │
│  │  channel/group)│  │ ORCHESTRATOR  │  │ idle)                     │     │
│  └────────────────┘  │ for image gen)│  └───────────────────────────┘     │
│                       └──────┬────────┘                                  │
└──────────────────────────────┼───────────────────────────────────────────┘
                                │  Private network / VPN (e.g., Tailscale)
                                │  REST API calls to ComfyUI
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  NEW: GPU SERVER (Phase 1: rented RunPod/Vast.ai — Phase 2: Hetzner       │
│  GEX44 dedicated OR owned RTX 4090/3090, colocated or on-prem)           │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │ ComfyUI (Docker container, API/headless mode)                    │    │
│  │                                                                    │    │
│  │  ┌────────────┐   ┌────────────┐   ┌─────────────────────────┐   │    │
│  │  │ FLUX.1 dev │   │ SDXL 1.0 + │   │ MACAL Empire Brand LoRA │   │    │
│  │  │ (hero/     │   │ realism    │   │ (one per base model —    │   │    │
│  │  │ cinematic) │   │ checkpoint │   │ locks Dark Luxury/       │   │    │
│  │  │            │   │ (volume)   │   │ Imperial/Cinematic look) │   │    │
│  │  └────────────┘   └────────────┘   └─────────────────────────┘   │    │
│  │                                                                    │    │
│  │  Workflow graph per job:                                          │    │
│  │  Load model → Apply LoRA → Sample → Tiled 4K Upscale →            │    │
│  │  Watermark/Frame Overlay → Save (templated path + PNG metadata)   │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │ Kohya SS / AI-Toolkit (LoRA training — run periodically, not      │    │
│  │ continuously; shares the same GPU during training windows)        │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  Local NVMe: active models + checkpoints + in-progress dataset           │
└──────────────────────────────┬───────────────────────────────────────────┘
                                │  Final images + metadata
                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  OUTPUT MANAGEMENT                                                        │
│  - Organized folders by campaign/date (on GPU server or synced back)     │
│  - n8n logs each job (prompt, seed, model, LoRA weight, output path)     │
│  - Long-term archive: object storage (e.g., Backblaze B2 / S3-compatible)│
│  - Distribution: Telegram channel, marketing assets, etc. via existing   │
│    n8n workflows                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Component roles

- **n8n** — the single orchestration point. Receives content ideas/prompts, submits
  jobs to ComfyUI's API, tracks completion, handles retries/errors, and routes
  finished images to their destination (Telegram, storage, etc.). This is the same
  role n8n already plays for the rest of the EEC automation stack.
- **ComfyUI** — the generation engine. Runs as a headless API service on the GPU
  server. One workflow graph = one repeatable "recipe" (model + LoRA + upscale +
  watermark), versioned as JSON.
- **FLUX.1 / SDXL + brand LoRA** — the creative core. The LoRA is what makes every
  output "look like MACAL Empire" without prompt engineering gymnastics each time.
- **Kohya SS / AI-Toolkit** — runs periodically (not a 24/7 service) whenever the
  brand LoRA needs (re)training, sharing the same GPU hardware.
- **Storage** — fast local disk for the working set (models + active dataset),
  cheap object storage for the long-term image archive.



---

## 10. Implementation Roadmap

| Phase | Duration | Activities | Exit criteria |
|---|---|---|---|
| **0. Legal/licensing check** | 1 day | Confirm FLUX.1 [dev] commercial license status directly with Black Forest Labs' current terms | Clear go/no-go on [dev] vs [schnell]-only |
| **1. Validation** | 2-4 weeks | Rent GPU (RunPod/Vast.ai, 24GB card). Install ComfyUI + models. Curate 40-80 image brand dataset. Train first MACAL Empire style LoRA (SDXL first — faster iteration — then FLUX). Manually test outputs against brand guidelines. | A LoRA that reliably produces on-brand images across varied prompts |
| **2. Pipeline automation** | 1-2 weeks | Build the ComfyUI workflow graph (generate → upscale → watermark → save). Wire n8n to submit jobs and log results. Test error handling and batch runs of 20-50 images. | End-to-end automated run from a prompt list to finished, watermarked 4K images with zero manual steps |
| **3. Production hardware decision** | 1 week | Based on actual validation-phase usage (hours/week, images/month), choose: Hetzner GEX44, owned RTX 4090, or owned RTX 3090 | Signed decision + budget approval (see Section 11) |
| **4. Production deployment** | 1 week | Provision/migrate to the chosen permanent GPU infrastructure, connect to existing n8n via private network, run a full production batch | System running unattended, generating brand-consistent content on schedule |
| **5. Ongoing** | Continuous | Periodic LoRA retraining as brand evolves; monitor via n8n execution logs; expand prompt/campaign library | — |

---

## 11. Estimated One-Time Infrastructure Costs

| Item | Low estimate | High estimate | Notes |
|---|---|---|---|
| Phase 1 validation (GPU rental) | $50 | $150 | 2-4 weeks, moderate usage on RunPod/Vast.ai |
| Legal review (license check) | $0 | $0 | Self-serve — read Black Forest Labs' published license |
| **If choosing owned RTX 3090** | $700 | $1,050 | Used market, 24GB VRAM |
| **If choosing owned RTX 4090** | $1,600 | $2,000 | New, 24GB VRAM, fastest option |
| **If choosing Hetzner GEX44 (rented, not owned)** | €79 setup + €184/mo | — | No upfront capex; ongoing opex instead |
| Brand dataset sourcing (photography/stock, if not using existing brand assets) | $0 (if using existing assets) | $500-1,500 (if commissioning original photography) | Highly variable — depends on whether MACAL Empire already has enough on-brand source imagery |
| Miscellaneous (storage expansion, VPN/networking setup) | $0 | $100 | Mostly software/config, minimal hardware cost |

**Realistic total one-time cost range: $50 (rental-only path) to ~$2,200 (owned RTX
4090 + dataset sourcing) before any ongoing opex.**

---

## 12. Final Recommendations

0. **If budget is $0 right now: start on Kaggle (Section 2.5), not the paid path.**
   Train the brand LoRA and run manual generation batches for free. Move to paid
   rented/owned hardware only once you need automation or exceed the free weekly
   GPU quota.
1. **Do the license check first** (Section 3.1 warning) — it's free and changes
   which model can safely be used for commercial brand assets.
2. **Rent before you buy.** Validate the entire pipeline on a rented 24GB GPU for
   2-4 weeks before spending capital on owned hardware.
3. **ComfyUI in API mode** is the correct engine — no serious alternative exists for
   the automation requirements described.
4. **Dual-model strategy**: FLUX.1 for hero/cinematic quality, SDXL for volume and
   LoRA/ControlNet depth.
5. **One dedicated style LoRA**, trained on 40-80 curated images, is what actually
   delivers "consistent high-end branding" — this is the single highest-leverage
   piece of this whole system and deserves the most care in dataset curation.
6. **Reuse n8n** as the orchestrator. Do not introduce Celery/RabbitMQ/a new queue
   system until real usage data proves n8n is insufficient.
7. **Keep post-processing inside ComfyUI** (upscale, watermark, frame, metadata) —
   no separate tools needed.
8. **Defer the owned-hardware purchase decision** until Phase 1 validation produces
   real usage numbers — this is the biggest single cost decision in the plan and
   should not be made speculatively.

---

## 13. Immediate Next Steps

### If starting at $0 (Section 2.5):

1. ✅ Review this document and approve/adjust the direction (this step).
2. Create a free Kaggle account (no credit card required).
3. Curate the first 40-80 image MACAL Empire brand dataset (source, clean, caption)
   — this is unpaid work regardless of which path you take, so it's a good first
   task either way.
4. Set up ComfyUI + Kohya SS (or AI-Toolkit) in a Kaggle notebook.
5. Train the first style LoRA (start with SDXL for faster iteration cycles) inside
   your weekly 30-hour quota.
6. Run a manual test batch (5-10 prompts) and review output quality against brand
   guidelines; iterate on the LoRA/dataset if needed.
7. Repeat weekly manual generation sessions until you outgrow the free tier
   (Section 2.5, "When to graduate") — then proceed to step 3 below.

### When ready to move to paid infrastructure:

1. Confirm FLUX.1 [dev] licensing status for commercial use (Section 3.1).
2. Provision a RunPod or Vast.ai account and rent a 24GB GPU instance (RTX 4090 or
   A6000) for the validation phase.
3. Install ComfyUI on the rented instance; download FLUX.1 and SDXL base models
   (or migrate your Kaggle-trained LoRA over — no need to retrain from scratch).
4. Build and test the first end-to-end ComfyUI workflow graph (generate → upscale →
   watermark → save).
5. Wire n8n to submit a small test batch (5-10 prompts) through the pipeline.
6. Reconvene to decide on permanent hardware (Section 11) based on real usage data.

---

*This document is a planning artifact. No infrastructure has been provisioned, no
GPU has been rented or purchased, and no models have been downloaded as part of
producing this report. All next steps in Section 13 require explicit approval
before execution.*
