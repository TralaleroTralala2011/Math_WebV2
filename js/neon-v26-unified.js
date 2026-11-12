/* MATH_WEB V26: DOM/accessibility polish. Never grants authentication or admin rights. */
(()=>{'use strict';
const page=(location.pathname.split('/').pop()||'index.html').toLowerCase();
const admin=page==='admin.html';
function init(){
 if(!document.body)return;
 const skip=document.createElement('a');skip.className='mw26-skip';skip.textContent='Bỏ qua điều hướng';skip.href='#mw26-main';
 const target=admin?document.querySelector('#appView .content'):document.querySelector('main')||document.querySelector('.mw-v6-home')||document.querySelector('.mw-v5-canvas')||document.querySelector('.wrap');
 if(target){target.id=target.id||'mw26-main';skip.href='#'+target.id;document.body.prepend(skip)}
 if(admin){
   document.body.classList.add('mw-v26-admin');
   const sidebar=document.querySelector('#appView .layout>.side');const top=document.querySelector('#appView>.top');
   if(!sidebar||!top)return;
   sidebar.id='mw26-admin-sidebar';
   const b=document.createElement('button');b.type='button';b.className='mw26-admin-menu';b.textContent='☰ Menu quản trị';
   b.setAttribute('aria-controls',sidebar.id);b.setAttribute('aria-expanded','false');
   b.addEventListener('click',()=>{const open=document.body.classList.toggle('mw26-admin-open');b.setAttribute('aria-expanded',String(open));b.textContent=open?'✕ Đóng menu':'☰ Menu quản trị'});
   sidebar.addEventListener('click',e=>{if(!e.target.closest('.navbtn'))return;document.body.classList.remove('mw26-admin-open');b.setAttribute('aria-expanded','false');b.textContent='☰ Menu quản trị'});
   top.prepend(b);
 }else{
   // Hide legacy Admin-only navigation from students; the backend still enforces access.
   document.querySelectorAll('a[href]').forEach(a=>{try{if(new URL(a.getAttribute('href'),location.href).pathname.split('/').pop()==='admin.html'){a.hidden=true;a.setAttribute('aria-hidden','true');a.tabIndex=-1}}catch{}});
   const menu=document.querySelector('#mw-v5-header .mw-v5-menu');
   if(menu){document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.querySelector('#mw-v5-header.open')){menu.click();menu.focus()}})}
   document.querySelectorAll('a[target="_blank"]').forEach(a=>{a.rel='noopener noreferrer'});
 }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
