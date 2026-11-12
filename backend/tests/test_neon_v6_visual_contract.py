"""Static contract tests for the screenshot-aligned shared interface.

These tests verify wiring and separation, not pixel-perfect device rendering.
"""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PAGES=('index.html','practice.html','practise.html','learn.html','learning.html',
       'learning-path.html','battle.html','chat.html','account.html','login.html',
       'register.html','geometry-studio.html','geometry-lab.html',
       'geometry-learning.html','learning-progress.html','curriculum-studio.html',
       'study-suite.html','final-features.html','trial-practise.html')


def test_shared_neon_theme_on_every_primary_student_page():
    for page in PAGES:
        content=(ROOT/page).read_text(encoding='utf-8')
        assert 'css/neon-v6.css?v=6' in content,page
        assert 'js/neon-v6-experience.js?v=6' in content,page
        assert 'js/admin-neon-v6.js' not in content,page


def test_admin_has_its_own_dashboard_script():
    admin=(ROOT/'admin.html').read_text(encoding='utf-8')
    assert 'css/neon-v6.css?v=6' in admin
    assert 'js/admin-neon-v6.js?v=6' in admin
    assert 'js/neon-v6-experience.js' not in admin
    assert 'href="learning-path.html">Xem giao diện Lộ trình học' not in admin


def test_all_visual_assets_exist_and_have_responsive_rules():
    for file in ('css/neon-v6.css','js/neon-v6-experience.js','js/admin-neon-v6.js','js/roadmap-v5.js'):
        assert (ROOT/file).is_file(),file
    style=(ROOT/'css/neon-v6.css').read_text(encoding='utf-8')
    assert '@media(max-width:760px)' in style
    assert '@media(max-width:480px)' in style
    assert 'mw-v6-learning-actions' in style
    assert 'mw-v6-roadmap-grid' in style
    assert 'mw-v5-admin' in style


def test_roadmap_keeps_gate_and_server_exam_contract():
    code=(ROOT/'js/roadmap-v5.js').read_text(encoding='utf-8')
    assert "if(!status?.placement_complete)" in code
    assert "begin('placement')" in code
    assert "begin('topic',t.id)" in code
    assert '≥25/30' in code
    assert "'/submit/'" in code
    assert "review(results)" in code
