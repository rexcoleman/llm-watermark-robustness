#!/usr/bin/env python3
"""FP-18: Watermark robustness experiments (E0-E6).

Tests how LLM paraphrasing degrades watermark signal.

Usage:
    ANTHROPIC_API_KEY=... python -u scripts/run_experiments.py
    ANTHROPIC_API_KEY=... python -u scripts/run_experiments.py --experiments E0,E1
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.watermark import apply_watermark, detect_watermark


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

OUTPUT_DIR = Path("outputs/experiments")
SEEDS = [42, 123, 456, 789, 1024]
MODEL = "claude-3-haiku-20240307"

# Sample topics for text generation
TOPICS = [
    "Analyze the impact of remote work on corporate productivity",
    "Evaluate the risks and benefits of artificial intelligence in healthcare",
    "Discuss strategies for reducing carbon emissions in urban transportation",
    "Assess the effectiveness of microfinance in developing economies",
    "Review the cybersecurity implications of cloud-native architectures",
]


def get_client():
    import anthropic
    return anthropic.Anthropic()


def generate_text(client, topic, length_words=200):
    resp = client.messages.create(
        model=MODEL, max_tokens=int(length_words * 1.5), temperature=0.7,
        messages=[{"role": "user", "content": f"Write a {length_words}-word analysis: {topic}"}],
    )
    return resp.content[0].text


def paraphrase(client, text):
    resp = client.messages.create(
        model=MODEL, max_tokens=len(text.split()) * 2, temperature=0.7,
        messages=[{"role": "user", "content": f"Paraphrase the following text completely. Change all word choices while preserving the meaning:\n\n{text}"}],
    )
    return resp.content[0].text


def run_e0(seeds):
    """E0: Sanity validation."""
    print(f"\n{'='*60}\nE0: Sanity Validation\n{'='*60}")
    results = {}

    # E0a: Watermarked text should be detected
    text = "We need to help people get good results and show them how to use the tools to make things start working."
    wm = apply_watermark(text, delta=4.0)
    det = detect_watermark(wm)
    e0a = det["detected"]
    print(f"  E0a positive: z={det['z_score']:.2f}, detected={e0a} — {'PASS' if e0a else 'FAIL'}")
    results["e0a"] = {"pass": e0a, "z_score": det["z_score"]}

    # E0b: Unwatermarked text should NOT be detected
    clean = "The quarterly revenue increased by twelve percent driven by strong enterprise demand across all segments."
    det_clean = detect_watermark(clean)
    e0b = not det_clean["detected"]
    print(f"  E0b negative: z={det_clean['z_score']:.2f}, detected={det_clean['detected']} — {'PASS' if e0b else 'FAIL'}")
    results["e0b"] = {"pass": e0b, "z_score": det_clean["z_score"]}

    # E0c: Higher delta = stronger detection
    z_low = detect_watermark(apply_watermark(text, delta=1.0))["z_score"]
    z_high = detect_watermark(apply_watermark(text, delta=4.0))["z_score"]
    e0c = z_high > z_low
    print(f"  E0c dose: delta=1.0 z={z_low:.2f}, delta=4.0 z={z_high:.2f} — {'PASS' if e0c else 'FAIL'}")
    results["e0c"] = {"pass": e0c, "z_low": z_low, "z_high": z_high}

    results["overall_pass"] = e0a and e0b and e0c
    print(f"  E0 OVERALL: {'PASS' if results['overall_pass'] else 'FAIL'}")
    return {"e0_sanity": results}


def run_e1(seeds):
    """E1: Paraphrase passes vs detection rate."""
    print(f"\n{'='*60}\nE1: Paraphrase Passes vs Detection\n{'='*60}")
    client = get_client()
    pass_counts = [0, 1, 2, 3, 5, 10]
    results = {}

    for n_passes in pass_counts:
        seed_results = []
        for seed in seeds:
            rng = np.random.default_rng(seed)
            topic = TOPICS[seed % len(TOPICS)]

            # Generate and watermark
            text = generate_text(client, topic, 200)
            wm_text = apply_watermark(text, delta=2.0, rng=rng)

            # Paraphrase N times
            current = wm_text
            for _ in range(n_passes):
                current = paraphrase(client, current)

            # Detect
            det = detect_watermark(current)
            seed_results.append(det)
            print(f"  passes={n_passes}, seed={seed}: z={det['z_score']:.2f}, detected={det['detected']}")

        z_scores = [r["z_score"] for r in seed_results]
        det_rates = [1 if r["detected"] else 0 for r in seed_results]
        results[str(n_passes)] = {
            "seeds": seed_results,
            "z_score_mean": float(np.mean(z_scores)),
            "z_score_std": float(np.std(z_scores)),
            "detection_rate": float(np.mean(det_rates)),
        }

    return results


def run_e3(seeds):
    """E3: Text length vs robustness."""
    print(f"\n{'='*60}\nE3: Text Length vs Robustness\n{'='*60}")
    client = get_client()
    lengths = [50, 200, 500]
    n_passes = 3  # Fixed at 3 passes
    results = {}

    for length in lengths:
        seed_results = []
        for seed in seeds:
            rng = np.random.default_rng(seed)
            topic = TOPICS[seed % len(TOPICS)]
            text = generate_text(client, topic, length)
            wm_text = apply_watermark(text, delta=2.0, rng=rng)

            current = wm_text
            for _ in range(n_passes):
                current = paraphrase(client, current)

            det = detect_watermark(current)
            seed_results.append(det)
            print(f"  length={length}w, seed={seed}: z={det['z_score']:.2f}")

        z_scores = [r["z_score"] for r in seed_results]
        results[str(length)] = {
            "seeds": seed_results,
            "z_score_mean": float(np.mean(z_scores)),
            "detection_rate": float(np.mean([1 if r["detected"] else 0 for r in seed_results])),
        }

    return results


def run_e4(seeds):
    """E4: Watermark strength (delta) vs robustness."""
    print(f"\n{'='*60}\nE4: Watermark Strength vs Robustness\n{'='*60}")
    client = get_client()
    deltas = [1.0, 2.0, 4.0]
    n_passes = 3
    results = {}

    for delta in deltas:
        seed_results = []
        for seed in seeds:
            rng = np.random.default_rng(seed)
            topic = TOPICS[seed % len(TOPICS)]
            text = generate_text(client, topic, 200)
            wm_text = apply_watermark(text, delta=delta, rng=rng)

            current = wm_text
            for _ in range(n_passes):
                current = paraphrase(client, current)

            det = detect_watermark(current)
            seed_results.append(det)
            print(f"  delta={delta}, seed={seed}: z={det['z_score']:.2f}")

        z_scores = [r["z_score"] for r in seed_results]
        results[str(delta)] = {
            "seeds": seed_results,
            "z_score_mean": float(np.mean(z_scores)),
            "detection_rate": float(np.mean([1 if r["detected"] else 0 for r in seed_results])),
        }

    return results


def run_e5(seeds):
    """E5: False positive rate on clean text."""
    print(f"\n{'='*60}\nE5: False Positive Rate\n{'='*60}")
    client = get_client()
    results = {}

    # Unwatermarked LLM text
    fp_llm = []
    for seed in seeds:
        topic = TOPICS[seed % len(TOPICS)]
        text = generate_text(client, topic, 200)
        det = detect_watermark(text)  # No watermark applied
        fp_llm.append(det)
        print(f"  LLM unwatermarked, seed={seed}: z={det['z_score']:.2f}, detected={det['detected']}")

    results["unwatermarked_llm"] = {
        "seeds": fp_llm,
        "false_positive_rate": float(np.mean([1 if r["detected"] else 0 for r in fp_llm])),
    }

    # Human-written text (simulated with different prompts)
    human_texts = [
        "The economic landscape continues to shift as global supply chains adapt to post-pandemic realities.",
        "Educational institutions face mounting pressure to integrate technology without sacrificing pedagogical quality.",
        "Urban planners increasingly recognize the need for mixed-use development to create vibrant communities.",
        "The pharmaceutical industry invests billions in research while facing scrutiny over drug pricing models.",
        "Agricultural innovation promises higher yields but raises questions about biodiversity and soil health.",
    ]
    fp_human = []
    for text in human_texts:
        det = detect_watermark(text)
        fp_human.append(det)
        print(f"  Human text: z={det['z_score']:.2f}, detected={det['detected']}")

    results["human_text"] = {
        "seeds": fp_human,
        "false_positive_rate": float(np.mean([1 if r["detected"] else 0 for r in fp_human])),
    }

    return results


def run_e6(seeds):
    """E6: Build predictive model of watermark survival."""
    print(f"\n{'='*60}\nE6: Predictive Model (R34.8)\n{'='*60}")

    # Load E1 and E4 results for features
    features = []
    labels = []

    e1_file = OUTPUT_DIR / "e1_results.json"
    if e1_file.exists():
        with open(e1_file) as f:
            e1 = json.load(f)["results"]
        for passes_str, data in e1.items():
            for seed_data in data["seeds"]:
                features.append([int(passes_str), 2.0, 200])
                labels.append(seed_data["z_score"])

    e4_file = OUTPUT_DIR / "e4_results.json"
    if e4_file.exists():
        with open(e4_file) as f:
            e4 = json.load(f)["results"]
        for delta_str, data in e4.items():
            for seed_data in data["seeds"]:
                features.append([3, float(delta_str), 200])
                labels.append(seed_data["z_score"])

    if not features:
        print("  No data — run E1 and E4 first")
        return {"error": "no data"}

    X = np.array(features)
    y = np.array(labels)

    # Fit linear model
    X_bias = np.column_stack([X, np.ones(len(X))])
    w, _, _, _ = np.linalg.lstsq(X_bias, y, rcond=None)
    y_pred = X_bias @ w
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / max(ss_tot, 1e-10)
    rmse = np.sqrt(np.mean((y - y_pred) ** 2))

    print(f"  R² = {r2:.4f}")
    print(f"  RMSE = {rmse:.4f}")
    print(f"  Weights: passes={w[0]:.3f}, delta={w[1]:.3f}, length={w[2]:.5f}, bias={w[3]:.3f}")

    return {
        "r2": float(r2), "rmse": float(rmse),
        "weights": {"passes": float(w[0]), "delta": float(w[1]),
                    "length": float(w[2]), "bias": float(w[3])},
        "n_observations": len(X),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", default="E0,E1,E3,E4,E5,E6")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    experiments = {"E0": run_e0, "E1": run_e1, "E3": run_e3,
                   "E4": run_e4, "E5": run_e5, "E6": run_e6}
    requested = [e.strip() for e in args.experiments.split(",")]
    all_results = {}

    print(f"FP-18 Watermark Robustness — Experiments")
    print(f"Model: {MODEL} | Seeds: {SEEDS}")

    for exp_id in requested:
        if exp_id in experiments:
            result = experiments[exp_id](SEEDS)
            all_results[exp_id] = result
            out_file = OUTPUT_DIR / f"{exp_id.lower()}_results.json"
            with open(out_file, "w") as f:
                json.dump({"experiment": exp_id, "date": datetime.now().isoformat(),
                          "results": result}, f, indent=2, cls=NpEncoder)
            print(f"  Saved: {out_file}")

    summary_file = OUTPUT_DIR / "all_experiments_summary.json"
    with open(summary_file, "w") as f:
        json.dump({"date": datetime.now().isoformat(), "model": MODEL,
                   "seeds": SEEDS, "results": all_results}, f, indent=2, cls=NpEncoder)
    print(f"\nSaved: {summary_file}")


if __name__ == "__main__":
    main()
