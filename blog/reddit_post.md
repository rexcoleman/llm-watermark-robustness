# I tested how many LLM paraphrase passes it takes to strip a watermark — 40% of texts are still detectable after 10 rewrites

I implemented Kirchenbauer green-list watermarking on GPT-2 and attacked it with Claude Haiku as a cross-model paraphraser. One pass drops detection from 100% to 60%. Then it plateaus — even after 10 passes, 40% of watermarked texts are still detectable. The watermark is more robust to paraphrasing than theoretical work suggested.

This was a cross-model attack: watermark with GPT-2 (direct logit access, delta=2.0 bias), paraphrase with Claude Haiku (completely different architecture, no knowledge of the watermarking key). This tests the realistic scenario where an adversary doesn't know the watermark scheme but can access a cheap LLM to rewrite text. At pass=0, watermarked text has a mean z-score of 9.64 with 100% detection. After 1 pass: z=5.21, 60% detection. After 10 passes: z=3.89, 40% detection.

The project has an honest failure story worth sharing. My first attempt (v1) used output-level synonym substitution with 15 word pairs. Result: 0% detection across 45 conditions — not because watermarks are robust, but because the simulation was structurally too weak. Only ~5 signal words per text vs ~149 for real Kirchenbauer watermarking. A 30x signal density gap. A power analysis at design time would have caught this.

Key takeaways:

- **Cross-model paraphrasing degrades watermarks but doesn't destroy them** — 40% detection survives 10 passes
- **The degradation curve has diminishing returns** — most damage happens in pass 1 (100% to 60%), subsequent passes barely move the needle
- **Logit-level watermarking is fundamentally stronger than output-level** — ~149 signal tokens per text vs ~5 for synonym substitution
- **Zero false positives** — unwatermarked text scores z=-0.08, well below the z=4.0 detection threshold
- **Sanity validation before experiments matters** — without E0 checks, v1 would have been published with structurally invalid results

Methodology: Kirchenbauer et al. (2023) green-list watermark, GPT-2 124M via HuggingFace, Claude 3 Haiku paraphraser, 5 fixed seeds, 5 pre-registered hypotheses. Full reproduce.sh included.

Repo: [github.com/rexcoleman/llm-watermark-robustness](https://github.com/rexcoleman/llm-watermark-robustness)

Code is open source with all experiment data. Happy to answer questions.
