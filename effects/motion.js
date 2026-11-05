/* MATH_WEB additive motion system. Avoid mutating app state or intercepting navigation. */
(function(){'use strict';
 if(window.__mwMotionInstalled)return;window.__mwMotionInstalled=true;
 var reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 var ready=function(){
  if(!document.body)return;
  document.body.classList.add('mw-effects-ready');
  var bar=document.createElement('div');bar.id='mw-progress';bar.setAttribute('aria-hidden','true');document.body.appendChild(bar);
  var loader=document.createElement('div');loader.id='mw-loader';loader.setAttribute('aria-hidden','true');
  loader.innerHTML='<div class="mw-load-center"><div class="mw-orbit"><i></i></div><span>MATH_WEB đang khởi động</span><span class="mw-load-caption">Chuẩn bị không gian học tập...</span></div>';
  document.body.appendChild(loader);
  var closeLoader=function(){loader.classList.add('mw-done');bar.style.width='100%';setTimeout(function(){bar.style.opacity='0'},400)};
  // Decorative loader only: never blocks interaction, auth redirects, or page operation.
  if(document.readyState==='complete')setTimeout(closeLoader,reduced?0:240);
  else {window.addEventListener('load',function(){setTimeout(closeLoader,reduced?0:160)},{once:true});setTimeout(closeLoader,1150)}
  window.addEventListener('pageshow',closeLoader);
  var top=document.createElement('button');top.type='button';top.className='mw-scroll-top';top.textContent='↑';top.title='Lên đầu trang';top.setAttribute('aria-label','Lên đầu trang');top.addEventListener('click',function(){window.scrollTo({top:0,behavior:reduced?'instant':'smooth'})});document.body.appendChild(top);
  var scrollUpdate=function(){top.classList.toggle('mw-show',window.scrollY>520)};window.addEventListener('scroll',scrollUpdate,{passive:true});scrollUpdate();
  // Reveal only explicit safe content; no auth, modal, live question, game or Battle elements.
  if(!reduced&&'IntersectionObserver' in window){
   var observer=new IntersectionObserver(function(entries){entries.forEach(function(entry){if(entry.isIntersecting){entry.target.classList.add('mw-visible');observer.unobserve(entry.target)}})},{threshold:.06,rootMargin:'0px 0px 30px 0px'});
   document.querySelectorAll('main section, main article, .features-section, .hero-section').forEach(function(el,i){if(i>18||el.closest('[hidden],.hidden,[aria-hidden="true"],#practiceOverlay,.modal'))return;el.classList.add('mw-reveal');observer.observe(el)});
  }
  document.addEventListener('pointerdown',function(e){
   if(reduced||e.button!==0)return;var target=e.target.closest('button,.btn,[role="button"]');if(!target||target.disabled||target.closest('#mw-loader'))return;
   var style=getComputedStyle(target);if(style.position==='static')target.style.position='relative';
   if(style.overflow==='visible')return; // Avoid clipping or overriding component layout.
   var rect=target.getBoundingClientRect(),s=Math.max(rect.width,rect.height),r=document.createElement('span');r.className='mw-ripple';r.style.width=r.style.height=s+'px';r.style.left=(e.clientX-rect.left-s/2)+'px';r.style.top=(e.clientY-rect.top-s/2)+'px';target.appendChild(r);setTimeout(function(){r.remove()},600);
  },{passive:true});
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();
