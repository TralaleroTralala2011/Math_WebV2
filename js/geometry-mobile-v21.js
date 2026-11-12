/* Compact mobile controls proxy to the existing MathGeo tool handlers. */
(()=>{'use strict';
const dock=document.getElementById('geo-mobile-dock');
const aside=document.getElementById('geo-studio-sidebar');
if(!dock||!aside)return;
const toggle=document.getElementById('geo-mobile-more');
function setOpen(open){
 aside.classList.toggle('geo-panel-open',open);
 toggle.setAttribute('aria-expanded',String(open));
 if(open){document.getElementById('geo-mobile-close')?.focus()}
 else if(aside.contains(document.activeElement)){toggle.focus()}
 window.dispatchEvent(new Event('resize'));
}
toggle.addEventListener('click',()=>setOpen(!aside.classList.contains('geo-panel-open')));
document.getElementById('geo-mobile-close').addEventListener('click',()=>setOpen(false));
dock.querySelectorAll('[data-geo-tool]').forEach(btn=>btn.addEventListener('click',()=>{
 const real=document.querySelector('.tool-btn[data-tool="'+btn.dataset.geoTool+'"]');
 if(!real)return;
 document.getElementById('tab-tools-btn')?.click();real.click();setOpen(false);
}));
document.getElementById('geo-mobile-undo').addEventListener('click',()=>document.getElementById('btn-undo')?.click());
const toolHints={select:'Chạm để chọn điểm; kéo để di chuyển.',point:'Chạm một vị trí để tạo điểm.',line:'Chạm hai vị trí để vẽ đoạn thẳng.',circle:'Chạm tâm rồi chạm một điểm trên đường tròn.',pan:'Kéo canvas để di chuyển hình.'};
const workspace=document.querySelector('#geo-studio-workspace main');
const hint=document.createElement('p');hint.id='geo-mobile-help';hint.setAttribute('role','status');
if(workspace)workspace.append(hint);
function sync(){
 const active=document.querySelector('.tool-btn.active-tool');
 const selected=active?.dataset.tool||'select';
 dock.querySelectorAll('[data-geo-tool]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.geoTool===selected)));
 hint.textContent=toolHints[selected]||'Chọn công cụ để dựng hình.';
}
document.querySelectorAll('.tool-btn').forEach(b=>b.addEventListener('click',sync));
document.addEventListener('keydown',e=>{if(e.key==='Escape')setOpen(false)});
sync();
})();
