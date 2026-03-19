---
title: "Output-Level Watermark Simulation Fails to Produce Detectable Signal: An Honest Negative Result"
date: 2026-03-19
author: Rex Coleman
project: FP-18
tags: [watermarking, llm-security, negative-results, ai-detection]
status: draft
hypothesized: true
---

# Output-Level Watermark Simulation Fails to Produce Detectable Signal: An Honest Negative Result

## The Question We Tried to Answer

How many rounds of LLM paraphrasing does it take to strip a statistical watermark from AI-generated text? This matters because watermarking is one of the most promising approaches to AI-generated content detection — and if a cheap paraphrasing attack can remove it, the entire approach may be unviable for adversarial settings.

We set out to measure this empirically. We pre-registered six hypotheses, designed five experiments, and ran them against real Claude API output. The result? **Zero detections across 45 experimental conditions.** Not because watermarks are robust. Because our watermark simulation was too weak to test.

This is a negative result, and we're publishing it anyway — because the failure mode is instructive.

## What We Built

We implemented an output-level approximation of the Kirchenbauer et al. (2023) green-list watermark. The original Kirchenbauer method works at the logit level: before each token is generated, the model partitions the vocabulary into "green" and "red" lists based on the previous token, then biases generation toward green tokens. Detection checks whether the text uses more green tokens than expected by chance.

Since we were using the Claude API (no logit access), we approximated this at the output level. We defined 15 synonym pairs — common words and their "green" equivalents:

- "important" → "significant"
- "show" → "demonstrate"
- "use" → "utilize"
- "help" → "facilitate"
- ...and 11 more pairs

The watermark applies by probabilistically replacing common words with their green synonyms. Detection counts how many green synonyms appear relative to the total signal words and computes a z-score. If z exceeds 2.0, the text is flagged as watermarked.

We then paraphrased watermarked texts using the same Claude Haiku model, running 0, 1, 2, 3, 5, and 10 passes. Each pass asks the model to completely rewrite the text while preserving meaning.

## What We Found

**Nothing.** Literally.

Detection rate: 0% across every condition. Not "the watermark was removed by paraphrasing." The watermark was never detectable in the first place — not even at zero passes (the original watermarked text, before any paraphrasing).

Here are the mean z-scores across paraphrase passes (threshold for detection: z > 2.0):

| Passes | Mean z-score | Detection Rate |
|--------|-------------|----------------|
| 0 | 0.94 | 0% |
| 1 | 0.25 | 0% |
| 2 | 0.72 | 0% |
| 3 | 0.19 | 0% |
| 5 | -0.05 | 0% |
| 10 | 0.09 | 0% |

The z-scores look like noise because they are noise. With only 1-11 signal words per 200-word text (out of our 15-pair vocabulary), the statistical test has essentially zero power.

We also tested watermark strength (delta parameter) and text length. Neither mattered. Delta showed a weak directional trend (mean z of -0.84 at delta=1.0 vs +0.48 at delta=4.0), but nothing approaching the detection threshold. Text length made no meaningful difference. Our predictive model achieved R² = 0.043 — explaining 4.3% of variance, which is to say: nothing.

## Why It Failed: The Signal Density Problem

The root cause is simple arithmetic. The Kirchenbauer watermark biases *every* token — in a 200-word text, that's ~200 data points for the statistical test. Our synonym substitution affects at most 15 specific word pairs. In a typical 200-word LLM-generated text, only 1-11 of those words appear.

For a z-score to exceed 2.0 with 100% green word fraction, you need at least 16 signal words. Our texts averaged about 3-5. The experiment was structurally unable to produce detections regardless of any other parameter.

This is not a subtle failure. It's a power analysis that should have been done before running experiments. A back-of-envelope calculation — "how many of my 15 signal words will appear in a 200-word text?" — would have revealed the problem immediately.

## What the Governance Framework Got Right (and Wrong)

This project was a deliberate governance pressure test. We applied our full research governance framework — 50 rules, pre-registered hypotheses, sanity validation, measurement tests — to a domain we'd never worked in before (watermark robustness instead of our usual multi-agent security focus).

**What worked:**
- **Pre-registration prevented post-hoc reframing.** We cannot claim we were "testing simulation fidelity all along." The hypotheses were about watermark robustness, and they failed.
- **Measurement tests (R46) validated the detection pipeline.** The code correctly computes z-scores. The pipeline works. The input signal just isn't there.
- **Honest reporting of negative results.** The finding taxonomy (OMISSION/DRIFT/HALLUCINATION/UNGROUNDED) forced us to categorize this correctly.

**What missed:**
- **E0 sanity validation used hand-crafted data.** Our sanity check sentence — "We need to help people get good results and show them how to use the tools to make things start working" — contained 10+ signal words, far more than any real LLM output. E0 passed, creating a false sense that the watermark worked. Lesson: sanity checks must use realistic data, not adversarial best-cases.
- **Gate 0.5 (design review) didn't include power analysis.** The experimental design was thorough — 4 baselines, 6 hypotheses, 5 ablation components — but nobody asked "will there be enough signal words for detection?" Adding a mandatory power analysis step to Gate 0.5 would have caught this.

## The Broader Lesson

Output-level text manipulation is fundamentally different from logit-level manipulation. This seems obvious in retrospect, but the distinction matters for anyone trying to study watermark robustness without access to model internals:

1. **Logit-level watermarking** biases every token (N ~ total tokens). High statistical power.
2. **Output-level watermarking** can only affect words that match a predefined vocabulary (N ~ vocabulary hits). Low statistical power unless the vocabulary is very large.

To properly study watermark robustness via API, you would need either:
- A synonym vocabulary of 200+ pairs (to ensure ~50+ signal words per text)
- Access to an open-source model with logit-level watermarking (LLaMA + the KGW library)

We chose to publish this negative result rather than quietly shelve it, because the failure mode is common: **approximating a mechanism at the wrong level of abstraction can silently invalidate an entire experimental design.** Pre-registration doesn't prevent bad designs — it just forces you to be honest about them.

## Reproducibility

All code, data, and experiment outputs are available in the repository. Experiments used Claude 3 Haiku (`claude-3-haiku-20240307`) with 5 fixed seeds (42, 123, 456, 789, 1024). Total API cost: approximately $5-10.

## Related Work

- Kirchenbauer et al. (2023) — "A Watermark for Large Language Models": The green-list watermarking method we approximated.
- Sadasivan et al. (2023) — "Can AI-Generated Text be Reliably Detected?": Theoretical argument that paraphrasing defeats detection. Our work was intended to provide empirical pass-count curves but could not due to simulation limitations.
- Krishna et al. (2023) — "Paraphrasing Evades AI-Generated Text Detectors": Showed DIPPER paraphraser defeats detectors. We planned to extend this to LLM-as-paraphraser.
- Christ et al. (2024) — "Undetectable Watermarks for Language Models": Theoretically robust watermark scheme. Highlights the gap between theoretical guarantees and practical deployment.
- Mitchell et al. (2023) — "DetectGPT": Zero-shot detection without watermarks. An alternative approach that doesn't require logit access.
- Zhao et al. (2023) — "Provable Robust Watermarking": Theoretical robustness bounds that our empirical study was meant to test.

---

*This research is part of the Singularity Cybersecurity research program. Securing AI from the architecture up.*

*[HYPOTHESIZED] This project is a governance pressure test — evaluating whether research governance generalizes across domains. The watermark robustness question remains open pending logit-level experiments.*
