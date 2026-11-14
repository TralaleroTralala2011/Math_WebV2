(function(){
  const pathname = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const pageKeyMap = {
    'index.html':'home',
    'practice.html':'practice',
    'practise.html':'practice',
    'trial-practise.html':'practice',
    'learn.html':'learn',
    'learning.html':'learn',
    'geometry-learning.html':'learn',
    'curriculum-studio.html':'learn',
    'study-suite.html':'learn',
    'learning-path.html':'roadmap',
    'learning-progress.html':'roadmap',
    'battle.html':'battle',
    'chat.html':'social',
    'account.html':'account',
    'geometry-studio.html':'learn',
    'geometry-lab.html':'learn'
  };
  const currentKey = pageKeyMap[pathname] || '';
  const links = [
    {key:'home', label:'Trang chủ', href:'index.html'},
    {key:'practice', label:'Luyện tập', href:'practise.html', cls:'protected-practice-link'},
    {key:'learn', label:'Học tập', href:'learn.html', cls:'protected-practice-link'},
    {key:'roadmap', label:'Lộ trình học', href:'learning-path.html', cls:'protected-practice-link'},
    {key:'battle', label:'Battle', href:'battle.html', cls:'protected-battle-link', id:'battleNavLink'},
    {key:'social', label:'Bạn bè & Chat', href:'chat.html', cls:'protected-practice-link'},
    {key:'account', label:'Tài khoản', href:'account.html', cls:'protected-account-link', id:'accountNavLink'}
  ];
  function getInitial(){
    const keys = ['mathweb_profile','mathweb_user','mathweb_trial_profile','mathweb_admin_profile'];
    for(const key of keys){
      try{
        const raw = localStorage.getItem(key);
        if(!raw) continue;
        const data = JSON.parse(raw);
        const name = (data && (data.username || data.name || data.display_name || data.player_id)) || '';
        if(name) return String(name).trim().charAt(0).toUpperCase();
      }catch(_){ }
    }
    return 'L';
  }
  function buildLink(link){
    const active = currentKey === link.key;
    return `<a href="${link.href}" class="nav-link ${link.cls||''} ${active?'active':''}" data-key="${link.key}" ${link.id?`id="${link.id}"`:''} ${active?'aria-current="page"':''}>${link.label}</a>`;
  }
  function buildNavbar(){
    return `
<header class="navbar mw-v55-unified" id="mathwebUnifiedNavbar">
  <a href="index.html" class="logo" aria-label="MATHWEB - Trang chủ">
    <div class="logo-icon">∑</div>
    <div class="logo-text">MATH<span>WEB</span></div>
  </a>
  <nav class="nav-menu" aria-label="Điều hướng chính">
    ${links.map(buildLink).join('')}
  </nav>
  <div class="nav-actions">
    <div class="notification-wrapper">
      <button id="notificationButton" class="notification-button" type="button" aria-label="Thông báo" aria-expanded="false" aria-controls="notificationPanel">🔔<span id="notificationBadge" class="notification-badge"></span></button>
      <div id="notificationPanel" class="notification-panel">
        <div class="notification-header">
          <div class="notification-title">Thông báo</div>
          <button id="readAllNotifications" class="notification-read-all" type="button">Đọc tất cả</button>
        </div>
        <div id="notificationList" class="notification-list"></div>
      </div>
    </div>
    <a href="account.html" class="account-badge" aria-label="Mở tài khoản">${getInitial()}</a>
  </div>
  <button class="mobile-menu-button" id="mobileMenuButton" type="button" aria-label="Mở menu" aria-expanded="false">☰</button>
</header>`;
  }
  function shouldReplaceHeader(header){
    if(!header) return false;
    const txt = (header.textContent || '').replace(/\s+/g,' ').trim();
    return /MATH|Trang chủ|Luyện tập|Battle|Tài khoản|Học tập|Đấu online|Bạn bè/i.test(txt);
  }
  function mount(){
    const replacement = document.createElement('div');
    replacement.innerHTML = buildNavbar();
    const navbar = replacement.firstElementChild;

    const existingNavbar = document.querySelector('header.navbar');
    const firstHeader = document.body ? document.body.querySelector(':scope > header') : null;
    if(existingNavbar){
      existingNavbar.replaceWith(navbar);
    } else if(shouldReplaceHeader(firstHeader)){
      firstHeader.replaceWith(navbar);
    } else if(document.body){
      const trialBanner = document.getElementById('mathwebTrialBanner');
      if(trialBanner && trialBanner.parentNode === document.body && trialBanner.nextSibling){
        document.body.insertBefore(navbar, trialBanner.nextSibling);
      } else {
        document.body.prepend(navbar);
      }
    }
    document.body.classList.add('mw-v55-nav-applied');

    const button = document.getElementById('mobileMenuButton');
    const nav = navbar.querySelector('.nav-menu');
    if(button && nav){
      button.addEventListener('click', ()=>{
        const open = navbar.classList.toggle('open');
        button.textContent = open ? '✕' : '☰';
        button.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      nav.querySelectorAll('a').forEach(a=>a.addEventListener('click', ()=>{
        navbar.classList.remove('open');
        button.textContent='☰';
        button.setAttribute('aria-expanded','false');
      }));
    }
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once:true});
  else mount();
})();
