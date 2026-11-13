/* MATH_WEB V47: bring existing topic popup to the browser top layer.
 * Does not override practise.js event handlers, question sources or game pages. */
(function(){ 'use strict';
  function init(){
    const popup=document.getElementById('knowledgePopup');
    const overlay=document.getElementById('practiceOverlay');
    const closeButton=document.getElementById('popupClose');
    if(!(popup instanceof HTMLDialogElement)||!overlay||!closeButton) return;
    const active=()=>popup.classList.contains('active')||popup.classList.contains('show');
    function sync(){
      if(active() && !popup.open){ try{ popup.showModal(); }catch(e){console.warn('MATHWEB practice modal:',e);} }
      if(!active() && popup.open) popup.close();
    }
    // Reuse the original close handler to restore focus, class flags and overlay.
    popup.addEventListener('cancel',e=>{e.preventDefault();closeButton.click();});
    popup.addEventListener('close',()=>{if(active())closeButton.click();});
    popup.addEventListener('click', e=>{
      if(e.target!==popup)return;
      const content=popup.querySelector('.popup-container');
      if(!content)return;
      const r=content.getBoundingClientRect();
      if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeButton.click();
    });
    const observer=new MutationObserver(sync);
    observer.observe(popup,{attributes:true,attributeFilter:['class']});
    sync();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
