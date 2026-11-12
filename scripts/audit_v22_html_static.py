"""Check 20 shipped HTML pages for viewport and local asset integrity.
Does not replace desktop/mobile visual browser testing."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
report=[]
for page in sorted(ROOT.glob('*.html')):
    doc=BeautifulSoup(page.read_text(encoding='utf-8',errors='replace'),'html.parser')
    problems=[]
    viewport=doc.find('meta',attrs={'name':'viewport'})
    if viewport is None:problems.append('missing viewport')
    for tag,attr in (('script','src'),('link','href'),('img','src')):
        for el in doc.find_all(tag):
            url=el.get(attr)
            if not url:continue
            parts=urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path or parts.path.startswith('/') or parts.path.startswith('data:'):continue
            path=unquote(parts.path)
            if not (ROOT/path).is_file():problems.append(f'local asset missing: {url}')
    report.append({'page':page.name,'viewport':bool(viewport),'problems':problems})
output={'audit_type':'Static HTML only, not visual/browser or JS runtime testing','pages':len(report),'issues':sum(len(x['problems']) for x in report),'page_results':report}
print(json.dumps(output,ensure_ascii=False,indent=2))
raise SystemExit(int(output['issues']>0))
