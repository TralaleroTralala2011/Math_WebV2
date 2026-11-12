/* V7: connect the screenshot-style dashboard to verified live user data. */
(()=>{'use strict';
const page=(location.pathname.split('/').pop()||'index.html').toLowerCase();
if(page!=='index.html')return;
let token='';try{token=localStorage.getItem('mathweb_token')||''}catch{}
if(!token){
 // Never display a previous student's cached XP/name on a shared device.
 const name=document.getElementById('mw-v6-name');if(name)name.textContent='bạn!';
 const level=document.getElementById('mw-v6-level');if(level)level.textContent='1';
 const xp=document.getElementById('mw-v6-xp');if(xp)xp.textContent='0 XP';
 const streak=document.getElementById('mw-v6-streak');if(streak)streak.textContent='Đăng nhập để xem';
 const ring=document.getElementById('mw-v6-ring');if(ring)ring.style.setProperty('--v6-progress','0%');
 const bar=document.getElementById('mw-v6-xp-bar');if(bar)bar.style.width='0%';
 const account=document.querySelector('#mw-v5-header .mw-v5-account');if(account){account.textContent='Đăng nhập';account.href='login.html';account.classList.remove('mw-v6-avatar')}
 return;
}
const base=(window.MATHWEB_API_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
async function api(path){const r=await fetch(base+path,{headers:{Authorization:'Bearer '+token}});if(!r.ok)throw Error('HTTP '+r.status);return r.json()}
const $=id=>document.getElementById(id);
const number=x=>Number(x||0).toLocaleString('vi-VN');
api('/api/users/me').then(d=>{
 const u=d.user||{};
 if($('mw-v6-name'))$('mw-v6-name').textContent=(u.username||'bạn')+'!';
 if($('mw-v6-level'))$('mw-v6-level').textContent=String(u.level||1);
 if($('mw-v6-xp'))$('mw-v6-xp').textContent=number(u.xp)+' XP';
 const needed=Math.max(1,Number(u.required_xp)||100+(Number(u.level)||1)*50);
 const percent=Math.max(0,Math.min(100,100*Number(u.xp||0)/needed));
 if($('mw-v6-ring'))$('mw-v6-ring').style.setProperty('--v6-progress',percent+'%');
 if($('mw-v6-xp-bar'))$('mw-v6-xp-bar').style.width=percent+'%';
}).catch(()=>{});
api('/api/games/streak').then(s=>{
 const target=$('mw-v6-streak');if(target)target.textContent=number(s.current)+' ngày liên tiếp';
}).catch(()=>{});
api('/api/games/activity-heatmap').then(d=>{
 const squares=$('mw-v6-heat')?.querySelectorAll('i');if(!squares||!Array.isArray(d.days))return;
 d.days.slice(-squares.length).forEach((day,i)=>{
  const n=Math.max(0,Number(day.sessions)||0);
  const square=squares[i];square.title=day.date+': '+n+' lượt luyện tập, '+number(day.questions)+' câu';
  square.dataset.activity=String(n===0?0:n===1?1:n<=3?2:n<=6?3:4);
 });
}).catch(()=>{});
for(const grade of [10,11,12]){
 api('/api/roadmap-v2/status/'+grade).then(d=>{
  const row=Array.from(document.querySelectorAll('.mw-v6-grade')).find(r=>r.querySelector('a')?.textContent.trim()==='Toán '+grade);
  if(!row)return;
  const bar=row.querySelector('.mw-v5-progress span'),label=row.querySelector('small');
  const total=Number(d.coverage?.topic_count)||0;
  if(!d.placement_complete){if(label)label.textContent='Chưa đánh giá';return}
  const completed=(d.mastery||[]).filter(x=>Number(x.best_score)>=25).length;
  const pct=total?Math.round(100*completed/total):0;
  if(bar)bar.style.width=pct+'%';if(label)label.textContent=pct+'%';
 }).catch(()=>{});
}
api('/api/users/me/learning-coach').then(data=>{
 const box=document.querySelector('.mw-v6-bottom .mw-v5-card:nth-child(2) p');
 if(box&&data.advice)box.textContent=data.advice;
}).catch(()=>{});
})();
