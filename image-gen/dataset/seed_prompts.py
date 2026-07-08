"""
MACAL Empire — Seed Prompt Generator.

Generates the master list of prompts used to bootstrap the initial seed dataset
(100-150 candidate images) from the base SDXL model, BEFORE any LoRA exists.

Why this exists: MACAL Empire has no existing brand photography (confirmed empty
assets/images/ in this repo). Instead of paying for photography, we generate
candidates with the base model using a carefully engineered brand prompt template,
then manually curate the best ones into the actual LoRA training set.

Usage (inside the Kaggle notebook, after ComfyUI is running):
    python seed_prompts.py > prompts.txt
    # then feed prompts.txt into the ComfyUI batch generation workflow (Task 6)

Brand parameters below are extracted directly from:
    bot/templates/base.py        (colors, mood)
    docs/06-AUTOMATION-ENGINE.md (established prompt patterns)
"""

# ---------------------------------------------------------------------------
# Brand constants — keep in sync with bot/templates/base.py if it ever changes
# ---------------------------------------------------------------------------
DARK = "#0A0A0F"
GOLD = "#D4AF37"
IVORY = "#F5F0E8"

BASE_STYLE_SUFFIX = (
    "dark luxury aesthetic, imperial and cinematic, gold accents on near-black "
    "background, premium realism, elegant minimalism, dramatic single-source "
    "lighting, subtle film grain, high detail, professional photography, 8k"
)

NEGATIVE_PROMPT = (
    "cartoon, illustration, anime, low quality, blurry, oversaturated, "
    "watermark, text, logo, cluttered, bright daylight, pastel colors, "
    "cheap looking, plastic, low contrast"
)

# ---------------------------------------------------------------------------
# Prompt categories — mirrors the composition mix in DATASET-SPEC.md Section 5
# ---------------------------------------------------------------------------

ABSTRACT_ATMOSPHERIC = [
    "abstract swirl of gold dust particles suspended in darkness, long exposure feel",
    "soft radial gold glow emanating from the center of a pure black void",
    "wisps of golden smoke curling against a near-black backdrop",
    "gold light refracting through dark smoked glass",
    "a single beam of warm gold light cutting through darkness, dust motes visible",
    "liquid gold dripping slowly against matte black stone",
    "gold embers floating upward into darkness, cinematic bokeh",
    "fractal gold light patterns projected onto a dark wall",
    "gold ink dispersing in black water, macro shot",
    "a thin gold thread glowing against total darkness",
]

ARCHITECTURAL_INTERIOR = [
    "grand imperial columns bathed in warm golden light, deep shadow, cinematic",
    "an ornate dark marble hallway with a single gold chandelier glow",
    "a black stone archway with gold inlay, dramatic side lighting",
    "empty imperial throne room, dark walls, gold trim catching a single light source",
    "a spiral staircase in black marble with a gold handrail, dramatic overhead light",
    "dark luxury library interior, gold-edged books, warm lamp glow",
    "a cathedral-like dark hall with gold light streaming through a high window",
    "black granite floor reflecting a golden ceiling light, minimal furniture",
    "an empty dark luxury lounge with a single gold-framed mirror catching light",
    "imperial gate with gold detailing, closed, dramatic backlight",
]

OBJECT_MATERIAL_CLOSEUP = [
    "close-up of dark velvet fabric with a thin gold thread pattern, soft studio lighting",
    "an ornate gold crown resting on black stone, dramatic single light source, deep shadow",
    "a black marble sphere with gold veining, studio lighting, high detail",
    "gold coins scattered on dark slate, dramatic top-down lighting",
    "a gold signet ring on black leather, macro detail, shallow depth of field",
    "dark jewel-toned fabric (deep emerald or sapphire) with gold embroidery detail",
    "a gold-rimmed obsidian goblet on a black table, single candle light",
    "polished black stone with a gold crack running through it, like kintsugi",
    "a gold key resting on dark aged wood, dramatic side light",
    "an antique gold compass on black velvet, cinematic macro shot",
]

PORTRAITURE_FIGURE = [
    "portrait of a person in silhouette, rim-lit in gold against a dark imperial hallway",
    "a figure in dark formal attire standing before a gold-lit archway, back turned",
    "close-up of hands holding a gold object, dramatic chiaroscuro lighting, dark background",
    "a person's profile lit only by warm gold side-light, rest of frame pure black",
    "a solitary figure walking away down a dark corridor toward a distant gold light",
]

WILDCARD_EXPERIMENTAL = [
    "a black chess piece (king) with gold detailing on a dark reflective surface",
    "gold fractal geometric pattern emerging from darkness, abstract luxury branding concept",
    "a dark storm cloud with a single crack of gold light, dramatic and powerful",
    "an hourglass with gold sand, black frame, dramatic lighting, symbolizing mastery of time",
    "a black feather with a gold-dipped tip, floating, dark background",
]

ALL_CATEGORIES = {
    "abstract": ABSTRACT_ATMOSPHERIC,
    "architectural": ARCHITECTURAL_INTERIOR,
    "object": OBJECT_MATERIAL_CLOSEUP,
    "portrait": PORTRAITURE_FIGURE,
    "wildcard": WILDCARD_EXPERIMENTAL,
}

# Target mix percentages (see DATASET-SPEC.md Section 5) applied when generating
# multiple variations per base prompt to reach the 100-150 seed target.
CATEGORY_VARIATION_COUNTS = {
    "abstract": 3,      # 10 prompts x 3 = 30 (~30% of ~100-150)
    "architectural": 3, # 10 prompts x 3 = 30 (~25%)
    "object": 2,        # 10 prompts x 2 = 20 (~20%)
    "portrait": 3,      # 5 prompts x 3 = 15 (~15%)
    "wildcard": 2,       # 5 prompts x 2 = 10 (~10%)
}

VARIATION_MODIFIERS = [
    "",  # base version, no modifier
    ", wide angle composition",
    ", extreme close-up macro composition",
    ", symmetrical composition",
]


def build_full_prompt(subject: str) -> str:
    """Combine a subject line with the fixed brand style suffix."""
    return f"{subject}, {BASE_STYLE_SUFFIX}"


def generate_seed_prompts() -> list[str]:
    """
    Generate the full seed prompt list (target: ~100-150 prompts) by combining
    each category's base subjects with a controlled number of variation modifiers.
    """
    prompts = []
    for category, subjects in ALL_CATEGORIES.items():
        variation_count = CATEGORY_VARIATION_COUNTS[category]
        modifiers = VARIATION_MODIFIERS[:variation_count]
        for subject in subjects:
            for modifier in modifiers:
                full_subject = subject + modifier
                prompts.append(build_full_prompt(full_subject))
    return prompts


def main():
    prompts = generate_seed_prompts()
    print(f"# Generated {len(prompts)} seed prompts", flush=True)
    print(f"# Negative prompt (use for all): {NEGATIVE_PROMPT}", flush=True)
    print("#" + "-" * 70, flush=True)
    for p in prompts:
        print(p)


if __name__ == "__main__":
    main()
