/* MATH_WEB V47: safe same-origin page transitions, based on SortLab motion concepts.
   Does not intercept forms, auth, API, SPA routing, or downloads. */
(()=>{'use strict';if(window.__MW_V47_TRANSITIONS__)return;window.__MW_V47_TRANSITIONS__=true;
const reduce=matchMedia('(prefers-reduced-motion: reduce)');const effects=['fade','flip','zoom','cube','warp','glitch'];
const allowed=new Set(['fade','flip','zoom','cube','warp','glitch','random','off']);
let mode='fade';try{const m=localStorage.getItem('mathweb_transition_mode');if(allowed.has(m))mode=m;}catch(_){}
const style=document.createElement('link');style.rel='stylesheet';style.href='css/page-transitions-v47.css';document.head.appendChild(style);
function choose(){return mode==='random'?effects[Math.floor(Math.random()*effects.length)]:mode;}
function enter(){if(reduce.matches||mode==='off')return;document.documentElement.dataset.mwTransition=choose();document.documentElement.classList.add('mw-enter');setTimeout(()=>document.documentElement.classList.remove('mw-enter'),850);}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',enter,{once:true});else enter();
window.MATHWEB_TRANSITIONS={setMode(m){if(!allowed.has(m))return false;mode=m;try{localStorage.setItem('mathweb_transition_mode',m)}catch(_){}return true},getMode(){return mode},modes:[...allowed]};
let leaving=false;document.addEventListener('click',e=>{
 if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||leaving||reduce.matches||mode==='off')return;
 const a=e.target.closest&&e.target.closest('a[href]');if(!a||a.hasAttribute('download')||a.hasAttribute('data-no-transition')||a.getAttribute('target')&&a.getAttribute('target')!=='_self')return;
 if(a.closest('[contenteditable="true"]')||a.hasAttribute('onclick')||a.closest('[data-no-transition]'))return;
 // Leave JS-driven links, in-page actions and browser-managed special URLs untouched.
 if(a.getAttribute('href')?.trim().startsWith('#')||a.getAttribute('role')==='button')return;
 let u;try{u=new URL(a.href,location.href)}catch(_){return}
 if(u.origin!==location.origin||!/^https?:$/.test(u.protocol)||u.pathname===location.pathname&&u.search===location.search)return;
 if(a.hasAttribute('data-bs-toggle')||a.hasAttribute('aria-controls'))return;
 if(!/\.html?$/i.test(u.pathname)&&!u.pathname.endsWith('/'))return;
 // Respect earlier handlers; prevent browser navigation before the exit animation.
 e.preventDefault();leaving=true;
 { const kind=choose();document.documentElement.dataset.mwTransition=kind;document.documentElement.classList.add('mw-leave');
 const navigate=()=>location.assign(u.href);let done=false;const go=()=>{if(done)return;done=true;navigate()};setTimeout(go,240);}
},false);
window.addEventListener('pageshow',()=>{leaving=false;document.documentElement.classList.remove('mw-leave')});
})();