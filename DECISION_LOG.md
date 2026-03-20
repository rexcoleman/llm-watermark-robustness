# DECISION LOG — FP-18: LLM Watermark Robustness

> **R52 (Autonomous Research Quality Loop) iteration tracking.**
> Each iteration records: score before, gaps found, fixes applied, score after.

---

## Iteration 0 — Initial (v1 synonym simulation) — 2026-03-19

- **Score:** 5/10 (self-assessed) | check_all_gates: 33 PASS, 0 FAIL, 12 WARN
- **Structural gap identified:** 0% detection across 45 conditions. Output-level synonym substitution (15 pairs) produces 1-11 signal words — insufficient for z > 2.0 detection.
- **Root cause:** Simulation fidelity failure. Output-level ≠ logit-level watermarking.
- **Action:** ESCALATE TO HUMAN — structural design flaw.
- **Human decision:** Rebuild with real Kirchenbauer watermarking using GPT-2 logit access.
- **Governance lessons:** LL-93 (power analysis), LL-94 (realistic E0).
- **API cost:** ~$5-10 (Claude Haiku for paraphrasing)

## Iteration 1 — v2 real Kirchenbauer — 2026-03-20

- **Score before:** 5/10 (v1)
- **Changes:** Implemented `kirchenbauer_watermark.py` with GPT-2 logit access. E0 PASSES 4/4 (z=8.44, 149 tokens, green=0.846).
- **E1 pass=0:** mean z=9.64 ± 1.03, detection_rate=100% (vs 0% in v1).
- **Experiments running:** E1, E3, E4, E5, E6 via nohup.
- **Fixable gaps addressed:** (pending gate re-run after experiments)
- **Score after:** TBD — waiting for experiments to complete.
- **API cost:** ~$5-10 estimated (Claude Haiku paraphrasing)

### Quality Loop — 2026-03-20T00:30:58+00:00
- Score: 8.7/10 | PASS: 39 | FAIL: 0 | WARN: 6
- Action: PASS
- Structural: 0
0 | Fixable: 7
