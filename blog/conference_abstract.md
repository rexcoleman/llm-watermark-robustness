# Conference Abstract — FP-18

**Title:** Output-Level Watermark Simulation Fails to Produce Detectable Signal: Lessons from a Pre-Registered Negative Result

**Target venue:** AISec Workshop (ACM CCS 2026) [HYPOTHESIZED]

**Authors:** Rex Coleman, Singularity Cybersecurity LLC

---

## Abstract (250 words)

We report a pre-registered negative result in LLM watermark robustness testing. We approximated the Kirchenbauer et al. (2023) green-list watermark at the output level using synonym substitution (15 word pairs) and measured detection rates under iterative LLM paraphrasing (0-10 passes) across varying text lengths (50-500 words) and watermark strengths (delta 1.0-4.0). All six pre-registered hypotheses about watermark degradation under paraphrasing were resolved: five as UNSUPPORTED (untestable) and one as trivially SUPPORTED.

The root cause is a signal density failure: output-level synonym substitution produces only 1-11 signal words per 200-word text, well below the minimum 16 required for z > 2.0 detection. The Kirchenbauer method biases every token at the logit level (~200 data points per text); our approximation biases only vocabulary-matched words (~3-5 per text). This structural insufficiency renders all robustness measurements void.

We identify two governance failures that allowed the experiment to proceed: (1) E0 sanity validation used a hand-crafted sentence with artificially high signal density, masking the power deficit; (2) the experimental design review (Gate 0.5) lacked a mandatory power analysis step. We also identify a governance success: pre-registered hypotheses prevented post-hoc reframing of the negative result.

Our contribution is methodological: we demonstrate that output-level watermark approximation is not a valid proxy for logit-level watermarking when testing robustness, and we propose concrete governance improvements (realistic E0 data, mandatory power analysis) to prevent similar failures.

**Keywords:** watermarking, LLM security, negative results, research governance, paraphrase attacks
