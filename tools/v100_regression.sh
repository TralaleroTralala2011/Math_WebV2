#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
PYTHONPATH=. python -m pytest -q \
 tests/test_api_integration.py tests/test_learning_assignments.py \
 tests/test_geometry_diagrams.py tests/test_additional_solid_diagrams.py \
 tests/test_geometry_45_topic_expansion.py tests/test_geometry_curriculum.py \
 tests/test_geometry_topic_coverage_306.py
cd ..
node --check js/battle.js
node --check js/practise.js
node --check js/practice-mathgeo-bridge.js
node tools/v97_triangle_sss_test.cjs geometry-studio.html
printf '\nRegression subset passed. Browser Battle/Admin end-to-end remains unverified.\n'
