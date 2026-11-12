"""V29 user-approved behaviors: dashboard on Account, unchanged Home and Battle,
non-destructive notifications, guest-only trial, and persistent sessions."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def test_dashboard_moved_to_account_and_original_pages_preserved():
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    battle=(ROOT/'battle.html').read_text(encoding='utf-8')
    assert 'Học Toán' in index and 'thú vị hơn' in index
    assert 'id="battleMenu"' in battle
    assert 'js/neon-v5.js' not in index and 'js/neon-v6-experience.js' not in battle
    assert 'js/neon-v5.js' in (ROOT/'account.html').read_text(encoding='utf-8')
    v5=(ROOT/'js/neon-v5.js').read_text(encoding='utf-8')
    v6=(ROOT/'js/neon-v6-experience.js').read_text(encoding='utf-8')
    v7=(ROOT/'js/neon-v7-experience.js').read_text(encoding='utf-8')
    assert "if(page==='account.html')home()" in v5
    assert "if(page==='account.html')home()" in v6
    assert "if(page!=='account.html')return" in v7
    assert 'extra.append(oldMain)' not in v5


def test_desktop_legacy_nav_and_mobile_notification_bridge():
    css=(ROOT/'css/v29-user-preferences.css').read_text(encoding='utf-8')
    bridge=(ROOT/'js/neon-v27-usability.js').read_text(encoding='utf-8')
    assert 'header.navbar:not(#mw-v5-header){display:flex!important}' in css
    assert 'header#mw-v5-header{display:none!important}' in css
    assert "existing.click()" in bridge
    assert 'mobileBadge' in bridge
    assert "oldButton.id='mw-v27-legacy-notification-button'" not in bridge


def test_trial_only_for_guests_and_session_is_not_wiped_by_navigation():
    demo=(ROOT/'js/demo-mode.js').read_text(encoding='utf-8')
    guard=(ROOT/'js/session-navigation-guard.js').read_text(encoding='utf-8')
    exit_trial=(ROOT/'js/trial-mode-banner.js').read_text(encoding='utf-8')
    assert "banner.style.display=active?'none':''" in demo
    assert "location.replace('account.html')" in guard
    assert 'mathweb_admin_token' in guard
    assert "localStorage.removeItem('mathweb_token')" not in demo
    assert "localStorage.removeItem('mathweb_token')" not in guard
    assert "localStorage.removeItem('mathweb_token')" not in exit_trial
    assert 'password' not in demo


def test_accounts_excluded_from_regular_student_admin_nav():
    assert 'admin.html' not in (ROOT/'js/neon-v5.js').read_text(encoding='utf-8').split('const entries=')[1].split('];')[0]
