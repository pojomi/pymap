#!/usr/bin/env python3
from difflib import SequenceMatcher

# Minimum average per-word score for a candidate to count as a match.
FUZZY_THRESHOLD = 0.6


def _token_score(word: str, tokens: list[str]) -> float:
    if any(word in token for token in tokens):
        return 1.0  # partial-word substring match
    best = 0.0
    for token in tokens:
        ratio = SequenceMatcher(None, word, token).ratio()
        if ratio > best:
            best = ratio
    return best


def fuzzy_score(query: str, text: str) -> float:
    # Scores how well `text` matches `query`, tolerating partial words and
    # minor misspellings. 1.0 = every query word appears as a substring of
    # some word in `text`; lower scores reflect approximate (typo-tolerant)
    # matches; 0.0 = no meaningful similarity.
    words = query.strip().lower().split()
    if not words:
        return 0.0
    tokens = text.lower().split()
    if not tokens:
        return 0.0
    return sum(_token_score(word, tokens) for word in words) / len(words)
