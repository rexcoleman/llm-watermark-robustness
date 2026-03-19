# Substack Introduction — FP-18

**Subject line:** I ran 45 experiments and got zero results. Here's why that matters.

---

I spent last week building a watermark robustness testing framework. Pre-registered six hypotheses. Designed five experiments. Ran them against real Claude API output.

Detection rate: 0%. Across every single condition.

The full post explains what went wrong (output-level synonym substitution can't approximate logit-level watermarking), what the governance framework caught (pre-registration forced honest reporting), and what it missed (sanity checks on unrealistic data).

If you're working on AI-generated text detection, the failure mode is worth understanding: approximating a mechanism at the wrong abstraction level can silently invalidate your entire experimental design.

**Read the full analysis →** [link]
