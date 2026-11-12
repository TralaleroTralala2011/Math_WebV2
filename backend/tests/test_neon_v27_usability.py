"""V27 UI contract: prevent legacy hidden notification trigger, misleading geometry and bad mobile behavior."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_header_scrolls_with_page_and_battle_fits_viewport():
    css=(ROOT/'css/neon-v27-usability.css').read_text(encoding='utf-8')
    assert '#mw-v5-header' in css and 'position:relative!important' in css
    assert 'height:100dvh!important' in css
    assert 'body.mw-v27-battle' in css and 'overflow:hidden!important' in css
    assert '@media(max-width:850px)' in css

def test_notification_control_moves_out_of_hidden_legacy_nav():
    js=(ROOT/'js/neon-v27-usability.js').read_text(encoding='utf-8')
    assert "button.id='notificationButton'" in js
    assert "oldButton.id='mw-v27-legacy-notification-button'" in js
    assert "document.body.append(panel)" in js
    assert 'window.MATHWEB_NOTIFICATIONS.openNotifications()' in js

def test_geometry_inline_without_fabricated_measurements():
    js=(ROOT/'js/geometry-inline-v27.js').read_text(encoding='utf-8')
    roadmap=(ROOT/'js/roadmap-v5.js').read_text(encoding='utf-8')
    assert 'MATHWEB_INLINE_GEOMETRY?.render(q)' in roadmap
    assert "Dựng hình với MathGeo Studio Pro" not in roadmap
    assert 'ac+bc>ab' in js and 'ab+ac>bc' in js
    assert 'KHÔNG dùng hình để suy ra độ dài' in js

def test_updated_design_loaded_on_student_pages():
    for name in ('index.html','learn.html','learning-path.html','battle.html','practice.html','chat.html','account.html'):
        markup=(ROOT/name).read_text(encoding='utf-8')
        assert 'neon-v27-usability.css' in markup, name
        assert 'neon-v27-usability.js' in markup, name
    markup=(ROOT/'learning-path.html').read_text(encoding='utf-8')
    assert markup.index('geometry-inline-v27.js')<markup.index('roadmap-v5.js')
