/* Isolated shared game navigation. Shadow DOM avoids collision with game JS/CSS. */
(()=>{'use strict';
if(document.getElementById('mw-v7-gamebar'))return;
document.body.classList.add('mw-v7-game');
const src=document.currentScript?.src||'';
const root=new URL('../',src||location.href);
const host=document.createElement('div');host.id='mw-v7-gamebar';
const shadow=host.attachShadow({mode:'open'});
const css=`:host{display:block;position:relative;z-index:500;font-family:Inter,'Segoe UI',Arial,sans-serif;color:#e8f8ff}*{box-sizing:border-box}nav{width:min(1160px,calc(100% - 28px));margin:12px auto 0;padding:10px 15px;display:flex;align-items:center;gap:10px;border:1px solid #1489c5;border-radius:19px;background:linear-gradient(130deg,#04172f,#071e3d);box-shadow:0 0 24px #07b8f028}a{text-decoration:none;color:#b9d8e9;font-size:12px;font-weight:650;white-space:nowrap;padding:10px 11px;border-radius:10px}a:hover,a:focus-visible{background:#0d3858;color:#00e6f0}a:focus-visible,button:focus-visible{outline:3px solid #0fe9f0;outline-offset:2px}.logo{font-size:18px;color:#fff;font-weight:850;letter-spacing:-.4px;margin-right:auto}.logo b{color:#08ecf2;font-size:26px}.active{background:#073858;color:#00e9f1}button{display:none;border:1px solid #2679a2;background:#082c4d;color:#fff;border-radius:11px;padding:9px 13px;cursor:pointer}#links{display:flex;align-items:center;gap:3px}@media(max-width:700px){nav{width:calc(100% - 20px);padding:8px 11px;flex-wrap:wrap}button{display:block}#links{display:none;width:100%;flex-direction:column;align-items:stretch}#links.open{display:flex}#links a{padding:12px 10px}.logo{font-size:16px}.logo b{font-size:22px}}`;
const style=document.createElement('style');style.textContent=css;
const nav=document.createElement('nav');nav.setAttribute('aria-label','Điều hướng chung MATH_WEB');
const logo=document.createElement('a');logo.className='logo';logo.href=new URL('index.html',root).href;logo.innerHTML='<b>∑</b> MATH<span style="color:#08ecf2">WEB</span>';nav.append(logo);
const toggle=document.createElement('button');toggle.type='button';toggle.textContent='☰ Menu';toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls','links');nav.append(toggle);
const links=document.createElement('div');links.id='links';
for(const [label,target] of [['Trang chủ','index.html'],['Luyện tập','practice.html'],['Học tập','learn.html'],['Lộ trình học','learning-path.html'],['Battle','battle.html'],['Bạn bè & Chat','chat.html']]){
 const a=document.createElement('a');a.textContent=label;a.href=new URL(target,root).href;if(target==='practice.html')a.className='active';links.append(a);
}
nav.append(links);shadow.append(style,nav);
toggle.addEventListener('click',()=>{const open=links.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));toggle.textContent=open?'✕ Đóng':'☰ Menu'});
document.body.prepend(host);
})();
