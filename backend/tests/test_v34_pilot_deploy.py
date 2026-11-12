"""Release contract tests: GitHub static frontend, Render API and packaged B54 data."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from fastapi.testclient import TestClient
from app.main import app

ROOT=Path(__file__).resolve().parents[2]

def test_bank_seed_matches_versioned_manifest():
    base=ROOT/'backend/app/ai/storage'
    manifest=json.loads((base/'v254_seed_manifest.json').read_text())
    assert (base/'v254_candidates.seed.zip').is_file()
    with zipfile.ZipFile(base/'v254_candidates.seed.zip') as archive:
        assert archive.namelist()==['v254_candidates.sqlite']
        assert archive.testzip() is None
        assert archive.getinfo('v254_candidates.sqlite').file_size == manifest['bytes']
    assert manifest['questions']==83298 and manifest['b54_word_labels']==95514

def test_all_feature_pages_use_canonical_backend_url():
    pages=['study-suite.html','curriculum-studio.html','final-features.html','learning-progress.html']
    for p in pages:
        html=(ROOT/p).read_text(encoding='utf-8')
        assert 'js/api-config.js' in html, p
    for file in ['js/study-suite.js','js/curriculum-studio.js','js/learning-progress.js']:
        source=(ROOT/file).read_text(encoding='utf-8')
        assert 'window.MATHWEB_API_URL' in source, file
        assert 'mathweb_api_base' not in source

def test_render_pilot_durable_storage_contract():
    blueprint=(ROOT/'render.yaml').read_text()
    for required in ['plan: starter','disk:','mountPath: /var/data','MATHWEB_DATA_DIR','MATHWEB_DB_PATH',
                     'MATHWEB_BOOTSTRAP_ADMIN_PASSWORD','restore_v254_bank.py']:
        assert required in blueprint
    for module in ['learning_progress_routes.py','study_suite_routes.py','final_features_routes.py']:
        assert 'MATHWEB_DATA_DIR' in (ROOT/'backend/app'/module).read_text()

def test_pages_cors_preflight_and_unauthenticated_security():
    client=TestClient(app)
    good=client.options('/api/auth/login',headers={
        'Origin':'https://tralalerotralala2011.github.io',
        'Access-Control-Request-Method':'POST',
        'Access-Control-Request-Headers':'content-type'})
    assert good.status_code==200,good.text
    assert good.headers.get('access-control-allow-origin')=='https://tralalerotralala2011.github.io'
    bad=client.options('/api/auth/login',headers={
        'Origin':'https://unknown-attacker.example',
        'Access-Control-Request-Method':'POST'})
    assert bad.headers.get('access-control-allow-origin') is None
    assert client.get('/api/auth/me').status_code==401
