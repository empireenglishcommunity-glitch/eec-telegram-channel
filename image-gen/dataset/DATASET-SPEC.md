# MACAL Empire — Brand Style LoRA Dataset Specification

> Defines exactly what goes into the training dataset, how it's captioned, and how
> it's organized. Read this before running anything in `kaggle/` or `training/`.

## 1. What we're training

A **style LoRA** (not a character LoRA) that teaches SDXL to default to the
MACAL Empire visual identity: **Dark Luxury, Imperial, Cinematic lighting, premium
realism, elegant minimalism.**

## 2. The trigger word (locked — do not change once training starts)

```
macalempire style
```

Every caption in the dataset starts with this exact phrase. At inference time,
including `macalempire style` in a prompt activates the trained look.

## 3. Bootstrapping problem & solution

**Problem:** MACAL Empire has no existing photography/brand image library (confirmed
— `assets/images/` in this repo is empty). Commissioning original photography costs
money, which conflicts with the zero-budget starting point.

**Solution — self-bootstrapping:** Generate the seed dataset *with the base model
itself* (SDXL, no LoRA yet), using a carefully engineered master prompt that encodes
the brand's exact color palette, materials, and mood (derived from the real brand
spec in `bot/templates/base.py` and `docs/06-AUTOMATION-ENGINE.md`). Generate many
candidates, manually curate the best ones, and use *those* as the LoRA training set.

This is a standard, well-documented technique for bootstrapping a style LoRA with
zero starting images — you're teaching the model to reliably reproduce a look it can
already produce *occasionally* and *inconsistently*, making it produce that look
*by default*.

## 4. Source-of-truth brand parameters (extracted from this repo)

| Parameter | Value | Source |
|---|---|---|
| Primary dark | `#0A0A0F` (near-black, slightly blue-black) | `bot/templates/base.py` |
| Accent gold | `#D4AF37` | `bot/templates/base.py` |
| Light text/highlight | `#F5F0E8` (warm ivory, not pure white) | `bot/templates/base.py` |
| Mood motifs | Subtle noise/grain texture, soft radial gold glow from upper-center, thin gold accent lines, marble/velvet/jewel-tone materials | `bot/templates/base.py`, image-gen research report |
| Established prompt patterns | "Crown or empire pillars, gold on matte black, premium brand identity, powerful"; "Dark background (#0A0A0F), gold accent (#D4AF37), modern, minimal, professional" | `docs/06-AUTOMATION-ENGINE.md` |
| Typography mood (for any in-image text/logo work later) | Cinzel (serif, imperial/classical feel) for brand marks | `bot/templates/base.py` |

## 5. Dataset size & composition target

| Category | Target count | Purpose |
|---|---|---|
| Seed candidates (generated, pre-curation) | 100-150 | Wide net — expect to discard ~half |
| **Final curated training set** | **40-80** | What actually goes into LoRA training |

Composition mix within the final 40-80 (approximate, not rigid):
- ~30% abstract/atmospheric (gold light on dark textures, smoke, particles, marble veining)
- ~25% architectural/interior (imperial columns, dark luxury interiors, dramatic lighting)
- ~20% object/material close-ups (gold on velvet, jewel tones, metal textures)
- ~15% portraiture/figure (cinematic lighting on a human subject, dark background, gold rim light) — only if MACAL Empire wants a human presence in its imagery
- ~10% wildcard/experimental (let the model surprise you, keep anything on-brand)

This variety-within-consistency is what teaches "style" rather than "one repeated scene."

## 6. Resolution & format

- 1024×1024 minimum (SDXL native training resolution)
- PNG (lossless — avoid JPEG artifacts contaminating training)
- No watermarks, no text overlays, no logos baked into the training images themselves
  (the brand watermark gets added at *generation* time later, in ComfyUI post-processing
  — never bake it into the LoRA)

## 7. Captioning rules

Every caption follows this exact structure:

```
macalempire style, <description of what's actually in THIS specific image>
```

**Do:**
- Describe the concrete subject, composition, and lighting of each individual image
- Keep captions natural language, not keyword-stuffed
- Vary the description content across images (that's what teaches variety)

**Don't:**
- Re-describe the general style ("dark luxury", "gold accents", "imperial") in every
  caption — the trigger word is what carries the style; if you restate it every time,
  the LoRA can bind the style too rigidly to specific caption phrasing instead of the
  trigger word alone
- Use inconsistent trigger phrasing (always exactly `macalempire style`, same casing,
  same position — first in the caption)

### Example captions

```
macalempire style, a marble column bathed in warm golden light against a near-black background, cinematic shadow
macalempire style, close-up of dark velvet fabric with a thin gold thread pattern, soft studio lighting
macalempire style, an ornate gold crown resting on black stone, dramatic single light source, deep shadow
macalempire style, portrait of a person in silhouette, rim-lit in gold against a dark imperial hallway
macalempire style, abstract swirl of gold dust particles suspended in darkness, long exposure feel
```

## 8. Folder structure

```
image-gen/dataset/
├── DATASET-SPEC.md              ← this file
├── seed_prompts.py               ← generates the master prompt list for bootstrapping
├── prepare_dataset.py            ← resize/validate/caption-scaffold script
├── manifest_template.csv         ← tracked in git (filenames + captions, NOT images)
├── raw_seed/                     ← (gitignored) 100-150 generated candidates land here
└── curated/                      ← (gitignored) final 40-80 curated training images + .txt caption files
```

> **Git policy:** `raw_seed/` and `curated/` are gitignored (binary images, large,
> and not portable across licensing). Only `manifest_template.csv` (the recipe —
> filenames + captions) is tracked in git, per the version-control guidance in the
> infrastructure report.
