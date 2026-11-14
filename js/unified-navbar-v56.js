/* MATH_WEB V56: single navbar renderer for all navigation-bearing HTML pages,
   including nested game pages. No game engine or API endpoints are modified. */
(function(){
'use strict';
const source = document.currentScript && document.currentScript.src;
const projectRoot = source ? new URL('../', source) : new URL('./', location.href);
const makeLink = filename => new URL(filename, projectRoot).href;
const currentFilename = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
const path = location.pathname.toLowerCase();
const isGamePage = /\/(?:games|game)\//.test(path);
const activeGroups = {
  'index.html':'home','practice.html':'practice','practise.html':'practice',
  'trial-practise.html':'practice','learn.html':'learn','learning.html':'learn',
  'geometry-learning.html':'learn','geometry-studio.html':'learn',
  'geometry-lab.html':'learn','curriculum-studio.html':'learn',
  'study-suite.html':'learn','learning-path.html':'roadmap',
  'learning-progress.html':'roadmap','battle.html':'battle',
  'chat.html':'social','account.html':'account',
  'login.html':'account','register.html':'account'
};
const active = isGamePage ? 'practice' : (activeGroups[currentFilename] || '');
const entries = [
  ['home','⌂','Trang chủ','index.html',''],
  ['practice','◎','Luyện tập','practise.html','protected-practice-link'],
  ['learn','▤','Học tập','learn.html','protected-practice-link'],
  ['roadmap','↗','Lộ trình học','learning-path.html','protected-practice-link'],
  ['battle','♜','Battle','battle.html','protected-battle-link'],
  ['social','▣','Bạn bè & Chat','chat.html','protected-practice-link'],
  ['account','♙','Tài khoản','account.html','protected-account-link']
];
function htmlEscape(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
function accountInitial(){
  for(const key of ['mathweb_profile','mathweb_user','mathweb_trial_profile']){
    try {
      const val=JSON.parse(localStorage.getItem(key)||'null');
      const name=val && (val.username || val.display_name || val.name);
      if(name && String(name).trim())return String(name).trim().slice(0,1).toUpperCase();
    }catch(e){}
  }
  return 'L';
}
function navbarHtml(){
  return `<header class="navbar mw-v56-unified" id="mathwebUnifiedNavbar" aria-label="Thanh điều hướng MATHWEB">
    <a class="logo" href="${makeLink('index.html')}" aria-label="MATHWEB - Trang chủ">
      <span class="logo-icon" aria-hidden="true">∑</span><span class="logo-text">MATH<span>WEB</span></span>
    </a>
    <nav class="nav-menu" aria-label="Điều hướng chính" id="mwV56NavMenu">
      ${entries.map(([key,icon,label,href,cls])=>`<a class="nav-link ${cls} ${key===active?'active':''}" data-key="${key}" ${key===active?'aria-current="page"':''} ${key==='battle'?'id="battleNavLink"':key==='account'?'id="accountNavLink"':''} href="${makeLink(href)}"><span aria-hidden="true" class="mw-nav-icon">${icon}</span>${label}</a>`).join('')}
    </nav>
    <div class="nav-actions">
      <div class="notification-wrapper">
        <button type="button" id="notificationButton" class="notification-button" aria-label="Thông báo" aria-expanded="false" aria-controls="notificationPanel">🔔<span id="notificationBadge" class="notification-badge" aria-label="Số thông báo chưa đọc"></span></button>
        <div class="notification-panel" id="notificationPanel" role="region" aria-label="Thông báo">
          <div class="notification-header"><div class="notification-title">Thông báo</div><button type="button" class="notification-read-all" id="readAllNotifications">Đọc tất cả</button></div>
          <div id="notificationList" class="notification-list"></div>
        </div>
      </div>
      <a class="account-badge" href="${makeLink('account.html')}" aria-label="Tài khoản của bạn">${htmlEscape(accountInitial())}</a>
    </div>
    <button type="button" class="mobile-menu-button" id="mobileMenuButton" aria-label="Mở menu" aria-expanded="false" aria-controls="mwV56NavMenu">☰</button>
  </header>`;
}
function mount(){
  if(!document.body || document.getElementById('mathwebUnifiedNavbar'))return;
  const temp=document.createElement('template');temp.innerHTML=navbarHtml();
  const navbar=temp.content.firstElementChild;
  const legacy=document.querySelector('header.navbar');
  if(legacy){
    legacy.replaceWith(navbar);
  } else {
    const oldV5=document.getElementById('mw-v5-header');
    if(oldV5){oldV5.setAttribute('aria-hidden','true');oldV5.inert=true;}
    // Other headers with functional controls (Battle, geometry studio, Admin)
    // are kept as part of the original page. Game top bars are hidden by CSS
    // only after the new navigation exists.
    const trial=document.getElementById('mathwebTrialBanner');
    if(trial && trial.parentElement===document.body){trial.insertAdjacentElement('afterend',navbar)}
    else document.body.insertBefore(navbar,document.body.firstChild);
  }
  // Hide only legacy navigation-specific top bars, never task HUDs/headers.
  const simple=document.querySelector('body > header:not(.navbar):not(.battle-header):not(.mw-v56-unified)');
  if(simple && !simple.querySelector('h1') && simple.querySelectorAll('a').length>=2 && !simple.querySelector('button, input, select')){
    simple.classList.add('mw-v56-legacy-nav');simple.setAttribute('aria-hidden','true');
  }
  document.body.classList.add('mw-v56-nav-applied');
  if(isGamePage && document.querySelector('main.wrap > .top > .brand'))document.body.classList.add('mw-v56-game');
  // Hide the old NEON navigation but leave its dashboard modules intact.
  const oldV5=document.getElementById('mw-v5-header');
  if(oldV5){oldV5.setAttribute('aria-hidden','true');oldV5.inert=true;}
  const menuButton=navbar.querySelector('#mobileMenuButton');
  const nav=navbar.querySelector('.nav-menu');
  function setMenu(open){navbar.classList.toggle('open',!!open);menuButton.textContent=open?'✕':'☰';menuButton.setAttribute('aria-expanded',String(!!open))}
  menuButton.addEventListener('click',()=>setMenu(!navbar.classList.contains('open')));
  nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>setMenu(false)));
  document.addEventListener('keydown',e=>{if(e.key==='Escape')setMenu(false)});
  // If a game has no notification controller, its bell still opens an accessible
  // panel with a route to the account/notifications page. Do not override the
  // existing notification.js controller on full application pages.
  const bell=navbar.querySelector('#notificationButton');
  bell.addEventListener('click',()=>{
    if(window.MATHWEB_NOTIFICATIONS)return;
    const panel=navbar.querySelector('#notificationPanel');
    const opening=!panel.classList.contains('show');
    panel.classList.toggle('show',opening);bell.setAttribute('aria-expanded',String(opening));
    const list=navbar.querySelector('#notificationList');
    if(opening && !list.children.length){
      const a=document.createElement('a');a.href=makeLink('account.html');
      a.textContent='Xem thông báo trong Tài khoản';a.style.cssText='color:#8aeaff;display:block;padding:10px;text-decoration:none';list.append(a);
    }
  });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});
else mount();
})();
