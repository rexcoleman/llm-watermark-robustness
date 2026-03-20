# Substack Introduction — LLM Watermark Robustness

**Subject line:** How many rewrites to strip a watermark? I measured it.

---

Can you strip a watermark from AI-generated text by paraphrasing it with another LLM?

I tested this empirically — real Kirchenbauer green-list watermarking on GPT-2, with Claude Haiku as a cross-model paraphraser. Six pre-registered hypotheses. Five experiments.

At baseline: 100% detection, z-score of 9.64. Then we started paraphrasing.

The full post includes the paraphrase-removal curves, a v1 failure recovery story (my first attempt got 0% detection because we approximated the watermark wrong), and the governance lessons that prevented me from quietly shelving the negative result.

If you're thinking about watermark viability for AI content detection, this is the empirical data you need.

**Read the full analysis →** [link]
