/* V84: MathGeo Studio v25 is bundled at geometry-studio.html. */
(function(){'use strict';
 const btnClass='mathweb-open-mathgeo';
 let active=null;
 function attach(){
  document.querySelectorAll('.mathweb-ai-diagram-wrap').forEach(w=>{
   if(w.querySelector('.'+btnClass))return;
   if(w.dataset.mathgeoAccuracy==='insufficient-data')return;
   let parsed=null;try{parsed=JSON.parse(w.dataset.diagram||'null')}catch(e){}
   if(!parsed || typeof parsed!=='object')return;
   // Render MathGeo Studio as the primary practice renderer when the
   // supplied data is constructible. Never replace missing data with a
   // generic triangle, circle or solid.
   const isFinitePoint=p=>Array.isArray(p)&&p.length>=2&&p.slice(0,2).every(v=>Number.isFinite(Number(v)));
   const hasCoordinates=parsed.type==='geometry' && (
     (parsed.points && Object.values(parsed.points).some(isFinitePoint)) ||
     (Array.isArray(parsed.circles)&&parsed.circles.some(c=>isFinitePoint(c.center)&&Number(c.radius)>0))
   );
   const s=parsed.sides;
   const triangleSSS=parsed.type==='triangle'&&s&&['AB','BC','CA'].every(k=>Number.isFinite(Number(s[k]))&&Number(s[k])>0)
     && Number(s.AB)+Number(s.BC)>Number(s.CA)
     && Number(s.AB)+Number(s.CA)>Number(s.BC)
     && Number(s.BC)+Number(s.CA)>Number(s.AB);
   const graph=parsed.type==='graph'&&Array.isArray(parsed.curves)&&parsed.curves.some(c=>Array.isArray(c.points)&&c.points.some(isFinitePoint));
   if((hasCoordinates||triangleSSS||graph) && !w.querySelector('.mathweb-mathgeo-embed')){
     const frame=document.createElement('iframe');
     frame.className='mathweb-mathgeo-embed';
     frame.title='MathGeo Studio Pro: hình học theo dữ kiện bài tập';
     frame.loading='lazy';
     frame.style.cssText='width:100%;height:340px;border:1px solid #cbd5e1;border-radius:10px;background:#fff';
     frame.src=new URL('geometry-studio.html',document.baseURI).href;
     frame.addEventListener('load',()=>frame.contentWindow?.postMessage({type:'MATHWEB_PRACTICE_TO_MATHGEO',diagram:parsed},location.origin));
     w.querySelectorAll('svg,canvas,.mathweb-3d-note').forEach(el=>el.remove());
     w.prepend(frame);
   }
   const b=document.createElement('button');b.type='button';b.className=btnClass;
   b.textContent='Mở trong MathGeo Studio';
   b.style.cssText='margin:8px 0;padding:7px 12px;border-radius:8px;border:1px solid #2563eb;background:#eff6ff;color:#1d4ed8;cursor:pointer;font-weight:600';
   b.addEventListener('click',()=>{
    let diagram=null;try{diagram=JSON.parse(w.dataset.diagram||'null')}catch(e){}
    if(w.dataset.mathgeoAccuracy==='insufficient-data'){
      alert('Chưa có tọa độ hoặc quan hệ dựng hình đủ để MathGeo Studio vẽ đúng đề. Không thể tự suy đoán hình.');
      return;
    }
    if(!diagram || typeof diagram!=='object'){alert('Hình chưa có dữ liệu dựng hình phù hợp.');return;}
    active={diagram,win:window.open(new URL('geometry-studio.html',document.baseURI).href,'mathweb_mathgeo_studio')};
    if(!active.win){alert('Trình duyệt đang chặn cửa sổ MathGeo Studio. Hãy cho phép popup.');return;}
    active.win.focus();
    // Reused named windows may already have finished loading. Request an explicit handshake.
    active.win.postMessage({type:'MATHWEB_MATHGEO_PING'},location.origin);
   });w.appendChild(b);
  });
 }
 window.addEventListener('message',e=>{
  if(e.origin!==location.origin||e.data?.type!=='MATHWEB_MATHGEO_READY'||!active?.win||e.source!==active.win)return;
  active.win.postMessage({type:'MATHWEB_PRACTICE_TO_MATHGEO',diagram:active.diagram},location.origin);
 });
 document.addEventListener('DOMContentLoaded',()=>{
  attach();let pending=false;
  new MutationObserver(()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;attach()})}).observe(document.body,{childList:true,subtree:true});
 });
})();
