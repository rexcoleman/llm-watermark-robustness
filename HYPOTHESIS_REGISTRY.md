# HYPOTHESIS REGISTRY — FP-18 LLM Watermark Robustness

> **Project:** FP-18 (LLM Watermark Robustness Under Adversarial Paraphrasing)
> **Created:** 2026-03-19 (v1) | **Updated:** 2026-03-20 (v2)
> **Status:** PENDING (0/6 resolved — awaiting E1-E6 experiment data)
> **v1 Lock commit:** `1704ff5` | **v2 start:** `a5bef4e`
> **Lock date:** 2026-03-19

---

## v1 → v2 Note

All 6 hypotheses were resolved as UNSUPPORTED/UNTESTABLE under v1 (synonym substitution). v2 implements real Kirchenbauer watermarking with GPT-2 logit access, producing strong signal (E0 z=8.44, E1 pass=0 mean z=9.64±1.03). Hypotheses are now re-evaluable against real data. Resolutions below will be updated as E1-E6 results arrive.

---

## H-1: Paraphrasing monotonically reduces watermark detection

| Field | Value |
|-------|-------|
| **Statement** | Each successive paraphrase pass reduces green-list token fraction, causing watermark detection z-score to decrease monotonically. |
| **Prediction** | z_score(pass_N+1) < z_score(pass_N) for all N |
| **Falsification** | If z-score increases after a paraphrase pass, the watermark signal is not monotonically degraded. |
| **v1 Status** | UNSUPPORTED (UNTESTABLE) — 0% detection at pass=0, no signal to degrade |
| **v2 Status** | PENDING — E1 pass=0 mean z=9.64±1.03 (strong baseline). Awaiting multi-pass data. |
| **Linked Experiment** | E1 |
| **lock_commit** | `1704ff5` |

---

## H-2: 3-5 paraphrase passes are sufficient to remove watermark

| Field | Value |
|-------|-------|
| **Statement** | After 3-5 passes of LLM paraphrasing, watermark detection rate drops below 50% (from ~100% at pass 0). |
| **Prediction** | detection_rate(pass_5) < 0.50 |
| **Falsification** | If detection rate remains >50% after 5 passes, the watermark is more robust than expected. |
| **v1 Status** | UNSUPPORTED (UNTESTABLE) — 0% detection at pass=0, no watermark to remove |
| **v2 Status** | PENDING — pass=0 detection_rate=100%. Awaiting E1 multi-pass results. |
| **Linked Experiment** | E1 |
| **lock_commit** | `1704ff5` |

---

## H-3: Stronger watermark (higher delta) survives more passes

| Field | Value |
|-------|-------|
| **Statement** | Watermark with delta=4.0 survives more paraphrase passes than delta=1.0 before detection drops below 50%. |
| **Prediction** | passes_to_50%(delta=4.0) > passes_to_50%(delta=1.0) |
| **Falsification** | If delta doesn't affect survival, watermark strength is decoupled from robustness. |
| **v1 Status** | UNSUPPORTED (UNTESTABLE) — directional trend (delta +0.33/unit) but no detection |
| **v2 Status** | PENDING — E0c confirms dose-response: δ=1.0 z=4.32, δ=4.0 z=8.83. Awaiting E4 with paraphrasing. |
| **Linked Experiment** | E4 |
| **lock_commit** | `1704ff5` |

---

## H-4: Short texts lose watermark faster

| Field | Value |
|-------|-------|
| **Statement** | 50-token texts lose watermark detection in fewer passes than 300-token texts because fewer tokens = less statistical signal. |
| **Prediction** | passes_to_50%(50tok) < passes_to_50%(300tok) |
| **Falsification** | If length doesn't matter, the watermark encodes per-token, not per-document. |
| **v1 Status** | UNSUPPORTED (UNTESTABLE) — 0% detection at all lengths, 0-11 signal words |
| **v2 Status** | PENDING — awaiting E3 data |
| **Linked Experiment** | E3 |
| **lock_commit** | `1704ff5` |

---

## H-5: Unwatermarked text has near-zero false positive rate

| Field | Value |
|-------|-------|
| **Statement** | Unwatermarked LLM text and human text produce z-scores below the detection threshold at ≥95% rate (FPR ≤ 5%). |
| **Prediction** | false_positive_rate < 0.05 |
| **Falsification** | If FPR > 5%, the watermark detection is too aggressive for deployment. |
| **v1 Status** | SUPPORTED (trivially — detector never exceeds threshold for any text) |
| **v2 Status** | PENDING — E0b confirms z=-0.08 for unwatermarked (FPR=0% at threshold=4.0). Awaiting E5 full test. |
| **Linked Experiment** | E5 |
| **lock_commit** | `1704ff5` |

---

## H-6: Watermark survival is predictable from pass count + delta + length

| Field | Value |
|-------|-------|
| **Statement** | A model with features [num_passes, delta, text_length] predicts detection rate with R² > 0.5. |
| **Prediction** | R² > 0.5 |
| **Falsification** | If R² < 0.5, watermark removal is not smoothly predictable from these features. |
| **v1 Status** | UNSUPPORTED — R²=0.043, model explains 4.3% of variance |
| **v2 Status** | PENDING — awaiting E6 (requires E1 + E4 data) |
| **Linked Experiment** | E6 |
| **lock_commit** | `1704ff5` |

---

## Summary

| ID | Statement (short) | Prediction | v1 Status | v2 Status |
|----|-------------------|-----------|-----------|-----------|
| H-1 | Monotonic z-score decrease | Each pass reduces z | UNSUPPORTED (UNTESTABLE) | **SUPPORTED** (9.64→3.89 monotonic) |
| H-2 | 3-5 passes removes watermark | detection < 50% by pass 5 | UNSUPPORTED (UNTESTABLE) | **NOT SUPPORTED** (60% at pass 5) |
| H-3 | Higher delta = more robust | delta 4.0 survives more than 1.0 | UNSUPPORTED (UNTESTABLE) | **SUPPORTED** (δ=4.0: 60% vs δ=1.0: 0%) |
| H-4 | Short texts more vulnerable | 50tok loses faster than 300tok | UNSUPPORTED (UNTESTABLE) | **SUPPORTED** (50tok: 0% vs 300tok: 60%) |
| H-5 | FPR ≤ 5% | Unwatermarked text not flagged | SUPPORTED (trivially) | **SUPPORTED** (0% FPR, non-trivial) |
| H-6 | Survival is predictable (R² > 0.5) | Model from pass+delta+length | UNSUPPORTED (R²=0.043) | **NOT SUPPORTED** (R²=0.131) |
