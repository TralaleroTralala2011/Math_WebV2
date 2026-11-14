/* MATH_WEB V32 | Visual-only effects. No app routing, storage, fetch, API or app handlers. */
(function(){
  'use strict';
  if(window.__MATHWEB_SORTLAB_FX_V32__)return;
  window.__MATHWEB_SORTLAB_FX_V32__=true;
  var reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var coarse=window.matchMedia&&window.matchMedia('(pointer: coarse)').matches;
  function init(){
    if(!document.body)return;
    if(!reduced){
      document.body.classList.add('mwfx-page-enter');
      var bg=document.createElement('div');bg.id='mwfx-ambient';bg.setAttribute('aria-hidden','true');document.body.appendChild(bg);
      var line=document.createElement('div');line.className='mwfx-shine';line.setAttribute('aria-hidden','true');document.documentElement.appendChild(line);
      line.addEventListener('animationend',function(){line.remove();},{once:true});
    }
    // Restrict decoration to visual card surfaces and common clickable elements.
    var cardSelectors='.battle-choice,.glass-card,.feature-card,.topic-card,.stat-card,.dashboard-card,.learning-card,.plan-card,.quick-card,.mode-card';
    document.querySelectorAll(cardSelectors).forEach(function(el){el.classList.add('mwfx-card');});
    document.querySelectorAll('button,a[href]').forEach(function(el){if(!el.closest('[contenteditable="true"]'))el.classList.add('mwfx-control');});
    if(reduced)return;
    var cursor=null,frame=0,lastX=-999,lastY=-999;
    if(!coarse && window.matchMedia && window.matchMedia('(hover: hover)').matches){
      cursor=document.createElement('div');cursor.id='mwfx-cursor';cursor.setAttribute('aria-hidden','true');document.documentElement.appendChild(cursor);
      document.addEventListener('pointermove',function(e){
        if(e.pointerType==='touch')return;
        lastX=e.clientX;lastY=e.clientY;
        if(frame)return;
        frame=requestAnimationFrame(function(){cursor.style.transform='translate3d('+(lastX-110)+'px,'+(lastY-110)+'px,0)';cursor.style.opacity='.72';frame=0;});
      },{passive:true});
      document.addEventListener('pointerleave',function(){cursor.style.opacity='0';},{passive:true});
    }
    document.addEventListener('pointerdown',function(e){
      if(e.button!==0||e.pointerType==='touch'||!e.target.closest)return;
      var target=e.target.closest('a,button,.battle-choice,[role="button"]');
      if(!target||target.closest('[contenteditable="true"]'))return;
      var r=document.createElement('span');r.className='mwfx-ripple';r.setAttribute('aria-hidden','true');r.style.left=e.clientX+'px';r.style.top=e.clientY+'px';document.documentElement.appendChild(r);
      r.addEventListener('animationend',function(){r.remove();},{once:true});
    },{passive:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
