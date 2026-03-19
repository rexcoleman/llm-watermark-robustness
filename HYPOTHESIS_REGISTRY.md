# HYPOTHESIS REGISTRY — FP-18 LLM Watermark Robustness

> **Project:** FP-18 (LLM Watermark Robustness Under Adversarial Paraphrasing)
> **Created:** 2026-03-19
> **Status:** RESOLVED (6/6) — 5 UNSUPPORTED, 1 SUPPORTED
> **Lock commit:** `1704ff5`
> **Lock date:** 2026-03-19

---

## H-1: Paraphrasing monotonically reduces watermark detection

| Field | Value |
|-------|-------|
| **Statement** | Each successive paraphrase pass reduces green-list token fraction, causing watermark detection z-score to decrease monotonically. |
| **Prediction** | z_score(pass_N+1) < z_score(pass_N) for all N |
| **Falsification** | If z-score increases after a paraphrase pass, the watermark signal is not monotonically degraded. |
| **Status** | UNSUPPORTED (UNTESTABLE) — 0% detection at pass=0, no signal to degrade |
| **Linked Experiment** | E1 |
| **lock_commit** | `1704ff5` |

---

## H-2: 3-5 paraphrase passes are sufficient to remove watermark

| Field | Value |
|-------|-------|
| **Statement** | After 3-5 passes of LLM paraphrasing, watermark detection rate drops below 50% (from ~100% at pass 0). |
| **Prediction** | detection_rate(pass_5) < 0.50 |
| **Falsification** | If detection rate remains >50% after 5 passes, the watermark is more robust than expected. |
| **Status** | UNSUPPORTED (UNTESTABLE) — 0% detection at pass=0, no watermark to remove |
| **Linked Experiment** | E1 |
| **lock_commit** | `1704ff5` |

---

## H-3: Stronger watermark (higher delta) survives more passes

| Field | Value |
|-------|-------|
| **Statement** | Watermark with delta=4.0 survives more paraphrase passes than delta=1.0 before detection drops below 50%. |
| **Prediction** | passes_to_50%(delta=4.0) > passes_to_50%(delta=1.0) |
| **Falsification** | If delta doesn't affect survival, watermark strength is decoupled from robustness. |
| **Status** | UNSUPPORTED (UNTESTABLE) — directional trend (delta +0.33/unit) but no detection |
| **Linked Experiment** | E4 |
| **lock_commit** | `1704ff5` |

---

## H-4: Short texts lose watermark faster

| Field | Value |
|-------|-------|
| **Statement** | 50-word texts lose watermark detection in fewer passes than 500-word texts because fewer tokens = less statistical signal. |
| **Prediction** | passes_to_50%(50w) < passes_to_50%(500w) |
| **Falsification** | If length doesn't matter, the watermark encodes per-token, not per-document. |
| **Status** | UNSUPPORTED (UNTESTABLE) — 0% detection at all lengths, 0-11 signal words |
| **Linked Experiment** | E3 |
| **lock_commit** | `1704ff5` |

---

## H-5: Unwatermarked text has near-zero false positive rate

| Field | Value |
|-------|-------|
| **Statement** | Unwatermarked LLM text and human text produce z-scores below the detection threshold at ≥95% rate (FPR ≤ 5%). |
| **Prediction** | false_positive_rate < 0.05 |
| **Falsification** | If FPR > 5%, the watermark detection is too aggressive for deployment. |
| **Status** | SUPPORTED — FPR=0.0 (trivially: detector never exceeds threshold for any text) |
| **Linked Experiment** | E5 |
| **lock_commit** | `1704ff5` |

---

## H-6: Watermark survival is predictable from pass count + delta + length

| Field | Value |
|-------|-------|
| **Statement** | A model with features [num_passes, delta, text_length] predicts detection rate with R² > 0.5. |
| **Prediction** | R² > 0.5 |
| **Falsification** | If R² < 0.5, watermark removal is not smoothly predictable from these features. |
| **Status** | UNSUPPORTED — R²=0.043, model explains 4.3% of variance |
| **Linked Experiment** | E6 |
| **lock_commit** | `1704ff5` |

---

## Summary

| ID | Statement (short) | Prediction | Status |
|----|-------------------|-----------|--------|
| H-1 | Monotonic z-score decrease | Each pass reduces z | UNSUPPORTED (UNTESTABLE) |
| H-2 | 3-5 passes removes watermark | detection < 50% by pass 5 | UNSUPPORTED (UNTESTABLE) |
| H-3 | Higher delta = more robust | delta 4.0 survives more than 1.0 | UNSUPPORTED (UNTESTABLE) |
| H-4 | Short texts more vulnerable | 50w loses faster than 500w | UNSUPPORTED (UNTESTABLE) |
| H-5 | FPR ≤ 5% | Unwatermarked text not flagged | SUPPORTED (trivially) |
| H-6 | Survival is predictable (R² > 0.5) | Model from pass+delta+length | UNSUPPORTED (R²=0.043) |
