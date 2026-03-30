# LLM Watermark Robustness Under Adversarial Paraphrasing

**Real Kirchenbauer watermarking produces z=8.44 detection signal — but cross-model paraphrasing degrades it from 100% detection at pass 0 to progressive failure. A single Claude Haiku paraphrase pass strips green-list token patterns that the watermark depends on.**

**Blog post:** [LLM Watermarks Break After One Paraphrase Pass](https://rexcoleman.dev/posts/llm-watermark-robustness/)

![govML](https://img.shields.io/badge/govML-v3.3-blue) ![Quality](https://img.shields.io/badge/quality-8.3-brightgreen) ![License](https://img.shields.io/badge/license-MIT-green)

![Key Result](outputs/figures/e1_detection_rate.png)

## Key Results

| Condition | Detection Rate | z-score (mean ± std) |
|-----------|---------------|---------------------|
| Pass 0 (no paraphrase) | 100% | 9.64 ± 1.03 |
| Pass 1 (single paraphrase) | Degraded | Progressive z-score decay |
| Clean (unwatermarked) | 0% | -0.08 |
| Watermark signal gap | — | ~8.5σ separation |

## Quick Start

```bash
git clone https://github.com/rexcoleman/llm-watermark-robustness
cd llm-watermark-robustness
pip install -e .
bash reproduce.sh
```

## Project Structure

```
FINDINGS.md # Research findings with pre-registered hypotheses and full results
EXPERIMENTAL_DESIGN.md # Pre-registered experimental design and methodology
HYPOTHESIS_REGISTRY.md # Hypothesis predictions, results, and verdicts
reproduce.sh # One-command reproduction of all experiments
governance.yaml # govML governance configuration
CITATION.cff # Citation metadata
LICENSE # MIT License
pyproject.toml # Python project configuration
scripts/ # Experiment and analysis scripts
src/ # Source code
tests/ # Test suite
outputs/ # Experiment outputs and results
config/ # Configuration files
docs/ # Documentation and decision records
```

## Methodology

See [FINDINGS.md](FINDINGS.md) and [EXPERIMENTAL_DESIGN.md](EXPERIMENTAL_DESIGN.md) for detailed methodology, pre-registered hypotheses, and full experimental results with multi-seed validation.

## Citation

If you use this work, please cite using the metadata in [CITATION.cff](CITATION.cff).

## License

[MIT](LICENSE) 2026 Rex Coleman

---

Governed by [govML](https://rexcoleman.dev/posts/govml-methodology/) v3.3
