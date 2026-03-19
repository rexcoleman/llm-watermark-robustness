"""R46: Measurement unit tests for watermark detection."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.watermark import apply_watermark, detect_watermark, GREEN_WORDS
import numpy as np


def test_watermark_increases_green_fraction():
    text = "We need to help people get good results and show them how to use tools."
    wm = apply_watermark(text, delta=4.0, rng=np.random.default_rng(42))
    det = detect_watermark(wm)
    assert det["green_fraction"] > 0.5, f"Green fraction {det['green_fraction']} should be > 0.5"


def test_unwatermarked_not_detected():
    text = "The quarterly revenue increased by twelve percent across all segments."
    det = detect_watermark(text)
    assert not det["detected"], f"Clean text should not be detected (z={det['z_score']})"


def test_strong_watermark_detected():
    text = "We need to help people get good results and show them how to use the tools to make things start working."
    wm = apply_watermark(text, delta=4.0, rng=np.random.default_rng(42))
    det = detect_watermark(wm)
    assert det["detected"], f"Strong watermark should be detected (z={det['z_score']})"


def test_higher_delta_stronger_signal():
    text = "We need to help people get good results and show them how to use tools."
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)
    z_low = detect_watermark(apply_watermark(text, delta=1.0, rng=rng1))["z_score"]
    z_high = detect_watermark(apply_watermark(text, delta=4.0, rng=rng2))["z_score"]
    assert z_high >= z_low, f"Higher delta should give higher z: {z_high} vs {z_low}"


def test_z_score_is_float():
    det = detect_watermark("Some text here")
    assert isinstance(det["z_score"], float)


def test_detection_returns_all_fields():
    det = detect_watermark("Test text with some words")
    assert "z_score" in det
    assert "green_fraction" in det
    assert "detected" in det
    assert "total_words" in det
