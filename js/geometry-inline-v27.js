/* Auditable inline MathGeo preview. Only explicit coordinates / valid side lengths are shown to scale.
   Otherwise a clearly labeled conceptual sketch is rendered; no fabricated lengths or angles. */
(()=>{'use strict';
const NS='http://www.w3.org/2000/svg';
const make=(tag,attrs={})=>{const n=document.createElementNS(NS,tag);for(const [key,value] of Object.entries(attrs))n.setAttribute(key,String(value));return n};
function draw(svg,tag,attrs){const node=make(tag,attrs);svg.append(node);return node}
function point(svg,x,y,label){draw(svg,'circle',{cx:x,cy:y,r:4.5,fill:'#43e9ee'});const text=draw(svg,'text',{x:x+8,y:y-9,fill:'#e5f7ff','font-size':17,'font-weight':650});text.textContent=label}
function render(question){
 const full=String(question?.question||'');const title=String(question?.title||'');const source=full+' '+title;
 const frame=document.createElement('figure');frame.className='mw-v27-geometry';
 const svg=make('svg',{viewBox:'0 0 640 330',role:'img','aria-label':'Hình học hiển thị trực tiếp từ dữ kiện đề bài'});
 const def=make('defs'),grid=make('pattern',{id:'mw27grid',width:30,height:30,patternUnits:'userSpaceOnUse'});grid.append(make('path',{d:'M 30 0 L 0 0 0 30',fill:'none',stroke:'#214b66','stroke-width':0.7}));def.append(grid);svg.append(def);
 draw(svg,'rect',{width:640,height:330,rx:12,fill:'#071b31'});draw(svg,'rect',{width:640,height:330,rx:12,fill:'url(#mw27grid)'});
 let caption='';
 const coords3=[...full.matchAll(/\b([A-Z])\s*\(\s*(-?\d+(?:[.,]\d+)?)\s*[;,]\s*(-?\d+(?:[.,]\d+)?)\s*[;,]\s*(-?\d+(?:[.,]\d+)?)\s*\)/g)]
  .map(m=>({name:m[1],x:Number(m[2].replace(',','.')),y:Number(m[3].replace(',','.')),z:Number(m[4].replace(',','.'))})).filter(p=>[p.x,p.y,p.z].every(Number.isFinite));
 const unique3=[...new Map(coords3.map(p=>[p.name,p])).values()];
 const coords=[...full.matchAll(/\b([A-Z])\s*\(\s*(-?\d+(?:[.,]\d+)?)\s*[;,]\s*(-?\d+(?:[.,]\d+)?)\s*\)/g)]
  .map(x=>({name:x[1],x:Number(x[2].replace(',','.')),y:Number(x[3].replace(',','.'))})).filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y));
 const unique=[...new Map(coords.map(p=>[p.name,p])).values()];
 if(unique3.length>=2){
  // Axonometric projection: preserves coordinates, labels and incidence but NOT 3D distances on-screen.
  const mapped=unique3.map(p=>({...p,u:(p.x-p.y)*.7,v:-(p.x+p.y)*.32-p.z*.8}));
  mapped.push({name:'O',u:0,v:0,x:0,y:0,z:0});
  const minU=Math.min(...mapped.map(p=>p.u)),maxU=Math.max(...mapped.map(p=>p.u));
  const minV=Math.min(...mapped.map(p=>p.v)),maxV=Math.max(...mapped.map(p=>p.v));
  const scale=Math.min(500/Math.max(2,maxU-minU),235/Math.max(2,maxV-minV));
  const px=u=>320+(u-(minU+maxU)/2)*scale,py=v=>160+(v-(minV+maxV)/2)*scale;
  const origin=[px(0),py(0)];
  for(const [label,dx,dy] of [['x',70,-32],['y',-70,-32],['z',0,-80]]){
   draw(svg,'line',{x1:origin[0],y1:origin[1],x2:origin[0]+dx,y2:origin[1]+dy,stroke:'#668ca3','stroke-width':1.5});
   const t=draw(svg,'text',{x:origin[0]+dx+3,y:origin[1]+dy-4,fill:'#91bbd2','font-size':15});t.textContent=label;
  }
  for(const p of mapped.filter(p=>p.name!=='O'))point(svg,px(p.u),py(p.v),`${p.name}(${p.x};${p.y};${p.z})`);
  caption='Hình chiếu trục đo Oxyz từ tọa độ đã cho; không dùng khoảng cách trên hình chiếu để đo độ dài không gian.';
 }else if(unique.length>=2){
  const all=[...unique,{x:0,y:0}];let xmin=Math.min(...all.map(p=>p.x)),xmax=Math.max(...all.map(p=>p.x)),ymin=Math.min(...all.map(p=>p.y)),ymax=Math.max(...all.map(p=>p.y));
  const w=Math.max(2,xmax-xmin),h=Math.max(2,ymax-ymin);const scale=Math.min(520/w,245/h);const px=x=>320+(x-(xmin+xmax)/2)*scale,py=y=>165-(y-(ymin+ymax)/2)*scale;
  draw(svg,'line',{x1:20,y1:py(0),x2:620,y2:py(0),stroke:'#6592ab','stroke-width':1.4});draw(svg,'line',{x1:px(0),y1:15,x2:px(0),y2:315,stroke:'#6592ab','stroke-width':1.4});
  const labels=unique.map(p=>p.name);
  if(labels.includes('A')&&labels.includes('B')&&labels.includes('C')&&/tam giác|triangle/i.test(source)){
   const a=unique.find(p=>p.name==='A'),b=unique.find(p=>p.name==='B'),c=unique.find(p=>p.name==='C');draw(svg,'polygon',{points:[a,b,c].map(p=>`${px(p.x)},${py(p.y)}`).join(' '),fill:'#09bdda25',stroke:'#41dbe6','stroke-width':2.5});
  }
  for(const p of unique)point(svg,px(p.x),py(p.y),`${p.name}(${p.x};${p.y})`);
  caption='Hình theo đúng tọa độ điểm nêu trong đề; các trục dùng cùng một tỷ lệ.';
 }else if(/tam giác\s+([A-Z])([A-Z])([A-Z])/i.test(source)){
  const letters=/tam giác\s+([A-Z])([A-Z])([A-Z])/i.exec(source).slice(1);
  // AB, AC, BC can determine triangle uniquely up to rigid motion, if all three are explicit.
  const side=(a,b)=>{const re=new RegExp('(?:'+a+b+'|'+b+a+')\\s*=\\s*(\\d+(?:[.,]\\d+)?)','i');const m=source.match(re);return m?Number(m[1].replace(',','.')):null};
  const ab=side(letters[0],letters[1]),ac=side(letters[0],letters[2]),bc=side(letters[1],letters[2]);let pts=[[140,245],[490,245],[315,65]],accurate=false;
  if(ab>0&&ac>0&&bc>0 && ab+ac>bc && ab+bc>ac && ac+bc>ab){
   const xc=(ab*ab+ac*ac-bc*bc)/(2*ab),yc=Math.sqrt(Math.max(0,ac*ac-xc*xc));
   const scale=Math.min(365/ab,215/Math.max(1,yc));const baseX=320-ab*scale/2;
   pts=[[baseX,260],[baseX+ab*scale,260],[baseX+xc*scale,260-yc*scale]];accurate=true;
  }
  draw(svg,'polygon',{points:pts.map(p=>p.join(',')).join(' '),fill:'#16b9e71d',stroke:'#40dce8','stroke-width':3});
  pts.forEach((p,i)=>point(svg,p[0],p[1],letters[i]));
  caption=accurate?'Tam giác dựng theo ba cạnh đã cho, bảo toàn tỷ lệ.':'Hình phác họa tam giác theo tên đỉnh; KHÔNG dùng hình để suy ra độ dài, góc hay tính chất chưa được cho.';
 }else if(/đường tròn|hình tròn/i.test(source)){
  draw(svg,'circle',{cx:320,cy:160,r:105,fill:'#12a6df13',stroke:'#45dce7','stroke-width':3});
  draw(svg,'line',{x1:320,y1:160,x2:425,y2:160,stroke:'#f6c56b','stroke-width':2.6});point(svg,320,160,'O');
  const r=/\b(?:bán kính|R)\s*(?:bằng|=|là)?\s*(\d+(?:[.,]\d+)?)/i.exec(full);if(r){const label=draw(svg,'text',{x:350,y:151,fill:'#f6d98e','font-size':17});label.textContent='R = '+r[1]}
  caption='Hình tròn minh họa; chỉ thể hiện bán kính khi đề nêu rõ, không suy ra vị trí các điểm khác.';
 }else{return null}
 const label=document.createElement('figcaption');label.textContent=caption;
 frame.append(svg,label);return frame;
}
window.MATHWEB_INLINE_GEOMETRY={render};
})();
