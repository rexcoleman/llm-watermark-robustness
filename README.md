# FP-18: LLM Watermark Robustness Under Adversarial Paraphrasing

Cross-model paraphrasing drops Kirchenbauer watermark detection from 100% to 60% in a single pass. After 10 passes, it plateaus at 40%. The watermark is partially robust — but not enough for adversarial settings.

**Blog post:** [How Many Rewrites to Strip a Watermark?](https://rexcoleman.dev/posts/llm-watermark-robustness/)

## Key Results

| Metric | Value |
|--------|-------|
| Detection at pass=0 | 100% (z > 4.0) |
| Detection after 1 pass | 60% |
| Detection plateau (10 passes) | 40% |
| Watermark model | GPT-2 (124M) with logit access |
| Paraphrase model | Claude 3 Haiku (cross-model) |
| Seeds | 42, 123, 456, 789, 1024 |

## Quick Start

```bash
pip install -r requirements.txt
python scripts/run_experiments.py --experiments E0,E1
```

## Experiments

- **E0:** Sanity — dose-response at δ=0.5,1.0,2.0,4.0
- **E1:** Multi-pass paraphrase decay curve (1-10 passes)
- **E3:** Token length sensitivity (50, 150, 300 tokens)
- **E4:** Semantic preservation vs detection tradeoff
- **E5/E6:** Model comparison and combined attacks

Built with [govML](https://rexcoleman.dev/posts/govml-methodology/) governance. 6 pre-registered hypotheses. 5 experiments. Full reproduction via `bash reproduce.sh`.
