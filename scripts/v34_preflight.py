"""Release gate for GitHub Pages frontend and Render API.

Check real assets, deployment settings, database contents and API route contract.
Fail CI rather than publishing a broken update. No network access required.
"""
from __future__ import annotations
import json, re, sqlite3, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob('*.html'))
REQUIRED_PATHS = {
    '/health', '/api/auth/login', '/api/auth/register', '/api/auth/me',
    '/api/matchmaking/invite', '/api/games/activity-heatmap',
    '/api/roadmap-v2/status/{grade}', '/api/roadmap-v2/tutor/{grade}',
    '/api/learning-progress/overview', '/api/study-suite/bank',
    '/api/final-features/lessons', '/api/curriculum/graph',
}
class Refs(HTMLParser):
    def __init__(self): super().__init__(); self.refs=[]
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        for key in ('src','href'):
            if data.get(key): self.refs.append((tag,key,data[key]))

def run():
    failures=[]
    if len(PAGES)<20: failures.append(f'expected >=20 public pages, got {len(PAGES)}')
    count=0
    for page in PAGES:
        s=page.read_text(encoding='utf-8')
        doc=Refs(); doc.feed(s)
        api_scripts=['js/curriculum-studio.js','js/learning-progress.js','js/study-suite.js']
        if (any(x in s for x in api_scripts) or page.name=='final-features.html') and 'js/api-config.js' not in s:
            failures.append(f'{page.name}: missing canonical api-config.js')
        for tag,key,ref in doc.refs:
            ref=ref.strip()
            if not ref or ref.startswith(('#','//','http:','https:','data:','mailto:','tel:','javascript:')):continue
            if ref.startswith('api/'):continue
            ref=unquote(urlsplit(ref).path)
            if not ref or ref.endswith('/'):continue
            path=(ROOT/ref.lstrip('/'))
            # root docs only: inherited paths are resolved against root.
            if not path.is_file():
                # Ignore href links that intentionally point to remote / dynamic pages.
                failures.append(f'{page.name}: {key}={ref} not found')
            count+=1
    from app.main import app
    routes={route.path for route in app.routes}
    for route in REQUIRED_PATHS:
        if route not in routes: failures.append(f'API route missing: {route}')
    with sqlite3.connect(f'file:{(ROOT/"backend/app/ai/storage/v254_candidates.sqlite").as_posix()}?mode=ro',uri=True) as db:
        integ=db.execute('PRAGMA quick_check').fetchone()[0]
        counts={table:db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in ('questions','b54_word_labels')}
    if integ!='ok' or counts!={'questions':83298,'b54_word_labels':95514}:
        failures.append(f'database mismatch: {integ} {counts}')
    yaml=(ROOT/'render.yaml').read_text()
    if not all(word in yaml for word in ['disk:', 'MATHWEB_DB_PATH', 'MATHWEB_DATA_DIR', 'restore_v254_bank.py']):
        failures.append('Render blueprint missing bank bootstrap or persistent data')
    workflow=(ROOT/'.github/workflows/pages.yml').read_text()
    if not all(word in workflow for word in ('/tmp/mathweb-public','--exclude=\'backend\'','v34_preflight.py','pytest -q')):
        failures.append('GitHub action missing secure publishing QA gates')
    result={'pages':len(PAGES),'checked_relative_refs':count,'bank':counts,'api_routes':len(routes),'failures':failures}
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 1 if failures else 0

if __name__=='__main__':sys.exit(run())
