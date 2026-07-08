# Seed Image Curation Review

> **STATUS: APPROVED by user July 8, 2026.** Final counts below were corrected after
> re-verification against the actual generation log (`raw_seed/seed_batch_log.csv`):
> **76 KEEP / 18 REJECT** (initial verbal estimate of 68/26 was off by a recount error —
> `#066` was missing from the original tally and has been added to KEEP).
> Captions were written from the real prompt text used to generate each image (not
> guessed) and processed through `prepare_dataset.py` — see `curated/manifest.csv`.

Open this PR on GitHub to see the actual images rendered inline below each contact sheet.
94 raw seed images were generated. They're grouped into 5 contact sheets (grids of thumbnails,
labeled with their `#NNN` index = `seed_NNN.png` in `image-gen/dataset/raw_seed/`).

**How to review:** Look at each sheet image below, then check the KEEP/REJECT table against what
you see. Reply in chat with any numbers you want to move between lists (e.g. "keep #013 too" or
"reject #096"), or just say "approved" to confirm the shortlist as-is.

---

## Contact Sheet 0 (#002 - #022)
![Sheet 0](contact_sheets/contact_sheet_00.jpg)

## Contact Sheet 1 (#023 - #043)
![Sheet 1](contact_sheets/contact_sheet_01.jpg)

## Contact Sheet 2 (#044 - #069)
![Sheet 2](contact_sheets/contact_sheet_02.jpg)

## Contact Sheet 3 (#070 - #090)
![Sheet 3](contact_sheets/contact_sheet_03.jpg)

## Contact Sheet 4 (#091 - #105)
![Sheet 4](contact_sheets/contact_sheet_04.jpg)

---

## Final KEEP list (76 images) — used for training dataset

| Group | Numbers |
|---|---|
| Abstract gold textures/liquid/smoke | 002, 003, 004, 005, 006, 007, 008, 009, 010, 011, 023, 025, 026, 027 |
| Geometric/pattern gold-on-black | 024, 098, 099 |
| Imperial architecture (columns, halls, arches, stairs) | 031, 032, 033, 039, 044, 045, 046, 049, 050, 051, 052, 058, 059, 093, 094, 095 |
| Throne rooms / regal interiors | 034, 035, 036, 038, 040, 041, 042, 043, 047, 048, 054, 055, 056, 057 |
| Objects (keys, compass, coins, goblets, ring, marble sphere) | 066, 067, 068, 069, 070, 073, 074, 075, 077, 078, 079, 080 |
| Silhouetted robed figures (best brand-identity shots) | 081, 082, 083, 084, 085, 086, 087, 088, 089 |
| Chess/power symbolism | 096 |
| Feathers (dark+gold) | 104, 105 |
| Gold nuggets/bokeh | 018, 019, 020, 021, 022 |

## Final REJECT list (18 images)

| # | Reason |
|---|---|
| 013, 014, 015, 016, 017 | Grey/neutral studio background — breaks dark palette |
| 028, 029, 030 | Generic gold rope/chain, redundant with better texture shots |
| 053 | White marble hallway — breaks dark palette |
| 071, 072 | Green damask pattern — wrong color palette |
| 090 | Light/white studio background |
| 091, 092 | Portrait busts on light background (also raises stock-likeness concerns) |
| 100, 101 | Storm clouds/lightning — off-concept (weather, not imperial/luxury) |
| 102, 103 | Hourglasses on light grey studio background |

---

## Completed: dataset preparation

- Real captions (from actual generation prompts, not placeholders) written for all 76 kept
  images → `manifest_template.csv` (tracked in git)
- `prepare_dataset.py` run: **76/76 accepted, 0 rejected** — all resized/cropped to 1024x1024,
  all captions verified non-placeholder
- Output: `curated/` folder (76 `.png` + 76 `.txt` pairs + `manifest.csv`) — gitignored per
  `DATASET-SPEC.md` (binary training images not committed to git)
- Zipped for handoff: `curated_dataset.zip` (~106MB) — see `image-gen/RUN_GUIDE.md` Step 5 for
  how to upload this to a new Kaggle session as a Dataset and start LoRA training

**Next step:** upload `curated_dataset.zip` contents to Kaggle and run
`training/MACAL_Empire_Train_LoRA.ipynb` (RUN_GUIDE.md Step 5).
