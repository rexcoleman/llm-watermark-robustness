# LinkedIn Post — LLM Watermark Robustness

I pre-registered 6 hypotheses about LLM watermark robustness. First attempt: 0% detection across 45 conditions.

So I rebuilt the experiment from scratch.

v1 approximated watermarks at the output level (synonym substitution). Only ~5 signal words per text. A power analysis would have flagged this immediately.

v2 implements real Kirchenbauer watermarking with GPT-2 logit access. Result: z=8.44 at baseline (84.6% green tokens), 100% detection rate with zero paraphrasing.

Then the real question: how many Claude Haiku paraphrase passes does it take to strip the watermark? Cross-model attack — the paraphraser has no knowledge of the watermark key.

Key findings from the v1 failure:
- Output-level watermark approximation is not a valid proxy for logit-level watermarking (~30x signal density gap)
- Pre-registration forced honest reporting of the negative result
- Two governance fixes now prevent repeats: mandatory power analysis (LL-93) and realistic sanity data (LL-94)

The governance framework caught what intuition missed. A back-of-envelope calculation would have saved a week.

Are you relying on watermarks for AI content detection? What's your fallback?

#AISecurity #Watermarking #LLMSecurity #AdversarialML #ResearchGovernance

---

> First comment: "Full analysis with paraphrase-removal curves: [blog URL]"
