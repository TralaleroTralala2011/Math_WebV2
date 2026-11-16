(() => {
 'use strict';
 const box=document.getElementById('profile-container');
 const params=new URLSearchParams(location.search);
 const playerId=params.get('player_id');
 const escapeHTML=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const safeNumber=v=>Number.isFinite(Number(v))?Math.max(0,Math.floor(Number(v))):0;
 async function show(){
  if(!playerId || playerId.length>100){box.textContent='Thiếu Player ID hợp lệ.';return;}
  const token=(localStorage.getItem('mathweb_token')||'').trim();
  if(!token){box.innerHTML='<p>Vui lòng đăng nhập để xem hồ sơ.</p><a href="login.html">Đăng nhập</a>';return;}
  try{
   const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),13000);
   let response;
   try{response=await fetch((window.MATHWEB_API_URL||'http://127.0.0.1:8000')+'/api/users/profile/'+encodeURIComponent(playerId),{headers:{Authorization:'Bearer '+token,Accept:'application/json'},signal:controller.signal});}
   finally{clearTimeout(timeout);}
   if(response.status===401){box.textContent='Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại.';return;}
   if(!response.ok){box.textContent=response.status===404?'Không tìm thấy người chơi.':'Không thể tải hồ sơ (HTTP '+response.status+').';return;}
   const data=await response.json();const p=data.user||data.profile||data;
   const username=String(p.username||'Người chơi'),xp=safeNumber(p.xp),required=safeNumber(p.required_xp);
   const percent=required?Math.min(100,Math.round(xp/required*100)):0;
   const stats=[['Cấp độ','Lv.'+safeNumber(p.level)],['Kinh nghiệm',xp+' XP'],['Lượt chơi',safeNumber(p.total_games)],['Câu đúng',safeNumber(p.total_correct)],['Câu sai',safeNumber(p.total_wrong)],['Tổng điểm',safeNumber(p.total_score)]];
   box.innerHTML='<div class="hero"><div class="avatar" aria-hidden="true">'+escapeHTML(username.slice(0,1).toUpperCase())+'</div><div><h1>'+escapeHTML(username)+'</h1><p>Player ID: '+escapeHTML(p.player_id||playerId)+'</p><p>'+(p.online?'🟢 Đang online':'⚪ Offline')+'</p></div></div><div class="stats">'+stats.map(([name,value])=>'<div class="stat"><span>'+escapeHTML(name)+'</span><strong>'+escapeHTML(value)+'</strong></div>').join('')+'</div><p>Tiến độ cấp độ: '+percent+'%</p><div class="levelbar"><div style="width:'+percent+'%"></div></div>';
  }catch(e){box.textContent=e.name==='AbortError'?'Hết thời gian kết nối máy chủ.':'Không thể kết nối backend. Vui lòng thử lại.';}
 }
 show();
})();
