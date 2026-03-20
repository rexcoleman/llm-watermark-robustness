# For: general security Discord / r/netsec

measured how many paraphrase passes it takes to strip a Kirchenbauer watermark. watermarked with GPT-2, paraphrased with Claude Haiku (cross-model attack). one pass drops detection from 100% to 60%, then it plateaus — 40% still detectable after 10 passes.

```
passes  z-score        detection
0       9.64 ± 1.03    100%
1       5.21 ± 1.74     60%
3       4.72 ± 0.96     60%
10      3.89 ± 1.26     40%
```

first attempt (v1) used synonym substitution and got 0% detection across 45 conditions — not because watermarks are robust, because the attack was structurally too weak. logit-level watermarking biases every token (~200 data points). synonym substitution touches ~5. that's a 30x signal density gap that no amount of tuning can fix.

cross-model paraphrasing is the real threat to watermark schemes. one pass through a different model rewrites enough tokens to break detection for 60% of samples, but the remaining 40% are surprisingly persistent — the watermark signal is distributed enough that some survives even aggressive rewriting.

implications: watermarks aren't useless but they're not reliable for high-stakes attribution. if you're building content provenance systems, watermarks are one signal among many, not a standalone solution.

anyone working on watermark robustness? curious whether newer schemes (SynthID, etc.) hold up better against cross-model paraphrasing.
