---
project: "FINDINGS — FP-18: LLM Watermark Robustness Under Adversarial Paraphrasing"
fp: "FP-18"
status: COMPLETE
quality_score: 8.3
last_scored: 2026-03-20
profile: security-ml
---

# FINDINGS — FP-18: LLM Watermark Robustness Under Adversarial Paraphrasing

> **Project:** FP-18 (v2 — Real Kirchenbauer Watermarking)
> **Date:** 2026-03-20
> **Status:** COMPLETE
> **Lock commit (v1):** `1704ff5` | **v2 start:** `a5bef4e`
> **Watermark model:** GPT-2 (124M) with logit access
> **Paraphrase model:** Claude 3 Haiku (`claude-3-haiku-20240307`)
> **Seeds:** [42, 123, 456, 789, 1024]
> **Experiments run:** E0, E1, E3, E4, E5, E6

---

## Executive Summary

Real Kirchenbauer green-list watermarking via GPT-2 logit access produces strong, detectable signal: **z=8.44 at E0** (84.6% green fraction, 149 tokens scored). This is a fundamental improvement over v1's synonym-substitution simulation, which achieved 0% detection across 45 conditions.

Cross-model paraphrasing (GPT-2 watermark → Claude Haiku paraphrase) degrades the watermark signal. At **pass=0 (no paraphrasing), detection rate is 100%** with mean z=9.64±1.03 across 5 seeds. Subsequent passes progressively reduce z-scores, with detection dropping as paraphrasing strips green-list token patterns.

**v1 → v2 transition:** v1 was an honest negative result (LL-93, LL-94). The failure was structural: output-level synonym substitution produces only 1-11 signal words, below the minimum 16 needed for z > 2.0. v2 fixes this by implementing the actual Kirchenbauer algorithm with logit-level token biasing.

---

## E0: Sanity Validation (LL-94 Compliant)

All 4 sub-tests PASS on realistic data (not hand-crafted):

| Test | Result | Detail |
|------|--------|--------|
| E0a: Watermarked detected | PASS | z=8.44, green=84.6%, 126/149 tokens |
| E0b: Unwatermarked not detected | PASS | z=-0.08, green=49.7%, 74/149 tokens |
| E0c: Dose-response (δ=1.0 vs δ=4.0) | PASS | z=4.32 vs z=8.83 |
| E0d: Sufficient tokens for detection | PASS | 149 tokens scored (need ≥50) |

The clean/watermarked separation is massive: z=8.44 vs z=-0.08, a ~8.5σ gap. This confirms the Kirchenbauer implementation produces detectable signal on realistic LLM output.

---

## Hypothesis Resolutions

_Note: Hypotheses were pre-registered under v1 (lock_commit `1704ff5`). v2 re-evaluates them with real watermarking. See HYPOTHESIS_REGISTRY.md for full details._

### H-1: Paraphrasing monotonically reduces watermark detection — SUPPORTED

| Field | Value |
|-------|-------|
| **Prediction** | z_score(pass_N+1) < z_score(pass_N) for all N |
| **Result** | Mean z decreases monotonically: 9.64→5.21→4.85→4.72→4.66→3.89 across passes 0,1,2,3,5,10. Detection drops 100%→60%→60%→60%→60%→40%. |
| **Resolution** | **SUPPORTED.** Z-score monotonically decreases. Detection rate shows sharp initial drop (100%→60% at pass 1) then plateau through pass 5, with final drop to 40% at pass 10. |

### H-2: 3-5 passes sufficient to remove watermark — NOT SUPPORTED

| Field | Value |
|-------|-------|
| **Prediction** | detection_rate(pass_5) < 0.50 |
| **Result** | detection_rate(pass_5) = 60%. Detection remains above 50% through 5 passes. Only at pass=10 does it drop to 40%. |
| **Resolution** | **NOT SUPPORTED.** The watermark is more robust than predicted. 3-5 passes are NOT sufficient — detection remains at 60%. 10 passes reduces to 40% but does not eliminate detection. |

### H-3: Stronger watermark survives more passes — SUPPORTED

| Field | Value |
|-------|-------|
| **Prediction** | passes_to_50%(delta=4.0) > passes_to_50%(delta=1.0) |
| **Result** | After 3 paraphrase passes: δ=1.0 z=1.48±1.32 (0% detected), δ=2.0 z=2.34±2.19 (20%), δ=4.0 z=4.48±1.97 (60%). Strong dose-response. |
| **Resolution** | **SUPPORTED.** δ=4.0 survives paraphrasing with 60% detection while δ=1.0 is completely stripped (0%). |

### H-4: Short texts lose watermark faster — SUPPORTED

| Field | Value |
|-------|-------|
| **Prediction** | passes_to_50%(50tok) < passes_to_50%(300tok) |
| **Result** | After 3 passes: 50tok z=-0.23±1.06 (0% det), 150tok z=3.16±1.31 (20% det), 300tok z=4.89±2.17 (60% det). Clear length dependence. |
| **Resolution** | **SUPPORTED.** 50-token texts are completely stripped of watermark. 300-token texts retain 60% detection. Length is a strong predictor of watermark robustness. |

### H-5: Unwatermarked text has near-zero false positive rate — SUPPORTED

| Field | Value |
|-------|-------|
| **Prediction** | false_positive_rate < 0.05 |
| **Result** | FPR = 0% for both unwatermarked LLM text and human-written text. No false positives at z>4.0 threshold. |
| **Resolution** | **SUPPORTED.** The detector never flags non-watermarked text. Unlike v1 (trivially true because nothing was detected), v2 has genuine true positives (100% at pass=0), making the 0% FPR meaningful. |

### H-6: Watermark survival is predictable (R² > 0.5) — NOT SUPPORTED

| Field | Value |
|-------|-------|
| **Prediction** | R² > 0.5 |
| **Result** | R² = 0.131, RMSE = 2.50. Weights: passes=-0.321, delta=+0.569, length=+0.022. Model explains 13% of z-score variance. |
| **Resolution** | **NOT SUPPORTED.** R²=0.131 << 0.5 threshold. Watermark survival is not smoothly predictable from these three features alone. The high variance within conditions (e.g., pass=1 std=1.74) dominates. |

---

## Root Cause Analysis (v1 → v2)

v1 failed because output-level synonym substitution (15 pairs) produces only 1-11 signal words per 200-word text. The Kirchenbauer watermark biases **every token** at the logit level — ~200 tokens scored, not ~5.

| Metric | v1 (Synonym) | v2 (Kirchenbauer) |
|--------|-------------|-------------------|
| Mechanism | Output-level word replacement | Logit-level token biasing |
| Signal words per 200w text | 1-11 | ~149-199 |
| E0 z-score | 0.94 (noise) | 8.44 (strong signal) |
| Detection rate at pass=0 | 0% | 100% |
| Statistical power | Near zero | High |

---

## Sensitivity Analysis

**E0 sensitivity:** z=8.44±0 (single run). Dose-response confirmed: δ=1.0→z=4.32, δ=4.0→z=8.83. The z-score scales with delta as expected.

**E1 pass=0 (5 seeds):** mean z=9.64±1.03. Individual values: 10.28, 9.52, 10.94, 7.87, 9.57. Coefficient of variation = 0.11 (low dispersion — consistent signal).

**E1 full paraphrase curve (5 seeds each):**

| Passes | Mean z | Std | Detection Rate |
|--------|--------|-----|----------------|
| 0 | 9.64 | 1.03 | 100% |
| 1 | 5.21 | 1.74 | 60% |
| 2 | 4.85 | 1.75 | 60% |
| 3 | 4.72 | 0.96 | 60% |
| 5 | 4.66 | 1.87 | 60% |
| 10 | 3.89 | 1.26 | 40% |

**E3 text length (after 3 paraphrase passes):**

| Length | Mean z | Std | Detection Rate |
|--------|--------|-----|----------------|
| 50 tok | -0.23 | 1.06 | 0% |
| 150 tok | 3.16 | 1.31 | 20% |
| 300 tok | 4.89 | 2.17 | 60% |

**E4 watermark strength (after 3 paraphrase passes):**

| Delta | Mean z | Std | Detection Rate |
|-------|--------|-----|----------------|
| 1.0 | 1.48 | 1.32 | 0% |
| 2.0 | 2.34 | 2.19 | 20% |
| 4.0 | 4.48 | 1.97 | 60% |

**E5 false positive rate:** 0% on both unwatermarked LLM text and human text.

**E6 predictive model:** R²=0.131, RMSE=2.50. Passes has negative weight (-0.321), delta positive (+0.569), length weakly positive (+0.022).

---

## Detection Methodology (R38)

Detection uses the Kirchenbauer z-score test with threshold z > 4.0:

1. Tokenize text using GPT-2 tokenizer
2. For each token (except first), compute green list from previous token hash
3. Count tokens falling in green list
4. Compute z = (green_count - γ·T) / √(T·γ·(1-γ)), where T = tokens scored, γ = 0.5
5. If z > 4.0, flag as watermarked (one-tailed, p < 3.2×10⁻⁵)

**Threshold choice:** v2 uses z > 4.0 (stricter than v1's z > 2.0) because real watermarking produces much stronger signal. This dramatically reduces false positive risk while maintaining high true positive rate.

**Cross-model attack:** Watermark is embedded by GPT-2 (logit biasing during generation). Paraphrasing is performed by Claude Haiku (a different model with no knowledge of the watermark). This tests the realistic adversarial scenario where the attacker doesn't know the watermarking key.

---

## Formal Contribution Statement (R34)

We contribute:
1. **Empirical paraphrase-removal curves** for the Kirchenbauer watermark: detection rate as a function of pass count, watermark strength (δ), and text length, using real logit-level watermarking on GPT-2 with cross-model paraphrasing via Claude Haiku.
2. **A v1→v2 methodology case study** demonstrating that output-level watermark simulation (synonym substitution) is not a valid proxy for logit-level watermarking — signal density differs by ~30x (5 vs 149 tokens scored).
3. **Governance lessons:** mandatory power analysis at Gate 0.5 (LL-93) and realistic E0 inputs (LL-94) prevent structural experiment failures.

---

## v1 Negative Result (Historical — Preserved)

v1 (lock_commit `1704ff5`) produced an honest negative result: 0% detection across 45 conditions using output-level synonym substitution. This is preserved as a governance case study — pre-registration forced honest reporting, and the failure revealed two governance gaps (LL-93, LL-94) now codified as rules.

See `git show 33abad8:FINDINGS.md` for the full v1 FINDINGS.

---

## Content Hooks

| Finding | Content Angle | Format |
|---------|--------------|--------|
| v1→v2 failure-to-success arc | "When Your Experiment Fails: A Governance Recovery Story" | Blog post (teaching) |
| Paraphrase removal curves | "How Many Rewrites to Strip a Watermark?" | Blog post (findings) |
| Cross-model attack viability | Practical watermark security assessment | LinkedIn post |
| Governance lessons (LL-93/94) | Power analysis as design requirement | Teaching post |

---

## Related Work

| # | Paper | Year | Relevance |
|---|-------|------|-----------|
| 1 | Kirchenbauer et al. — "A Watermark for LLMs" | 2023 | Green-list method we implement |
| 2 | Sadasivan et al. — "Can AI-Generated Text be Reliably Detected?" | 2023 | Theoretical paraphrase attack argument. We provide empirical curves. |
| 3 | Krishna et al. — "Paraphrasing Evades Detectors" | 2023 | DIPPER paraphraser. We extend to LLM-as-paraphraser. |
| 4 | Mitchell et al. — "DetectGPT" | 2023 | Zero-shot detection baseline |
| 5 | Christ et al. — "Undetectable Watermarks" | 2024 | Theoretical robustness bounds |
| 6 | Zhao et al. — "Provable Robust Watermarking" | 2023 | Robustness analysis of watermark schemes |

---

## Limitations

1. GPT-2 (124M) is a small model — watermark behavior may differ on larger models
2. Single paraphrase model (Claude Haiku) — E2 cross-model comparison not yet run
3. 5 seeds per condition (limited by CPU compute time on 2-vCPU VM)
4. Detection threshold z > 4.0 is stricter than some literature (z > 2.0)
5. No perplexity measurement (quality cost of watermarking not quantified)

---

## Next Steps

1. Complete E1-E6 experiments and fill in hypothesis resolutions
2. Generate figures from experiment data
3. Update blog post with v2 results
4. Consider E2 (cross-model: Haiku vs Sonnet paraphrase) if API budget allows
5. Measure perplexity impact of watermarking (Defense Harm Test from EXPERIMENTAL_DESIGN.md)
