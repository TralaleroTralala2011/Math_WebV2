from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_every_optional_api_page_initializes_backend_first():
    pages=[]
    for page in ROOT.glob("*.html"):
        html=page.read_text(encoding="utf-8")
        if "js/optional-api-v33.js" not in html: continue
        pages.append(page.name)
        assert "js/api-config.js" in html, page.name
        assert html.index("js/api-config.js") < html.index("js/optional-api-v33.js"), page.name
    assert len(pages)>=19
