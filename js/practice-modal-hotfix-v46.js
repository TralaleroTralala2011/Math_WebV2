/* Non-invasive popup visibility guard: respects existing practise.js state. */
(function(){'use strict';
function init(){const overlay=document.getElementById('practiceOverlay'),popup=document.getElementById('knowledgePopup');if(!overlay||!popup)return;
let pending=false;
function sync(){pending=false;const active=popup.classList.contains('active')||popup.classList.contains('show');
if(active){popup.style.setProperty('z-index','20001','important');popup.style.setProperty('visibility','visible','important');popup.style.setProperty('opacity','1','important');}
else {popup.style.removeProperty('z-index');popup.style.removeProperty('visibility');popup.style.removeProperty('opacity');
if(overlay.classList.contains('active')||overlay.classList.contains('show')){overlay.classList.remove('active','show');document.body.classList.remove('popup-open');}}
}
const observer=new MutationObserver(()=>{if(!pending){pending=true;requestAnimationFrame(sync)}});
observer.observe(popup,{attributes:true,attributeFilter:['class']});observer.observe(overlay,{attributes:true,attributeFilter:['class']});sync();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();})();
