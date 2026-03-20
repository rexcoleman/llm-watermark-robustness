# Conference Abstract — LLM Watermark Robustness

**Title:** Cross-Model Paraphrase Attacks on Kirchenbauer Watermarks: Empirical Removal Curves from a Pre-Registered Study

**Target venue:** AISec Workshop (ACM CCS 2026) [HYPOTHESIZED]

**Authors:** Rex Coleman, Singularity Cybersecurity LLC

---

## Abstract (250 words)

We present empirical paraphrase-removal curves for the Kirchenbauer et al. (2023) green-list watermark, measuring how cross-model paraphrasing degrades watermark detection. Using GPT-2 (124M) with logit-level watermark injection (δ=2.0, γ=0.5) and Claude Haiku as a cross-model paraphraser, we test six pre-registered hypotheses across paraphrase pass count (0-10), watermark strength (δ=1.0-4.0), and text length (50-300 tokens).

At zero paraphrase passes, watermarked text produces strong detection signal: mean z=9.64±1.03 across 5 seeds (threshold z=4.0), with 100% detection rate and 84.6% green-list token fraction. Iterative cross-model paraphrasing progressively degrades this signal. We report the full detection-rate decay curve and identify the pass count at which detection drops below 50%.

This study also documents a methodology recovery: an initial attempt using output-level synonym substitution (v1) produced 0% detection across 45 conditions — a structural failure where ~5 signal words per text were insufficient for statistical detection. The v1 negative result, honestly reported under pre-registered hypotheses, motivated the v2 implementation with real logit access (~149 tokens scored per text). This v1→v2 transition yielded two governance improvements now applied to all future projects: mandatory power analysis at experiment design review (LL-93) and realistic-data E0 sanity validation (LL-94).

Our contribution is an empirical cost-detectability tradeoff surface that practitioners can use to assess watermark viability under adversarial paraphrasing, plus a governance case study in recovering from a pre-registered negative result.

**Keywords:** watermarking, LLM security, adversarial robustness, paraphrase attacks, research governance

---

## Author Bio

**Rex Coleman** is the founder of Singularity Cybersecurity LLC, focused on AI security research. His research spans security OF AI systems (multi-agent delegation, prompt injection, model behavioral fingerprinting) and security FROM AI (watermark robustness, AI-generated content detection). Previously, he worked in data analytics and sales at FireEye/Mandiant. He holds a Master's in Computer Science from Georgia Tech (Machine Learning specialization). Securing AI from the architecture up.
