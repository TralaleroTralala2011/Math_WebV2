/* GeoGebra adapter for practice graph diagrams. Fallback SVG stays visible if unavailable. */
(function(){
"use strict";
let seq=0;
const finite=n=>typeof n==="number"&&Number.isFinite(n);
const safe=n=>Number(n).toString();
function commands(diagram){
 const result=[], xmin=Number(diagram.x_range?.[0]),xmax=Number(diagram.x_range?.[1]),ymin=Number(diagram.y_range?.[0]),ymax=Number(diagram.y_range?.[1]);
 if(![xmin,xmax,ymin,ymax].every(finite)||xmin>=xmax||ymin>=ymax)return [];
 (diagram.curves||[]).slice(0,8).forEach((curve,i)=>{
  let run=[];let part=0;
  const flush=()=>{
   if(run.length>=2){
    const name="Curve"+i+"_"+part++;
    result.push(name+"=Polyline("+run.map(p=>"("+safe(p[0])+","+safe(p[1])+")").join(",")+")");
   }run=[];
  };
  (curve.points||[]).slice(0,400).forEach(point=>{
   if(!Array.isArray(point)||point.length<2||!finite(Number(point[0]))||!finite(Number(point[1]))||Number(point[0])<xmin||Number(point[0])>xmax||Number(point[1])<ymin||Number(point[1])>ymax){flush();return;}
   run.push([Number(point[0]),Number(point[1])]);
  });flush();
 });
 (diagram.marked_points||[]).slice(0,30).forEach((p,i)=>{
  const a=Number(p.x),b=Number(p.y);
  if(finite(a)&&finite(b))result.push("P"+i+"=("+safe(a)+","+safe(b)+")");
 });
 return result;
}

function geometryCommands(diagram){
 const out=[];const is3D=Boolean(diagram.coordinates_3d&&Object.keys(diagram.coordinates_3d).length);
 const coords=is3D?diagram.coordinates_3d:diagram.points;
 if(!coords||typeof coords!=="object")return {commands:[],is3D};
 const validName=n=>/^[A-Za-z][A-Za-z0-9_]{0,19}$/.test(n);
 const pointNames=new Set();
 Object.entries(coords).slice(0,70).forEach(([name,point])=>{
  if(!validName(name)||!Array.isArray(point)||point.length<(is3D?3:2))return;
  const values=point.slice(0,is3D?3:2).map(Number);
  if(!values.every(finite))return;
  pointNames.add(name);
  out.push(name+"=("+values.map(safe).join(",")+")");
 });
 const safeSeg=seg=>Array.isArray(seg)&&seg.length>=2&&pointNames.has(seg[0])&&pointNames.has(seg[1]);
 (diagram.segments||[]).slice(0,120).forEach((seg,i)=>{
  if(safeSeg(seg))out.push("s"+i+"=Segment("+seg[0]+","+seg[1]+")");
 });
 (diagram.hidden_segments||[]).slice(0,70).forEach((seg,i)=>{
  if(safeSeg(seg))out.push("h"+i+"=Segment("+seg[0]+","+seg[1]+")");
 });
 (diagram.dashed_segments||[]).slice(0,70).forEach((seg,i)=>{
  if(safeSeg(seg))out.push("d"+i+"=Segment("+seg[0]+","+seg[1]+")");
 });
 if(!is3D){
  (diagram.circles||[]).slice(0,30).forEach((c,i)=>{
   const center=Array.isArray(c.center)?c.center.map(Number):[];const radius=Number(c.radius);
   if(center.length>=2&&center.slice(0,2).every(finite)&&finite(radius)&&radius>0)
    out.push("c"+i+"=Circle(("+safe(center[0])+","+safe(center[1])+"),"+safe(radius)+")");
  });
  (diagram.polylines||[]).slice(0,30).forEach((poly,i)=>{
   if(!Array.isArray(poly))return;
   const pts=poly.slice(0,100).map(p=>Array.isArray(p)?p.slice(0,2).map(Number):[]);
   if(pts.length>=2&&pts.every(p=>p.length===2&&p.every(finite)))
    out.push("l"+i+"=Polyline("+pts.map(p=>"("+p.map(safe).join(",")+")").join(",")+")");
  });
 }
 return {commands:out,is3D};
}
function render(el){
 if(el.dataset.geogebraState)return;
 const diagram=JSON.parse(el.dataset.diagram);
 if(diagram.type!=="graph"&&diagram.type!=="geometry")return;
 el.dataset.geogebraState="loading";
 if(typeof window.GGBApplet!=="function"){el.dataset.geogebraState="fallback";return;}
 const id="mw-ggb-"+(++seq), target=document.createElement("div");target.id=id;
 target.style.cssText="width:100%;height:300px;min-height:300px";
 el.prepend(target);
 const width=Math.max(320,Math.round(el.getBoundingClientRect().width||360));
 try{
  const isGeometry=diagram.type==="geometry";
  const geo=isGeometry?geometryCommands(diagram):null;
  if(isGeometry&&(!geo||!geo.commands.length)){target.remove();el.dataset.geogebraState="fallback";return;}
  const app=new window.GGBApplet({
   appName:isGeometry?(geo.is3D?"3d":"geometry"):"graphing",width,height:300,showToolBar:false,showMenuBar:false,
   showAlgebraInput:false,showResetIcon:false,enableShiftDragZoom:true,
   enableRightClick:false,showFullscreenButton:true,
   appletOnLoad(api){
    try{
     if(isGeometry){
      geo.commands.forEach(cmd=>api.evalCommand(cmd));
     }else{
      const xr=diagram.x_range,yr=diagram.y_range;
      api.setCoordSystem(Number(xr[0]),Number(xr[1]),Number(yr[0]),Number(yr[1]));
      commands(diagram).forEach(cmd=>api.evalCommand(cmd));
     }
     const fallback=el.querySelector(".mw-ggb-fallback");
     if(fallback)fallback.hidden=true;
     if(isGeometry){const oldControls=el.querySelector(".mathweb-3d-controls");if(oldControls)oldControls.hidden=true;}
     el.dataset.geogebraState="ready";
    }catch(e){target.remove();el.dataset.geogebraState="fallback";}
   }
  },true);
  app.inject(id);
 }catch(e){target.remove();el.dataset.geogebraState="fallback";}
}
function scan(){document.querySelectorAll(".mw-geogebra[data-diagram]").forEach(render);}
document.addEventListener("DOMContentLoaded",()=>{
 scan();let pending=false;
 const observer=new MutationObserver(()=>{if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;scan();});});
 observer.observe(document.body,{childList:true,subtree:true});
});
})();
