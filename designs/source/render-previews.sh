#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
python3.11 "${SCRIPT_DIR}/render-previews.py"
