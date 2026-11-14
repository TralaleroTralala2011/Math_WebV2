/* V53: sample-inspired bookshelf only, server-authoritative shared Battle topic voting. */
(function(){'use strict';
let root=null, activeId=null, selected=[], matchData=null, poll=null, submitting=false;
const API=()=>window.MATHWEB_API_BASE||window.MATHWEB_API_URL||'http://127.0.0.1:8000';
const auth=()=>({Authorization:'Bearer '+(localStorage.getItem('mathweb_token')||''),Accept:'application/json'});
const esc=v=>String(v||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const slug=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').toLowerCase().trim();
const TIERS=['Nền tảng','Trung cấp','Nâng cao'];
// The HTML reference supplies only visual/theme inspiration, not authentication or API logic.
const preferredTier=(name,index)=>{
 const t=slug(name);
 if(/nang cao|tong hop|van dung|toi uu|cuc tri khoang cach|dirichlet|quy nap|chung minh/.test(t))return 2;
 if(/co ban|nhan biet|menh de|tap hop|chia du|chia het|cap so cong|cap so nhan|do dai|thong ke/.test(t))return 0;
 return index%9===0?0:1;
};
function ensure(){
 if(root)return;
 root=document.createElement('div');root.id='mwBattleShelf';root.hidden=true;root.setAttribute('role','dialog');root.setAttribute('aria-modal','true');root.setAttribute('aria-label','Chọn chủ đề Battle');
 root.innerHTML=`<div class="bs-shell"><div class="bs-sky" aria-hidden="true"></div><div class="bs-head"><div><h2>📚 Tủ sách chủ đề Battle</h2><p class="bs-sub">Mỗi người chọn từ 1 đến 3 chủ đề. Có thể chốt ngay sau cuốn đầu tiên.</p></div><span class="bs-counter" id="bs-counter">0 / 3 chủ đề</span></div><div class="bs-main"><div class="bs-status" id="bs-status" role="status">Đang tải danh sách chủ đề…</div><div id="bs-shelves"></div></div><div class="bs-actions"><span class="bs-selected" id="bs-selection">Chưa chọn chủ đề</span><button class="bs-confirm" id="bs-confirm" type="button" disabled>Chốt chủ đề, bỏ qua chọn thêm</button><span class="bs-note">⏱️ Đồng hồ chỉ chạy sau khi hai người chốt.</span></div></div>`;
 document.body.appendChild(root);
 root.querySelector('#bs-confirm').addEventListener('click',submit);
}
function status(message){const el=root?.querySelector('#bs-status');if(el)el.textContent=message;}
function update(){if(!root)return;root.querySelector('#bs-counter').textContent=`${selected.length} / 3 chủ đề`;root.querySelector('#bs-confirm').disabled=submitting||!selected.length||!!matchData?.topic_selection?.my_ready;root.querySelector('#bs-selection').textContent=selected.length?`Đã chọn ${selected.length} cuốn, có thể chốt ngay.`:'Chọn tối thiểu 1 cuốn';root.querySelectorAll('.bs-book').forEach(b=>b.setAttribute('aria-pressed',String(selected.includes(b.dataset.topic))));}
function renderCatalog(topics){
 const wrap=root.querySelector('#bs-shelves');wrap.textContent='';
 TIERS.forEach((tier,level)=>{
   const list=topics.filter((t,i)=>preferredTier(t.name,i)===level);
   if(!list.length)return;
   const section=document.createElement('section');section.className='bs-tier';
   const title=document.createElement('div');title.className='bs-tier-title';title.textContent=['🔰','📗','🏅'][level]+' '+tier+' · '+list.length+' cuốn';section.appendChild(title);
   const grid=document.createElement('div');grid.className='bs-books';
   list.forEach((topic,index)=>{
     const button=document.createElement('button');button.type='button';button.className='bs-book';button.dataset.topic=topic.id;button.setAttribute('aria-pressed','false');button.style.setProperty('--book-color',['#2b756f','#2e527e','#764b81','#75602e','#275b74'][index%5]);button.title=topic.name;
     button.innerHTML=`<span class="bs-book-name">${esc(topic.name)}</span><small class="bs-book-foot">Toán ${topic.grade} · ${esc(tier)}</small>`;
     button.addEventListener('click',()=>{
       if(matchData?.topic_selection?.my_ready)return;
       const current=selected.indexOf(topic.id);
       if(current>=0)selected.splice(current,1);
       else if(selected.length<3)selected.push(topic.id);
       else{status('Tối đa 3 chủ đề. Hãy bỏ một cuốn trước khi chọn cuốn khác.');return;}
       update();status('Bạn có thể chọn thêm hoặc chốt ngay. Cả hai người được quyền chọn chủ đề riêng.');
     });
     grid.appendChild(button);
   });section.appendChild(grid);wrap.appendChild(section);
 });update();
}
async function readJson(response){const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.detail||data.message||`HTTP ${response.status}`);return data;}
async function fetchMatch(){return readJson(await fetch(`${API()}/api/matchmaking/match/${encodeURIComponent(activeId)}`,{headers:auth(),cache:'no-store'}));}
async function show(match,onPlaying){
 ensure();if(!match||!match.id)return;
 if(activeId!==String(match.id)){selected=[];activeId=String(match.id)}
 matchData=match;root.hidden=false;
 if(match.topic_selection?.my_choices?.length)selected=match.topic_selection.my_choices.slice(0,3);
 status(match.topic_selection?.my_ready?'Đã chốt. Đang chờ đối thủ xác nhận…':'Hãy chọn từ 1 đến 3 cuốn trong tủ sách.');
 update();
 try{
  const data=await readJson(await fetch(`${API()}/api/matchmaking/topic-catalog?grade=${encodeURIComponent(match.grade)}`,{headers:auth(),cache:'no-store'}));
  if(activeId!==String(match.id))return;
  renderCatalog(data.topics||[]);
 }catch(e){status('Không tải được tủ sách từ máy chủ: '+e.message);return;}
 clearInterval(poll);
 poll=setInterval(async()=>{
   if(root.hidden||!activeId){clearInterval(poll);poll=null;return;}
   try{const state=await fetchMatch();matchData=state;
     if(state.status==='PLAYING'){close();if(typeof onPlaying==='function')onPlaying(state.id);return;}
     if(['FINISHED','CANCELLED','REJECTED'].includes(state.status)){status('Trận đấu đã kết thúc hoặc bị hủy.');close();return;}
     if(state.topic_selection?.my_ready){selected=state.topic_selection.my_choices||selected;status(state.topic_selection.opponent_ready?'Hai người đã chốt, đang tạo đề…':'Đã chốt chủ đề. Chờ người còn lại xác nhận…');update()}
   }catch(e){status('Mất kết nối tạm thời. Đang thử kết nối lại…')}
 },2200);
}
async function submit(){
 if(submitting||selected.length<1||selected.length>3||!activeId)return;
 submitting=true;update();status('Đang xác nhận chủ đề với máy chủ…');
 try{
  const response=await readJson(await fetch(`${API()}/api/matchmaking/match/${encodeURIComponent(activeId)}/topics`,{method:'POST',headers:{...auth(),'Content-Type':'application/json'},body:JSON.stringify({topics:selected})}));
  if(response.status==='PLAYING'){status('Đã đủ hai người. Trận đấu bắt đầu!');close();document.dispatchEvent(new CustomEvent('mathweb:battle-topics-ready',{detail:{matchId:activeId}}));return;}
  matchData.topic_selection={...matchData.topic_selection,my_choices:selected.slice(),my_ready:true};
  status('Đã chốt '+selected.length+' chủ đề. Đang chờ đối thủ chốt…');
 }catch(error){status('Chưa thể chốt: '+error.message+'. Bạn có thể đổi chủ đề và thử lại.');}
 finally{submitting=false;update()}
}
function close(){if(root)root.hidden=true;if(poll){clearInterval(poll);poll=null}}
window.MathWebBattleTopicBookshelf={show,close};
})();
