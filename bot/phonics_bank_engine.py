"""
Phonics Bank Engine — Hybrid Answer System for MACAL.

Flow:
1. Student message comes in
2. Check phonics_bank.json for keyword/fuzzy match
3. If match found → serve verified answer instantly (no API call)
4. If no match → fall back to Groq AI with master prompt

Matching Strategy:
- Exact keyword match (highest priority)
- Question pattern match (medium priority)
- Fuzzy keyword match via token overlap (lower priority)
- Minimum confidence threshold to avoid false positives
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

# Load bank on import
BANK_PATH = Path(__file__).parent / "data" / "bank" / "phonics_bank.json"
_bank_data = None
_bank_entries = []
_bank_cta = ""


def _load_bank():
    """Load phonics bank from JSON file."""
    global _bank_data, _bank_entries, _bank_cta
    if _bank_data is not None:
        return

    try:
        with open(BANK_PATH, "r", encoding="utf-8") as f:
            _bank_data = json.load(f)
        _bank_entries = _bank_data.get("entries", [])
        _bank_cta = _bank_data.get("cta", "")
        print(f"  📚 Phonics bank loaded: {len(_bank_entries)} entries")
    except Exception as e:
        print(f"  ⚠️ Failed to load phonics bank: {e}")
        _bank_data = {}
        _bank_entries = []
        _bank_cta = ""


def _normalize(text: str) -> str:
    """Normalize Arabic/English text for matching."""
    if not text:
        return ""
    # Lowercase English
    text = text.lower()
    # Normalize Arabic characters
    text = text.replace("إ", "ا").replace("أ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    # Remove diacritics (tashkeel)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Remove punctuation except ? and Arabic question mark
    text = re.sub(r'[^\w\s؟?]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _tokenize(text: str) -> set:
    """Split normalized text into tokens."""
    return set(_normalize(text).split())


def _keyword_score(message_normalized: str, message_tokens: set, entry: dict) -> float:
    """
    Score an entry against the message using keyword matching.
    Returns a score between 0.0 and 1.0.
    """
    score = 0.0
    keywords = entry.get("keywords", [])

    if not keywords:
        return 0.0

    matched_keywords = 0
    for kw in keywords:
        kw_norm = _normalize(kw)
        # Exact substring match (e.g., "الفرق بين p و b" in message)
        if kw_norm in message_normalized:
            # Multi-word keywords get higher weight
            if ' ' in kw_norm:
                matched_keywords += 3  # Phrase match = very high signal
            else:
                matched_keywords += 1
        # Token match
        elif kw_norm in message_tokens:
            matched_keywords += 1

    # Normalize by number of keywords (more matches = higher confidence)
    if matched_keywords > 0:
        # At least 2 keyword hits needed for decent confidence
        score = min(matched_keywords / 3.0, 1.0)

    return score


def _pattern_score(message_normalized: str, entry: dict) -> float:
    """
    Score an entry against the message using question pattern matching.
    Returns a score between 0.0 and 1.0.
    """
    patterns = entry.get("question_patterns", [])

    if not patterns:
        return 0.0

    best_score = 0.0
    for pattern in patterns:
        pattern_norm = _normalize(pattern)
        # Exact pattern match
        if pattern_norm in message_normalized or message_normalized in pattern_norm:
            return 1.0  # Perfect match

        # Token overlap
        pattern_tokens = set(pattern_norm.split())
        message_tokens = set(message_normalized.split())
        if not pattern_tokens:
            continue

        overlap = pattern_tokens & message_tokens
        overlap_ratio = len(overlap) / len(pattern_tokens)

        if overlap_ratio > best_score:
            best_score = overlap_ratio

    return best_score


def find_bank_answer(message: str) -> Optional[str]:
    """
    Search the phonics bank for a matching answer.

    Args:
        message: The student's question/message text.

    Returns:
        The verified answer string (with CTA appended) if a match is found,
        or None if no confident match (should fall back to AI).
    """
    _load_bank()

    if not _bank_entries or not message:
        return None

    message_normalized = _normalize(message)
    message_tokens = _tokenize(message)

    if not message_normalized or len(message_normalized) < 3:
        return None

    best_entry = None
    best_score = 0.0

    for entry in _bank_entries:
        # Calculate both scores
        kw_score = _keyword_score(message_normalized, message_tokens, entry)
        pat_score = _pattern_score(message_normalized, entry)

        # Combined score: pattern match is stronger signal
        combined = max(kw_score, pat_score * 1.2)

        # Bonus for category relevance based on message content
        # If message mentions specific letters/sounds, boost sound-related entries
        if entry["category"] in ("sound_pairs", "individual_sounds", "word_pronunciations"):
            # Check if message is asking about pronunciation
            pronunciation_signals = ["نطق", "بتتنطق", "بينطق", "انطق", "أنطق", "pronunciation"]
            for signal in pronunciation_signals:
                if signal in message_normalized:
                    combined *= 1.1
                    break

        if combined > best_score:
            best_score = combined
            best_entry = entry

    # Confidence threshold — must be reasonably confident
    # 0.4 = at least 2 keyword matches or strong pattern overlap
    CONFIDENCE_THRESHOLD = 0.4

    if best_score >= CONFIDENCE_THRESHOLD and best_entry:
        answer = best_entry["answer"]

        # Append the mandatory CTA if not already ending with it
        if _bank_cta and "@macal_emperor" not in answer:
            answer += f"\n\n{_bank_cta}"
        elif _bank_cta and "النطق الصح محتاج ممارسة" not in answer:
            # Answer has @macal_emperor but not the full CTA — append it
            answer += f"\n\n{_bank_cta}"

        print(f"  📚 Bank match! Entry #{best_entry['id']} ({best_entry['category']}) — score: {best_score:.2f}")
        return answer

    return None


def reload_bank():
    """Force reload the phonics bank (useful after updates)."""
    global _bank_data
    _bank_data = None
    _load_bank()
