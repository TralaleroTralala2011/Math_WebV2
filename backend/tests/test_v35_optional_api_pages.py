from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_all_pages_load_capability_gate_before_neon_experience():
    dependent = ('js/neon-v6-experience.js', 'js/neon-v7-experience.js', 'js/learn-neon-v5.js')
    pages = []
    for page in ROOT.glob('*.html'):
        text = page.read_text(encoding='utf-8')
        positions = [text.index(dep) for dep in dependent if dep in text]
        if not positions:
            continue
        pages.append(page.name)
        assert 'js/optional-api-v33.js' in text, f'{page.name}: capability gate missing'
        assert text.index('js/optional-api-v33.js') < min(positions), f'{page.name}: incorrect script order'
    assert len(pages) >= 19
