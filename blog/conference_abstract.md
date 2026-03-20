# Conference Abstract — LLM Watermark Robustness

**Title:** Cross-Model Paraphrase Attacks on Kirchenbauer Watermarks: Empirical Removal Curves from a Pre-Registered Study

**Target venue:** AISec Workshop (ACM CCS 2026) [HYPOTHESIZED]

**Authors:** Rex Coleman, Singularity Cybersecurity LLC

---

## Abstract (250 words)

AI-generated text watermarking is proposed as a detection mechanism, but how robust are these watermarks against adversarial removal? Cross-model paraphrasing — using one LLM to rewrite another's watermarked output — is the most accessible attack, yet empirical removal curves do not exist in the literature.

We measure paraphrase-removal curves for the Kirchenbauer et al. (2023) green-list watermark using GPT-2 (124M) with logit-level injection and Claude Haiku as a cross-model paraphraser, testing six pre-registered hypotheses across pass count (0-10), watermark strength (delta 1.0-4.0), and text length (50-300 tokens). At baseline: z=9.64, 100% detection. Iterative paraphrasing progressively degrades this signal; we identify the pass count at which detection drops below 50%. An initial v1 approach using synonym substitution produced 0% detection across 45 conditions — a structural failure that motivated our v2 implementation and yielded two governance improvements (mandatory power analysis, E0 sanity validation).

Attendees will leave with an empirical cost-detectability tradeoff surface for assessing watermark viability under adversarial paraphrasing, plus a reproducible methodology for generating removal curves on their own watermark implementations.

**Keywords:** watermarking, LLM security, adversarial robustness, paraphrase attacks, research governance

---

## Author Bio

**Rex Coleman** is the founder of Singularity Cybersecurity LLC, focused on AI security research. His research spans security OF AI systems (multi-agent delegation, prompt injection, model behavioral fingerprinting) and security FROM AI (watermark robustness, AI-generated content detection). Previously, he worked in data analytics and sales at FireEye/Mandiant. He holds a Master's in Computer Science from Georgia Tech (Machine Learning specialization). Securing AI from the architecture up.
