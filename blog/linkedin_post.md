# LinkedIn Post — FP-18 Negative Result

I pre-registered 6 hypotheses about LLM watermark robustness. Then I ran the experiments.

Detection rate across 45 conditions: 0%.

Not because watermarks are robust — because my simulation was too weak to test them.

The setup: I approximated the Kirchenbauer green-list watermark at the output level (synonym substitution) since I couldn't access model logits through the API. Tested paraphrasing attacks across 6 pass counts, 3 text lengths, 3 watermark strengths.

The problem: my 15-pair synonym vocabulary produces only 1-11 signal words per 200-word text. You need 16+ for statistical detection. The experiment was structurally unable to produce results regardless of other parameters.

The governance lesson: my E0 sanity check passed — because it used a hand-crafted sentence stuffed with signal words. Real LLM output doesn't look like that. Sanity validation that doesn't use realistic data can mask fundamental design flaws.

What I'd do differently:
→ Back-of-envelope power analysis BEFORE burning API budget
→ E0 sanity on actual model outputs, not constructed examples
→ Open-source model with logit access for real Kirchenbauer watermarking

Publishing the negative result because the failure mode is instructive: approximating a mechanism at the wrong level of abstraction silently invalidates your experimental design.

Pre-registration doesn't prevent bad designs. It just forces you to be honest about them.

#AIResearch #Watermarking #NegativeResults #AISecurity #MachineLearning
