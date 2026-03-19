"""Watermark simulation for LLM output.

Since we can't access model logits through the API, we simulate watermarking
by injecting a statistical signature: specific word choices that can be
detected but are invisible to readers. This approximates the Kirchenbauer
green-list method at the output level.

The "watermark" is: biasing word choice toward a deterministic set of
"green" synonyms. Detection checks whether the text uses more green
synonyms than expected by chance.
"""
import hashlib
import re
from collections import Counter

import numpy as np

# Green-list: preferred synonyms that serve as watermark signal
# Each pair: (common word, green synonym)
GREEN_PAIRS = [
    ("important", "significant"),
    ("show", "demonstrate"),
    ("big", "substantial"),
    ("help", "facilitate"),
    ("use", "utilize"),
    ("get", "obtain"),
    ("make", "generate"),
    ("good", "effective"),
    ("bad", "detrimental"),
    ("think", "consider"),
    ("need", "require"),
    ("give", "provide"),
    ("start", "initiate"),
    ("end", "conclude"),
    ("try", "attempt"),
]

GREEN_WORDS = {g for _, g in GREEN_PAIRS}
COMMON_WORDS = {c for c, _ in GREEN_PAIRS}
ALL_SIGNAL_WORDS = GREEN_WORDS | COMMON_WORDS


def apply_watermark(text: str, delta: float = 2.0, rng=None) -> str:
    """Apply watermark by biasing toward green synonyms.

    Higher delta = more aggressive substitution = stronger watermark.
    delta=1.0: ~50% substitution, delta=4.0: ~90% substitution.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    words = text.split()
    result = []
    for word in words:
        lower = word.lower().strip(".,!?;:")
        # Check if word has a green synonym
        for common, green in GREEN_PAIRS:
            if lower == common:
                # Probability of substitution increases with delta
                prob = 1.0 - np.exp(-delta * 0.5)
                if rng.random() < prob:
                    # Preserve capitalization
                    replacement = green if word[0].islower() else green.capitalize()
                    # Preserve trailing punctuation
                    trailing = ""
                    for ch in reversed(word):
                        if ch in ".,!?;:":
                            trailing = ch + trailing
                        else:
                            break
                    word = replacement + trailing
                break
        result.append(word)
    return " ".join(result)


def detect_watermark(text: str, threshold: float = 2.0) -> dict:
    """Detect watermark by measuring green-list word frequency.

    Returns z-score: how many standard deviations above expected green fraction.
    z > threshold → watermarked.
    """
    words = text.lower().split()
    words_clean = [re.sub(r'[.,!?;:]', '', w) for w in words]

    signal_words = [w for w in words_clean if w in ALL_SIGNAL_WORDS]
    if len(signal_words) == 0:
        return {"z_score": 0.0, "green_fraction": 0.0, "signal_count": 0,
                "detected": False, "total_words": len(words)}

    green_count = sum(1 for w in signal_words if w in GREEN_WORDS)
    green_fraction = green_count / len(signal_words)

    # Under null hypothesis (no watermark), green and common are equally likely
    expected_fraction = 0.5
    n = len(signal_words)
    std = np.sqrt(expected_fraction * (1 - expected_fraction) / max(n, 1))
    z_score = (green_fraction - expected_fraction) / max(std, 0.001)

    return {
        "z_score": float(z_score),
        "green_fraction": float(green_fraction),
        "green_count": int(green_count),
        "signal_count": int(n),
        "total_words": len(words),
        "detected": z_score > threshold,
    }
