#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
PYTHONPATH=. python -m pytest -q tests/test_api_integration.py tests/test_learning_assignments.py tests/test_geometry_diagrams.py tests/test_additional_solid_diagrams.py
cd ..
node --check js/battle.js
node --check js/practise.js
node --check js/practice-mathgeo-bridge.js
