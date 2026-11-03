(function(){
  'use strict';
  const card=document.getElementById('learningCoach');
  if(!card)return;
  const api=window.MATHWEB_API_URL||'http://127.0.0.1:8000';
  const token=()=>localStorage.getItem('mathweb_token');
  const isTrial=()=>((location.pathname.split('/').pop()||'').toLowerCase()==='trial-practise.html' && new URLSearchParams(location.search).get('trial')==='1');
  const $=id=>document.getElementById(id);
  const label={auto:'Tự đề xuất',easy:'Nền tảng',medium:'Trung cấp',hard:'Nâng cao'};
  function preferenceKey(){if(isTrial())return 'mathweb_preferred_difficulty_guest';try{const u=JSON.parse(localStorage.getItem('mathweb_user')||'{}');return 'mathweb_preferred_difficulty_'+String(u.id||u.username||'guest')}catch{return 'mathweb_preferred_difficulty_guest'}}
  async function request(path,opts={}){
    const headers={'Accept':'application/json',...(opts.headers||{})};
    if(token())headers.Authorization='Bearer '+token();
    if(opts.body)headers['Content-Type']='application/json';
    const res=await fetch(api+path,{...opts,headers});
    let data={};try{data=await res.json()}catch{}
    if(!res.ok)throw new Error(data.detail||'Không thể tải gợi ý học tập.');
    return data;
  }
  async function load(){
    if(isTrial()){
      card.classList.remove('hidden');
      const saved=localStorage.getItem(preferenceKey())||'auto';
      $('coachDifficulty').value=['auto','easy','medium','hard'].includes(saved)?saved:'auto';
      $('coachAdvice').textContent='Bạn đang ở khu luyện tập thử. Hãy làm vài câu để tự khám phá nhịp học phù hợp; dữ liệu thử không ảnh hưởng hồ sơ thật.';
      $('coachBasis').textContent='Chế độ khách: lựa chọn độ khó được lưu trên trình duyệt này; không có hồ sơ cá nhân hoặc tính năng xã hội.';
      return;
    }
    if(!token()){card.classList.add('hidden');return}
    try{
      const d=await request('/api/users/me/learning-coach');
      $('coachAdvice').textContent=d.advice||'Chọn một chủ đề để bắt đầu luyện tập.';
      $('coachBasis').textContent=`Đã ghi nhận ${Number(d.sessions||0)} lượt học · ${Number(d.questions||0)} câu · ${d.accuracy==null?'chưa đủ dữ liệu':`độ chính xác ${d.accuracy}%`} · Đề xuất: ${label[d.suggested_difficulty]||d.suggested_difficulty}. ${d.basis||''}`;
      $('coachDifficulty').value=d.difficulty||'auto';
      localStorage.setItem(preferenceKey(),d.difficulty&&d.difficulty!=='auto'?d.difficulty:(d.suggested_difficulty||'medium'));
      if(d.weak_topic&&Number(d.weak_topic.questions||0)>0){$('coachAdvice').title=`Chủ đề nên ôn: ${d.weak_topic.topic} (${d.weak_topic.accuracy??'chưa có'}%)`}
    }catch(e){$('coachAdvice').textContent='Tớ sẽ đưa gợi ý cá nhân sau khi kết nối được lịch sử học tập.';$('coachBasis').textContent='Bạn vẫn có thể chọn độ khó thủ công ở đây.'}
  }
  $('saveCoachDifficulty').addEventListener('click',async function(){const btn=this;btn.disabled=true;try{const choice=$('coachDifficulty').value;if(isTrial()){localStorage.setItem(preferenceKey(),choice);$('coachAdvice').textContent='Đã lưu độ khó cho phiên dùng thử. Bạn có thể đổi bất cứ lúc nào.';$('coachBasis').textContent='Lựa chọn chỉ tồn tại trên trình duyệt này, không gắn với tài khoản thật.';}else{await request('/api/users/me/difficulty',{method:'PUT',body:JSON.stringify({difficulty:choice})});localStorage.setItem(preferenceKey(),choice==='auto'?'medium':choice);btn.textContent='Đã lưu ✓';await load();} }catch(e){$('coachBasis').textContent=e.message}finally{btn.disabled=false;setTimeout(()=>{btn.textContent='Lưu lựa chọn'},1400)}});
  load();
})();
