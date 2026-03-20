#!/usr/bin/env python3
"""FP-18v2: Watermark robustness experiments with REAL Kirchenbauer watermarking.

Uses GPT-2 with logit access for true green-list watermarking.
Claude Haiku for paraphrasing (cross-model attack).

Usage:
    python -u scripts/run_experiments_v2.py --experiments E0
    python -u scripts/run_experiments_v2.py --experiments E0,E1,E3,E4,E5,E6
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.kirchenbauer_watermark import KirchenbauerWatermark

OUTPUT_DIR = Path("outputs/experiments_v2")
SEEDS = [42, 123, 456, 789, 1024]
WATERMARK_MODEL = "gpt2"

PROMPTS = [
    "The impact of remote work on corporate productivity has been",
    "Artificial intelligence in healthcare presents both risks and benefits because",
    "Reducing carbon emissions in urban transportation requires strategies that",
    "The effectiveness of microfinance in developing economies depends on",
    "Cloud-native architectures introduce cybersecurity implications including",
]


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)


def save_results(name, data):
    out_file = OUTPUT_DIR / f"{name}_results.json"
    with open(out_file, "w") as f:
        json.dump({"experiment": name, "date": datetime.now().isoformat(),
                    "results": data}, f, indent=2, cls=NpEncoder)
    print(f"  Saved: {out_file}")


def get_paraphrase_client():
    """Claude client for paraphrasing (cross-model attack)."""
    import anthropic
    return anthropic.Anthropic()


def paraphrase(client, text):
    """Paraphrase using Claude (cross-model adversarial attack)."""
    resp = client.messages.create(
        model="claude-3-haiku-20240307", max_tokens=len(text.split()) * 3,
        temperature=0.7,
        messages=[{"role": "user", "content":
            f"Paraphrase the following text completely. Change all word choices "
            f"while preserving the meaning:\n\n{text}"}],
    )
    return resp.content[0].text


def run_e0(wm):
    """E0: Sanity validation on REALISTIC data (LL-94 compliant)."""
    print(f"\n{'='*60}\nE0: Sanity Validation (LL-94: realistic inputs)\n{'='*60}")
    results = {}

    # E0a: Watermarked text MUST be detected
    wm_text = wm.generate_watermarked("The future of artificial intelligence is",
                                       max_new_tokens=150)
    det_wm = wm.detect(wm_text)
    e0a = det_wm["detected"]
    print(f"  E0a watermarked (realistic): z={det_wm['z_score']:.2f}, "
          f"tokens={det_wm['num_tokens_scored']}, green={det_wm['green_fraction']:.3f}, "
          f"detected={e0a} — {'PASS' if e0a else 'FAIL'}")
    results["e0a"] = {"pass": e0a, **det_wm, "text_preview": wm_text[:100]}

    # E0b: Unwatermarked text MUST NOT be detected
    clean_text = wm.generate_unwatermarked("The future of artificial intelligence is",
                                            max_new_tokens=150)
    det_clean = wm.detect(clean_text)
    e0b = not det_clean["detected"]
    print(f"  E0b unwatermarked (realistic): z={det_clean['z_score']:.2f}, "
          f"tokens={det_clean['num_tokens_scored']}, green={det_clean['green_fraction']:.3f}, "
          f"detected={det_clean['detected']} — {'PASS' if e0b else 'FAIL'}")
    results["e0b"] = {"pass": e0b, **det_clean, "text_preview": clean_text[:100]}

    # E0c: Higher delta = stronger detection (dose-response)
    wm_low = KirchenbauerWatermark(WATERMARK_MODEL, delta=1.0)
    wm_high = KirchenbauerWatermark(WATERMARK_MODEL, delta=4.0)
    text_low = wm_low.generate_watermarked("Climate change affects global economies by",
                                            max_new_tokens=100)
    text_high = wm_high.generate_watermarked("Climate change affects global economies by",
                                              max_new_tokens=100)
    z_low = wm_low.detect(text_low)["z_score"]
    z_high = wm_high.detect(text_high)["z_score"]
    e0c = z_high > z_low
    print(f"  E0c dose-response: delta=1.0 z={z_low:.2f}, delta=4.0 z={z_high:.2f} "
          f"— {'PASS' if e0c else 'FAIL'}")
    results["e0c"] = {"pass": e0c, "z_low": z_low, "z_high": z_high}

    # E0d: Realistic generation produces enough tokens for detection (LL-94)
    e0d = det_wm["num_tokens_scored"] >= 50
    print(f"  E0d token count: {det_wm['num_tokens_scored']} tokens scored "
          f"(need ≥50) — {'PASS' if e0d else 'FAIL'}")
    results["e0d"] = {"pass": e0d, "num_tokens": det_wm["num_tokens_scored"]}

    results["overall_pass"] = e0a and e0b and e0c and e0d
    print(f"  E0 OVERALL: {'PASS' if results['overall_pass'] else 'FAIL'} "
          f"({sum([e0a, e0b, e0c, e0d])}/4)")
    return results


def run_e1(wm, seeds):
    """E1: Paraphrase passes vs detection rate."""
    print(f"\n{'='*60}\nE1: Paraphrase Passes vs Detection\n{'='*60}")
    client = get_paraphrase_client()
    pass_counts = [0, 1, 2, 3, 5, 10]
    results = {}

    for n_passes in pass_counts:
        seed_results = []
        for i, seed in enumerate(seeds):
            torch_seed = torch.manual_seed(seed)
            prompt = PROMPTS[i % len(PROMPTS)]
            wm_text = wm.generate_watermarked(prompt, max_new_tokens=200,
                                               temperature=1.0)
            # Paraphrase N times
            current = wm_text
            for p in range(n_passes):
                current = paraphrase(client, current)

            det = wm.detect(current)
            seed_results.append(det)
            print(f"  passes={n_passes}, seed={seed}: z={det['z_score']:.2f}, "
                  f"green={det['green_fraction']:.3f}, tokens={det['num_tokens_scored']}, "
                  f"detected={det['detected']}")

        z_scores = [r["z_score"] for r in seed_results]
        det_rates = [1 if r["detected"] else 0 for r in seed_results]
        results[str(n_passes)] = {
            "seeds": seed_results,
            "z_score_mean": float(np.mean(z_scores)),
            "z_score_std": float(np.std(z_scores)),
            "detection_rate": float(np.mean(det_rates)),
        }
        print(f"  → pass={n_passes}: mean_z={np.mean(z_scores):.2f} ± {np.std(z_scores):.2f}, "
              f"detection_rate={np.mean(det_rates):.1%}")

    save_results("e1", results)
    return results


def run_e3(wm, seeds):
    """E3: Text length vs robustness."""
    print(f"\n{'='*60}\nE3: Text Length vs Robustness\n{'='*60}")
    client = get_paraphrase_client()
    lengths = [50, 150, 300]  # tokens (GPT-2 generates tokens, not words)
    n_passes = 3
    results = {}

    for length in lengths:
        seed_results = []
        for i, seed in enumerate(seeds):
            torch.manual_seed(seed)
            prompt = PROMPTS[i % len(PROMPTS)]
            wm_text = wm.generate_watermarked(prompt, max_new_tokens=length)

            current = wm_text
            for _ in range(n_passes):
                current = paraphrase(client, current)

            det = wm.detect(current)
            seed_results.append(det)
            print(f"  length={length}tok, seed={seed}: z={det['z_score']:.2f}, "
                  f"tokens={det['num_tokens_scored']}")

        z_scores = [r["z_score"] for r in seed_results]
        results[str(length)] = {
            "seeds": seed_results,
            "z_score_mean": float(np.mean(z_scores)),
            "z_score_std": float(np.std(z_scores)),
            "detection_rate": float(np.mean([1 if r["detected"] else 0 for r in seed_results])),
        }

    save_results("e3", results)
    return results


def run_e4(wm_base, seeds):
    """E4: Watermark strength (delta) vs robustness."""
    print(f"\n{'='*60}\nE4: Watermark Strength vs Robustness\n{'='*60}")
    client = get_paraphrase_client()
    deltas = [1.0, 2.0, 4.0]
    n_passes = 3
    results = {}

    for delta in deltas:
        wm_d = KirchenbauerWatermark(WATERMARK_MODEL, delta=delta)
        seed_results = []
        for i, seed in enumerate(seeds):
            torch.manual_seed(seed)
            prompt = PROMPTS[i % len(PROMPTS)]
            wm_text = wm_d.generate_watermarked(prompt, max_new_tokens=200)

            current = wm_text
            for _ in range(n_passes):
                current = paraphrase(client, current)

            det = wm_d.detect(current)
            seed_results.append(det)
            print(f"  delta={delta}, seed={seed}: z={det['z_score']:.2f}, "
                  f"detected={det['detected']}")

        z_scores = [r["z_score"] for r in seed_results]
        results[str(delta)] = {
            "seeds": seed_results,
            "z_score_mean": float(np.mean(z_scores)),
            "z_score_std": float(np.std(z_scores)),
            "detection_rate": float(np.mean([1 if r["detected"] else 0 for r in seed_results])),
        }

    save_results("e4", results)
    return results


def run_e5(wm, seeds):
    """E5: False positive rate on clean text."""
    print(f"\n{'='*60}\nE5: False Positive Rate\n{'='*60}")
    results = {}

    # Unwatermarked LLM text
    fp_llm = []
    for i, seed in enumerate(seeds):
        torch.manual_seed(seed)
        prompt = PROMPTS[i % len(PROMPTS)]
        text = wm.generate_unwatermarked(prompt, max_new_tokens=200)
        det = wm.detect(text)
        fp_llm.append(det)
        print(f"  LLM unwatermarked, seed={seed}: z={det['z_score']:.2f}, "
              f"detected={det['detected']}")

    results["unwatermarked_llm"] = {
        "seeds": fp_llm,
        "false_positive_rate": float(np.mean([1 if r["detected"] else 0 for r in fp_llm])),
    }

    # Human-written text
    human_texts = [
        "The economic landscape continues to shift as global supply chains adapt to post-pandemic realities. Governments worldwide are implementing new trade policies.",
        "Educational institutions face mounting pressure to integrate technology without sacrificing pedagogical quality. The balance between innovation and tradition remains difficult.",
        "Urban planners increasingly recognize the need for mixed-use development to create vibrant communities. Zoning reforms are accelerating across major cities.",
        "The pharmaceutical industry invests billions in research while facing scrutiny over drug pricing models. Patent reform debates continue in Congress.",
        "Agricultural innovation promises higher yields but raises questions about biodiversity and soil health. Sustainable farming practices are gaining mainstream adoption.",
    ]
    fp_human = []
    for text in human_texts:
        det = wm.detect(text)
        fp_human.append(det)
        print(f"  Human text: z={det['z_score']:.2f}, detected={det['detected']}")

    results["human_text"] = {
        "seeds": fp_human,
        "false_positive_rate": float(np.mean([1 if r["detected"] else 0 for r in fp_human])),
    }

    save_results("e5", results)
    return results


def run_e6(seeds):
    """E6: Predictive model of watermark survival."""
    print(f"\n{'='*60}\nE6: Predictive Model (R34.8)\n{'='*60}")
    features, labels = [], []

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

    result = {"r2": float(r2), "rmse": float(rmse),
              "weights": {"passes": float(w[0]), "delta": float(w[1]),
                          "length": float(w[2]), "bias": float(w[3])},
              "n_observations": len(X)}
    save_results("e6", result)
    return result


import torch  # needed for seed setting in experiment functions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiments", default="E0")
    parser.add_argument("--delta", type=float, default=2.0)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"FP-18v2 Watermark Robustness — Real Kirchenbauer Watermarking")
    print(f"Watermark model: {WATERMARK_MODEL} | Paraphrase model: claude-3-haiku")
    print(f"Delta: {args.delta} | Gamma: 0.5 | Seeds: {SEEDS}")
    print(f"Loading model...")

    t0 = time.time()
    wm = KirchenbauerWatermark(WATERMARK_MODEL, delta=args.delta)
    print(f"Model loaded in {time.time()-t0:.1f}s")

    experiments = {
        "E0": lambda: run_e0(wm),
        "E1": lambda: run_e1(wm, SEEDS),
        "E3": lambda: run_e3(wm, SEEDS),
        "E4": lambda: run_e4(wm, SEEDS),
        "E5": lambda: run_e5(wm, SEEDS),
        "E6": lambda: run_e6(SEEDS),
    }

    requested = [e.strip() for e in args.experiments.split(",")]
    all_results = {}

    for exp_id in requested:
        if exp_id in experiments:
            result = experiments[exp_id]()
            all_results[exp_id] = result
            if exp_id == "E0":
                save_results("e0", result)
                if not result.get("overall_pass", False):
                    print("\n*** E0 FAILED — stopping. Fix before running E1+. ***")
                    break

    summary_file = OUTPUT_DIR / "all_experiments_summary.json"
    with open(summary_file, "w") as f:
        json.dump({"date": datetime.now().isoformat(),
                    "watermark_model": WATERMARK_MODEL,
                    "paraphrase_model": "claude-3-haiku-20240307",
                    "seeds": SEEDS, "results": all_results}, f, indent=2, cls=NpEncoder)
    print(f"\nSaved: {summary_file}")


if __name__ == "__main__":
    main()
