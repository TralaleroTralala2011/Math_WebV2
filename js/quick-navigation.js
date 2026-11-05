/* MATH_WEB floating navigation, progressive, account-only, page-aware. */
(()=>{
'use strict';
const ID='mathweb-quicknav';
const shortcuts=[['learning-path.html','🧭','Lộ trình học','mw-path'],['geometry-studio.html','📐','Vẽ hình','mw-geometry'],['learn.html','📘','Học bài','mw-learn']];
const hiddenPages=new Set(['learning-path.html','geometry-studio.html','learn.html','learning.html','geometry-learning.html','login.html','register.html','game.html','games.html','game-play.html','play.html']);
function page(){return (location.pathname.split('/').pop()||'index.html').toLowerCase()}
function account(){try{const token=(localStorage.getItem('mathweb_token')||'').trim();return Boolean(token&&token!=='null'&&token!=='undefined')}catch(e){return false}}
function isGame(){const p=page();return hiddenPages.has(p)||/^(game[-_]|play[-_]|mini[-_])/.test(p)||location.pathname.toLowerCase().split('/').includes('games')}
function gameOpen(){
  const overlay=document.querySelector('#practiceOverlay');
  if(overlay&&(overlay.classList.contains('show')||overlay.classList.contains('active')||overlay.getAttribute('aria-hidden')==='false'))return true;
  for(const el of document.querySelectorAll('#gameOverlay,.game-overlay,.game-modal')){
    if(el.hidden||el.classList.contains('hidden'))continue;
    const style=getComputedStyle(el);
    if(style.display!=='none'&&style.visibility!=='hidden'&&Number(style.opacity)!==0&&el.getClientRects().length)return true;
  }
  return false;
}
function sync(){
  const old=document.getElementById(ID);
  if(!account()||isGame()||gameOpen()) {if(old)old.remove();return}
  if(old||!document.body)return;
  const nav=document.createElement('nav');nav.id=ID;nav.className='mathweb-quicknav';nav.setAttribute('aria-label','Truy cập nhanh công cụ học tập');
  for(const [url,emoji,title,cls] of shortcuts){const a=document.createElement('a');a.href=url;a.className=cls;a.setAttribute('aria-label',title);a.innerHTML='<span class="mw-quick-icon" aria-hidden="true">'+emoji+'</span><span>'+title+'</span>';nav.appendChild(a)}
  document.body.appendChild(nav);
}
let queued=false;function schedule(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;sync()})}
function start(){
 sync();
 // Observe DOM changes only on the practice page; other pages use navigation/auth events.
 if(page()==='practise.html'){
  const overlay=document.querySelector('#practiceOverlay');
  if(overlay)new MutationObserver(schedule).observe(overlay,{attributes:true,attributeFilter:['class','style','hidden','aria-hidden']});
  for(const el of document.querySelectorAll('#gameOverlay,.game-overlay,.game-modal')){
   new MutationObserver(schedule).observe(el,{attributes:true,attributeFilter:['class','style','hidden','aria-hidden']});
  }
  // Game overlays can be created dynamically by existing practice code.
  new MutationObserver(schedule).observe(document.body,{childList:true,subtree:false});
 }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
window.addEventListener('pageshow',schedule);window.addEventListener('storage',schedule);window.addEventListener('focus',schedule);document.addEventListener('visibilitychange',()=>{if(!document.hidden)schedule()});document.addEventListener('mathweb:auth-changed',schedule);
// Account state can be changed by existing login code without a custom event.
// Poll lightly instead of monkey-patching browser storage or modifying authentication logic.
let last='';setInterval(()=>{const current=account()+'|'+page();if(current!==last){last=current;schedule()}},1200);
})();
