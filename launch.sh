#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
YEAR="${YEAR:-2025}"
source virtual-env/bin/activate
python3 ibkr.py
capgains calc master.csv "$YEAR"
