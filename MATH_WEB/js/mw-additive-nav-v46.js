/* Additive navigation only. Does not modify login or game logic. */
(()=>{function init(){if(document.getElementById('mw-geometry-nav-link'))return;
const links=[...document.querySelectorAll('a[href]')];const learn=links.find(a=>/learn(?:\.html|ing)/i.test(a.getAttribute('href')||'')&&/học tập|học bài/i.test(a.textContent||''));
const path=links.find(a=>/learning-path\.html/i.test(a.getAttribute('href')||'')&&/lộ trình/i.test(a.textContent||''));
if(!path)return;const nav=path.parentElement;if(!nav)return;
const a=document.createElement('a');a.id='mw-geometry-nav-link';a.href='geometry-studio.html';a.className=path.className;a.innerHTML='<span aria-hidden="true">📐</span> Hình học';a.setAttribute('aria-label','Hình học - Vẽ hình');
if(learn&&learn.parentElement===nav)learn.insertAdjacentElement('afterend',a);else nav.insertBefore(a,path);
}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();})();