# FINDINGS — FP-18: LLM Watermark Robustness Under Adversarial Paraphrasing

> **Project:** FP-18
> **Date:** 2026-03-19
> **Status:** COMPLETE — NEGATIVE RESULT
> **Lock commit:** `1704ff5`
> **Model:** claude-3-haiku-20240307
> **Seeds:** [42, 123, 456, 789, 1024]
> **Experiments run:** E1, E3, E4, E5, E6

---

## Executive Summary

**All six hypotheses resolved. Five are UNSUPPORTED (untestable); one is SUPPORTED (H-5).** The watermark simulation — output-level synonym substitution with 15 word pairs — does not produce sufficient statistical signal for detection under any condition. Detection rate is 0% across all 45 experimental conditions. This is a **simulation fidelity failure**: the experiment measures the limitations of output-level watermarking approximation, not the robustness of the Kirchenbauer watermark scheme.

This is an honest negative result. The governance framework forced pre-registration of hypotheses, which means we cannot retroactively reframe the failure. The finding is: **output-level synonym substitution is not a valid proxy for logit-level watermarking when testing robustness.**

---

## Hypothesis Resolutions

### H-1: Paraphrasing monotonically reduces watermark detection — UNSUPPORTED (UNTESTABLE)

| Field | Value |
|-------|-------|
| **Prediction** | z_score(pass_N+1) < z_score(pass_N) for all N |
| **Result** | z-scores are noise: mean z ranges from -0.05 to 0.94 across pass counts. No monotonic trend. |
| **Resolution** | **UNSUPPORTED — untestable.** Cannot measure degradation of a signal that was never present. Detection rate is 0% at pass=0 (no paraphrasing), so there is no baseline to degrade from. |

**Data:**
| Passes | Mean z | Std | Detection Rate |
|--------|--------|-----|----------------|
| 0 | 0.94 | 1.05 | 0% |
| 1 | 0.25 | 0.78 | 0% |
| 2 | 0.72 | 1.00 | 0% |
| 3 | 0.19 | 0.85 | 0% |
| 5 | -0.05 | 1.34 | 0% |
| 10 | 0.09 | 1.08 | 0% |

### H-2: 3-5 passes sufficient to remove watermark — UNSUPPORTED (UNTESTABLE)

Detection rate is 0% at pass=0. There is no watermark to remove. The prediction assumes a starting detection rate near 100%.

### H-3: Stronger watermark (higher delta) survives more passes — UNSUPPORTED (UNTESTABLE)

Mean z at delta=1.0: -0.84, delta=2.0: -0.30, delta=4.0: +0.48. The trend direction is consistent with prediction, but no condition reaches detection threshold. The 15-pair vocabulary is the bottleneck, not delta.

### H-4: Short texts lose watermark faster — UNSUPPORTED (UNTESTABLE)

Mean z at 50w: 0.20, 200w: 0.55, 500w: -0.24. No clear length effect. Signal word counts: 50w texts have 0-1 signal words, 200w have 1-6, 500w have 3-11. Even 500-word texts don't reach detection threshold.

### H-5: Unwatermarked text has near-zero false positive rate — SUPPORTED

FPR = 0.0 for both unwatermarked LLM text and human text. However, this is trivially true: the detector never exceeds z > 2.0 for ANY text. No false positives because no true positives either.

### H-6: Watermark survival is predictable (R² > 0.5) — UNSUPPORTED

R² = 0.043. RMSE = 1.16. Only non-trivial weight: delta (0.333 per unit). The model explains 4.3% of z-score variance.

---

## Root Cause Analysis

The Kirchenbauer green-list watermark biases **every token** at the logit level — with ~200 tokens, the statistical test has high power. Our simulation substitutes words from a **15-pair synonym list** at the output level:

1. **Low signal density:** Only 1-11 words (0.5-5%) match the 15 signal pairs
2. **Insufficient statistical power:** With n=3 signal words, 100% green fraction yields z=1.73 < 2.0 threshold
3. **Minimum needed:** z > 2.0 with 100% green fraction requires n >= 16 signal words

**Output-level synonym substitution is not a valid proxy for logit-level watermarking.**

---

## Governance Lessons

1. **E0 sanity should test on REALISTIC data.** E0a used a hand-crafted sentence with 10+ signal words — far more than LLM-generated text. This masked the signal density problem.
2. **Pre-registration worked.** We cannot retroactively claim we were "testing simulation fidelity." The hypotheses were about watermark robustness, and they are honestly resolved as untestable.
3. **Gate 0.5 design review did not catch the signal density issue.** A back-of-envelope power analysis would have flagged this before spending API budget.

---

## Sensitivity Analysis

All z-scores reported with standard deviation across 5 seeds. Key dispersion measures:

| Condition | Mean z +/- Std | N (signal words range) |
|-----------|---------------|------------------------|
| E1 pass=0 | 0.94 +/- 1.05 | 2-10 |
| E1 pass=10 | 0.09 +/- 1.08 | 1-8 |
| E4 delta=1.0 | -0.84 +/- 1.06 | 1-7 |
| E4 delta=4.0 | 0.48 +/- 0.93 | 1-9 |
| E3 50w | 0.20 +/- 0.88 | 0-1 |
| E3 500w | -0.24 +/- 0.88 | 3-11 |
| E6 model | R² = 0.043, RMSE = 1.16 | n=45 observations |

The high variance relative to mean (coefficient of variation > 1.0 in all conditions) confirms that z-scores are noise-dominated. Even the most favorable individual observation (z=2.0 in E3/200w) barely touches the detection threshold.

---

## Detection Methodology (R38)

Detection uses the Kirchenbauer z-score test: count green-list words among all signal words, compute z = (green_fraction - 0.5) / sqrt(0.25/n). Text is flagged as watermarked if z > 2.0 (one-tailed, p < 0.023).

**Detection threshold sensitivity:** Even lowering threshold to z > 1.0, detection rate remains below 40% at pass=0 and drops to ~20% at pass=5. The signal is fundamentally insufficient, not merely below an aggressive threshold.

**False positive baseline:** Unwatermarked LLM text mean z = -0.80 +/- 1.43. Human text mean z = -0.20 +/- 0.45. Neither approaches detection threshold.

---

## Formal Contribution Statement (R34)

We contribute:
1. **Empirical evidence** that output-level synonym substitution (15 pairs) is not a valid proxy for logit-level watermarking when measuring robustness — signal density is 100x too low.
2. **A governance failure case study** demonstrating that E0 sanity validation on unrealistic data can mask fundamental design flaws, and that pre-registration forces honest reporting of negative results.
3. **A power analysis requirement** for future Gate 0.5 reviews: estimate signal density before committing compute budget.

---

## Related Work

| # | Paper | Year | Relevance |
|---|-------|------|-----------|
| 1 | Kirchenbauer et al. — "A Watermark for LLMs" | 2023 | Green-list method we approximated |
| 2 | Sadasivan et al. — "Can AI-Generated Text be Reliably Detected?" | 2023 | Theoretical paraphrase attack argument |
| 3 | Krishna et al. — "Paraphrasing Evades Detectors" | 2023 | DIPPER paraphraser defeats detectors |
| 4 | Mitchell et al. — "DetectGPT" | 2023 | Zero-shot detection baseline |
| 5 | Christ et al. — "Undetectable Watermarks" | 2024 | Theoretical robustness bounds |
| 6 | Zhao et al. — "Provable Robust Watermarking" | 2023 | Robustness analysis of watermark schemes |

---

## Limitations

1. No logit access — API-only prevents true Kirchenbauer implementation
2. 15-pair synonym vocabulary insufficient for statistical detection on natural text
3. Only tested Haiku-to-Haiku (E2 cross-model not run)
4. 5 seeds per condition (limited by API cost)
5. Results do not generalize to real watermark implementations

---

## Next Steps (if pursued)

1. Use open-source model (LLaMA) with logit access for real Kirchenbauer watermarking
2. Expand synonym vocabulary to 200+ pairs for viable output-level simulation
3. Add power analysis to Gate 0.5 checklist for future projects
