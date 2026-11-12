"use strict";
(() => {
 const control=document.getElementById('matrix-assessment-toggle');
 const panel=document.getElementById('mw-v5-old-path');
 if(!control||!panel)return;
 control.addEventListener('click',()=>{
  const show=panel.hasAttribute('hidden');
  if(show)panel.removeAttribute('hidden');else panel.setAttribute('hidden','');
  control.setAttribute('aria-expanded',String(show));
  control.textContent=show?'Đóng khảo sát ma trận 900 câu ▴':'Khảo sát ma trận 900 câu (bản thử nghiệm) ▾';
 });
})();
