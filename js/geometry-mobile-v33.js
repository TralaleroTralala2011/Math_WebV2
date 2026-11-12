/* v33: give phone users the same drawing actions as desktop, without proxying
   pointer coordinates or changing MathGeo's tool state. */
(()=>{'use strict';
 const canvas=document.getElementById('geo-canvas'),parent=document.querySelector('#geo-studio-workspace main');
 if(!canvas||!parent)return;
 canvas.style.touchAction='none';
 const badge=document.createElement('div');badge.id='geo-touch-badge';
 badge.textContent='Chạm để dựng hình · 2 ngón để phóng to';
 badge.setAttribute('aria-hidden','true');parent.appendChild(badge);
 const update=()=>{
  const mode=document.querySelector('.tool-btn.active-tool')?.dataset.tool||'select';
  badge.textContent=mode==='pan'?'Kéo một ngón để di chuyển hình':
   mode==='select'?'Kéo điểm để sửa · 2 ngón để thu phóng':
   mode==='point'?'Chạm vào vùng vẽ để tạo điểm':
   mode==='line'?'Chạm hai vị trí để tạo đoạn thẳng':
   mode==='circle'?'Chạm tâm rồi chạm điểm trên đường tròn':
   'Chạm vào các điểm để dựng hình · 2 ngón thu phóng';
 };
 document.querySelectorAll('.tool-btn').forEach(b=>b.addEventListener('click',update));
 update();
})();
