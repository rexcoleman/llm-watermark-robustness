#!/bin/bash
set -e
echo "=== FP-18 Reproduce Pipeline ==="

# Gate 0.5
grep -qi "lock_commit.*TO BE SET\|lock_commit.*PENDING" EXPERIMENTAL_DESIGN.md && echo "FAIL: lock_commit not set" && exit 1 || echo "PASS: lock_commit set"

# R35: nohup
mkdir -p ~/compute_logs
pip install numpy anthropic pytest 2>&1 | tail -3

# Tests (R46)
echo "--- Tests ---"
python -m pytest tests/ -v

# E0 Sanity (R47)
echo "--- E0: Sanity ---"
python -u scripts/run_experiments.py --experiments E0

# Experiments (R35 nohup)
echo "--- Experiments (nohup) ---"
nohup python3 -u scripts/run_experiments.py --experiments E1,E3,E4,E5,E6 > ~/compute_logs/fp18_experiments.log 2>&1 &
echo "PID: $! — Log: ~/compute_logs/fp18_experiments.log"

# Gate Validation (R50)
echo "--- Gate Validation (R50) ---"
bash ~/ml-governance-templates/scripts/check_all_gates.sh .
