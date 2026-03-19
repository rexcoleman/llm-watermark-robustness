# Experimental Design Review — FP-18: LLM Watermark Robustness Under Adversarial Paraphrasing

> **Gate:** 0.5 (must pass before Phase 1 compute)
> **Date:** 2026-03-19
> **Target venue:** AISec Workshop (ACM CCS 2026) — Tier 2
> **lock_commit:** `1704ff5`
> **Profile:** contract-track
> **Budget:** ~$10-15 Claude API

---

## 1) Project Identity

**Project:** FP-18 — LLM Watermark Robustness Under Adversarial Paraphrasing
**Domain:** AI-generated text detection (Security FROM AI)
**This fills the gap:** Portfolio is 80% "Security OF AI." This is the first "Security FROM AI" research project.
**Completely different from FP-15/16/17:** Not multi-agent, not cascade, not delegation. Tests whether the governance generalizes.

---

## 2) Novelty Claim (one sentence)

> First empirical measurement of how many paraphrase passes are needed to remove statistical watermarks from LLM output, with a cost-quality-detectability tradeoff surface that practitioners can use to assess watermark viability.

---

## 3) Comparison Baselines

| # | Method | Citation | How We Compare | Why This Baseline |
|---|--------|----------|---------------|-------------------|
| 1 | Kirchenbauer et al. soft watermark | 2023 | Reproduce their green-list detection, test against our paraphrase attacks | Most cited watermark paper. Reviewer expects this comparison. |
| 2 | No watermark (unwatermarked LLM output) | Control | False positive rate: how often does unwatermarked text trigger detection? | Establishes baseline detection accuracy. |
| 3 | DetectGPT (zero-shot detection without watermark) | Mitchell et al. 2023 | Compare watermark detection to model-free detection under same paraphrase attacks | Alternative detection approach. Reviewer asks "why watermark at all?" |
| 4 | Simple heuristic (perplexity threshold) | Baseline | Cheapest detection method. If watermarks don't beat this, they're not worth the complexity. | Lower bound — any method must beat this. |

---

## 4) Pre-Registered Reviewer Kill Shots

| # | Criticism | Planned Mitigation | Design Decision |
|---|----------|-------------------|-----------------|
| 1 | "You're not implementing a real watermark — you're approximating one." | We implement the Kirchenbauer green-list algorithm exactly as described. Open-source, reproducible, with verification against their published results. | Use their algorithm, not a proxy. |
| 2 | "Paraphrasing with the same model that watermarked is circular." | Use a DIFFERENT model for paraphrasing than for watermarking. Watermark with one model, paraphrase with another. Test cross-model paraphrasing. | Watermark model ≠ paraphrase model. |
| 3 | "This only tests one watermark scheme." | Acknowledged in limitations. But Kirchenbauer is the dominant scheme. If it's fragile, the field has a problem. Future work: test Aaronson/Christ schemes. | Focus on the most-deployed scheme, do it well. |
| 4 | "N=100 texts is too few." | Each text is tested at 5 paraphrase levels × 5 seeds = 2500 detection decisions. The unit of analysis is the detection decision, not the text. | Large N of decisions from moderate N of texts. |

---

## 5) Ablation Plan

| Component | Hypothesis When Changed | Expected Effect | Priority |
|-----------|------------------------|-----------------|----------|
| Number of paraphrase passes (1, 2, 3, 5, 10) | More passes = weaker watermark signal | Detection rate decreases monotonically with passes | HIGH — the core finding |
| Paraphrase model (Haiku vs Sonnet) | Stronger paraphraser = faster watermark removal | Sonnet removes watermark in fewer passes | HIGH |
| Text length (short 50w, medium 200w, long 500w) | Longer text = more watermark signal = harder to remove | Short texts lose watermark faster | MEDIUM |
| Watermark strength (delta parameter: 1.0, 2.0, 4.0) | Stronger watermark = harder to remove but more detectable to humans | Higher delta survives more passes but degrades text quality | HIGH |
| Detection threshold (z-score: 2.0, 3.0, 4.0) | Higher threshold = fewer false positives but more missed watermarks | Tradeoff curve between FPR and TPR | MEDIUM |

---

## 6) Ground Truth Audit

| Source | Type | Count | Known Lag | Positive Rate | Limitations |
|--------|------|-------|-----------|---------------|-------------|
| Watermarked Claude output | Empirical (API) | ~100 texts × 5 paraphrase levels = 500 | None | 100% watermarked (by construction) | Single watermark scheme |
| Unwatermarked Claude output | Empirical (API) | ~100 texts | None | 0% watermarked (control) | Same model family |
| Human-written text samples | External dataset | ~50 texts | N/A | 0% watermarked | Different distribution than LLM |

### Alternative Sources Considered

| Source | Included? | Rationale |
|--------|-----------|-----------|
| GPT-4 watermarked output | NO | OpenAI's watermark is not public. Can't reproduce. |
| Open-source watermark implementations | YES (reference) | KGW implementation from HuggingFace |
| Academic paraphrase datasets | NO | We generate our own via API for consistency |

---

## 7) Statistical Plan

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Seeds | 5 (42, 123, 456, 789, 1024) | govML standard |
| Texts per condition | 20 | 20 texts × 5 seeds × 5 paraphrase levels = 500 detection decisions |
| Significance test | McNemar's test (paired binary: detected/not before vs after paraphrase) | Paired design — same text before and after |
| Effect size | ≥20pp detection rate drop after N paraphrases | Practitioner-meaningful |
| CI method | Wilson score (proportions) | Standard for binary detection |
| API budget | ~$10-15 (Haiku watermarking + Sonnet paraphrasing) | ~2000 API calls |

---

## 8) Related Work Checklist (≥5 for Tier 2)

| # | Paper | Year | Relevance | How We Differ |
|---|-------|------|-----------|---------------|
| 1 | Kirchenbauer et al. — "A Watermark for LLMs" | 2023 | THE watermark paper. Green-list method. | We test adversarial robustness, they tested basic quality. |
| 2 | Sadasivan et al. — "Can AI-Generated Text be Reliably Detected?" | 2023 | Showed paraphrasing defeats detection | Theoretical argument. We provide empirical pass-count curves. |
| 3 | Mitchell et al. — "DetectGPT" | 2023 | Zero-shot detection without watermark | Our comparison baseline #3. |
| 4 | Krishna et al. — "Paraphrasing Evades Detectors" | 2023 | Showed DIPPER paraphraser defeats detectors | We extend to LLM-as-paraphraser (stronger, cheaper). |
| 5 | Christ et al. — "Undetectable Watermarks for Language Models" | 2024 | Theoretically undetectable watermark | We test the practical (Kirchenbauer) scheme, not theoretical. |
| 6 | Zhao et al. — "Provable Robust Watermarking" | 2023 | Robustness analysis of watermark schemes | Theoretical bounds. We provide empirical curves. |

---

## 9) Design Review Checklist (Gate 0.5)

| # | Requirement | Status | Notes |
|---|------------|--------|-------|
| 1 | Novelty claim stated in ≤25 words | [x] | §2 |
| 2 | ≥2 comparison baselines identified | [x] | §3: 4 baselines |
| 3 | ≥2 reviewer kill shots with mitigations | [x] | §4: 4 kill shots |
| 4 | Ablation plan with hypothesized effects | [x] | §5: 5 components |
| 5 | Ground truth audit: sources, lag, positive rate | [x] | §6: 3 sources |
| 6 | Alternative label sources considered | [x] | §6: GPT-4, open-source, academic datasets |
| 7 | Statistical plan: seeds, tests, CIs | [x] | §7: McNemar's, Wilson CI |
| 8 | Related work: ≥5 papers | [x] | §8: 6 papers |
| 9 | Hypotheses pre-registered | [ ] | To create |
| 10 | lock_commit set | [ ] | To set |
| 11 | Target venue identified | [x] | AISec Workshop |
| 12 | This document committed before any training script | [x] | This commit |

**Gate 0.5 verdict:** [x] PASS (pending items 9-10)

---

## 10) Tier 2 Depth Escalation (R34)

### Depth Commitment

**Primary finding (one sentence):** N paraphrase passes with an LLM reduce watermark detection rate from X% to Y%, establishing a cost-quality-detectability tradeoff surface.

**Evaluation settings (minimum 2):**

| # | Setting | How It Differs | What It Tests |
|---|---------|---------------|---------------|
| 1 | Haiku watermark + Haiku paraphrase | Same-model paraphrase | Baseline removal rate |
| 2 | Haiku watermark + Sonnet paraphrase | Cross-model paraphrase | Whether stronger model removes faster |
| 3 | Variable text length (50w, 200w, 500w) | Length varies | Whether short texts are more vulnerable |

### Mechanism Analysis Plan

| Finding | Proposed Mechanism | Experiment to Verify |
|---------|-------------------|---------------------|
| Paraphrasing removes watermark | Green-list token distribution shifts toward natural distribution | Measure green-list token fraction before/after each pass |
| Stronger watermark survives more passes | Higher delta = more green-list bias = harder to fully remove | Sweep delta (1.0, 2.0, 4.0) × passes (1-10) |
| Short texts lose watermark faster | Fewer tokens = less statistical signal | Compare detection rate at 50w vs 500w after same number of passes |

### Adaptive Adversary Plan

| Robustness Claim | Weak Test | Adaptive Test |
|-----------------|-----------|---------------|
| Watermark survives basic paraphrasing | Single-pass paraphrase ("rewrite this") | Multi-pass paraphrase (10 passes) + instruction to maximize diversity |
| Detection robust to false positives | Unwatermarked LLM text | Human-written text (different distribution) |

### Defense Harm Test

- [ ] Verify watermarking doesn't degrade text quality below usability threshold
- [ ] Measure perplexity before/after watermarking — quality cost of defense

### Qualitative Prediction Validation

| Prediction | Quantitative | Qualitative |
|-----------|-------------|-------------|
| More passes = less detection | Monotonic decrease | No "recovery" at high pass counts |
| Stronger watermark = more robust | Higher delta = higher pass count for 50% detection | Linear or sub-linear relationship |
| Short texts more vulnerable | 50w loses detection in fewer passes than 500w | Length threshold below which watermark is useless |

### Simulation Calibration Note

> N/A — all experiments are on real LLM output. No simulation.

### Formalization Attempt (R34.8)

**Finding to formalize:** Detection rate as a function of paraphrase passes, watermark strength, and text length.

**Formalization type:**
- [x] Predictive model (features → detection rate)
- Features: [num_passes, watermark_delta, text_length, paraphrase_model_strength]
- Validation: LOO-CV
- If R² > 0.5: publish as "watermark survival model"
- If R² < 0.5: report as "watermark removal is not smoothly predictable" (finding)

### Depth Escalation Checklist

| # | Requirement | Status |
|---|------------|--------|
| 1 | ONE primary finding identified | [x] |
| 2 | ≥2 evaluation settings designed | [x] |
| 3 | Mechanism analysis planned (including nulls) | [x] |
| 4 | Adaptive adversary test planned | [x] |
| 5 | Formal contribution statement drafted | [x] |
| 6 | ≥1 published baseline reproduction planned | [x] |
| 7 | Parameter sensitivity sweep planned | [x] |
| 8 | Simulation-to-real validation | [x] N/A — all real |
| 9 | Formalization attempted or explained why not | [x] |

### Formal Contribution Statement (draft)

We contribute:
1. **Empirical paraphrase-removal curves** for the Kirchenbauer watermark: detection rate as a function of pass count, watermark strength, and text length on real Claude output.
2. **A cost-quality-detectability tradeoff surface** that practitioners can use to assess whether watermarking is viable for their use case (quality loss vs adversarial robustness).
3. **Cross-model paraphrasing analysis** showing whether a stronger paraphrase model removes watermarks faster, quantifying the attacker's compute-detection tradeoff.

---

## 11) Phase 1 Exit Checkpoint

| # | Check | Status | Deviation? |
|---|-------|--------|------------|
| 1 | All 4 baselines run | [ ] | |
| 2 | 5 seeds per experiment | [ ] | |
| 3 | All 5 ablation components tested | [ ] | |
| 4 | Deviations logged in DECISION_LOG | [ ] | |
| 5 | All experiment outputs exist | [ ] | |

---

## 12) Experiment Matrix

| ID | Question | IV | Levels | DV | Seeds |
|----|----------|-----|--------|-----|-------|
| E1 | How many passes to remove watermark? | Pass count | 0, 1, 2, 3, 5, 10 | Detection rate (z-score) | 5 |
| E2 | Does cross-model paraphrase remove faster? | Paraphrase model | Haiku, Sonnet | Detection rate per pass | 5 |
| E3 | Does text length affect robustness? | Length | 50w, 200w, 500w | Detection rate per pass | 5 |
| E4 | Does watermark strength affect survival? | Delta | 1.0, 2.0, 4.0 | Detection rate per pass | 5 |
| E5 | False positive rate on clean text | Text source | Unwatermarked LLM, human | Detection rate (should be ~0) | 5 |
| E6 | Formalization: can we predict survival? | All features | Combined from E1-E4 | R², RMSE | LOO-CV |
