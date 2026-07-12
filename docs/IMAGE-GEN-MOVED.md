# image-gen/ has moved

As of 2026-07-12, the AI image generation pipeline (LoRA training on
Kaggle + ComfyUI content generation) that used to live at `image-gen/`
in this repo has been split out into its own dedicated repository:

**`empireenglishcommunity-glitch/macal-empire-image-forge`**

## Why

`image-gen/` had its own independent commit history and its own purpose
(training an image model) that had nothing structurally to do with this
repo's actual job (Telegram channel content/posting/growth automation)
beyond one of them consuming the other's output via a shared HTML2IMG
*service*. It was a genuine separate project that had been bundled into
this repo by circumstance, not by design. Splitting it out means it can
be found, documented, and worked on without wading through unrelated
Telegram-bot code, and vice versa.

## What happened to the history

Nothing was lost. `git filter-repo --subdirectory-filter image-gen` was
used to extract the exact commit history for everything under
`image-gen/` (14 commits, 2026-07-08 through 2026-07-10, all originally
merged PRs) into the new repo, verified byte-identical against the
original files (including binary contact-sheet images) before this
removal happened.

If you need the old commit history for `image-gen/` from within *this*
repo's history (not the new repo), it's still there — this removal is a
new commit, not a rewrite of past history. `git log -- image-gen` on
any commit before this one will still show it.
