"""Sitewide structural regression: missing local assets and broken game inline setup."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[2]


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        fields = {'a':'href', 'link':'href', 'script':'src', 'img':'src', 'iframe':'src'}
        value = dict(attrs).get(fields.get(tag, ''))
        if value:
            self.refs.append(value)


def test_all_root_and_game_pages_reference_existing_local_assets():
    pages = list(ROOT.glob('*.html')) + list((ROOT/'games').rglob('*.html'))
    assert len(pages) >= 500
    bad = []
    for page in pages:
        parser = References()
        html = page.read_text(encoding='utf-8')
        parser.feed(html)
        assert html.count('<script') == html.count('</script>'), str(page)
        for ref in parser.refs:
            if ref.startswith(('https:', 'http:', 'data:', '//', '#', 'mailto:', 'javascript:')):
                continue
            path = urlsplit(ref).path
            if not path:
                continue
            target = ROOT/path.lstrip('/') if path.startswith('/') else page.parent/path
            if not target.is_file():
                bad.append((str(page.relative_to(ROOT)), ref))
    assert not bad, bad[:30]


def test_all_catalogue_game_pages_have_valid_bootstrap_script():
    games = list((ROOT/'games/knowledge').rglob('*.html'))
    assert len(games) >= 400
    broken = []
    for game in games:
        html = game.read_text(encoding='utf-8')
        if '<script>window.MATH_GAME=' not in html or 'api-config.js' not in html:
            broken.append(str(game.relative_to(ROOT)))
        if re.search(r'<script\s+src="[^"\n]*<script', html):
            broken.append(str(game.relative_to(ROOT)))
    assert not broken, broken[:30]


def test_study_and_geometry_pages_require_login_in_frontend():
    protected = [
        'practise.html', 'practice.html', 'account.html', 'chat.html',
        'battle.html', 'learning-path.html', 'learn.html', 'learning.html',
        'geometry-studio.html', 'geometry-learning.html', 'geometry-lab.html',
        'study-suite.html', 'curriculum-studio.html', 'learning-progress.html',
        'final-features.html',
    ]
    guard = (ROOT/'js/protected-pages.js').read_text(encoding='utf-8')
    for name in protected:
        assert name in guard, name
        html = (ROOT/name).read_text(encoding='utf-8')
        assert 'src="js/protected-pages.js"' in html, name
