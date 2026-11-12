/* Admin-only controls for grade-specific, independently reviewed fixed placement papers. */
(()=>{'use strict';
const root=document.getElementById('appView');if(!root)return;
const base=(window.MATHWEB_API_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
const qf=root.querySelector('#mw-v5-admin-qf');if(!qf)return;
const section=document.createElement('section');section.className='mw-v5-card mw-v16-fixed-admin';
section.innerHTML='<h2>Đề đầu vào cố định · Lớp 10–12</h2><p>Chỉ Admin được công bố đề. Mỗi chủ đề cần 3 câu đã kiểm chứng ở từng mức và tối thiểu 2 hình thức trả lời. Đề chưa đạt chuẩn sẽ bị khóa.</p><div class="mw-v16-fixed-grid" id="mw-v16-fixed-grid"></div><p class="mw-v5-sub" id="mw-v16-fixed-msg" role="status"></p>';
qf.after(section);
const grid=section.querySelector('#mw-v16-fixed-grid'),message=section.querySelector('#mw-v16-fixed-msg');
function token(){try{return localStorage.getItem('mathweb_admin_token')||''}catch{return ''}}
async function api(path,options={}){const r=await fetch(base+'/api/roadmap-v2'+path,{...options,headers:{Authorization:'Bearer '+token(),...(options.headers||{})}});const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:data.detail?.message||'Lỗi máy chủ');return data}
function card(grade){const node=document.createElement('article');node.className='mw-v16-fixed-card';
const title=document.createElement('h3');title.textContent='Toán lớp '+grade;
const status=document.createElement('p');status.textContent='Đang kiểm tra ngân hàng...';
const publish=document.createElement('button');publish.type='button';publish.className='mw-v5-btn';publish.textContent='Công bố đề cố định';publish.disabled=true;
node.append(title,status,publish);grid.append(node);
async function update(){try{const d=await api('/fixed/admin-status/'+grade);status.textContent=`${d.selected}/${d.required} câu đã duyệt · ${d.topics_with_format_diversity}/${d.topics_required} chủ đề đủ đa dạng · ${d.published_valid?(d.has_new_candidate?'Đã công bố, có bản mới':'Đã công bố'):'Chưa công bố'}. Còn ${d.gaps.length} nhóm chủ đề/mức thiếu câu.`;publish.disabled=!d.ready||(d.published_valid&&!d.has_new_candidate);
 publish.title=publish.disabled?'Đề chưa đủ điều kiện hoặc đã công bố':'Đã đủ điều kiện kỹ thuật, cần Admin xác nhận';
 }catch(e){status.textContent='Không thể kiểm tra: '+e.message;publish.disabled=true}}
 publish.addEventListener('click',async()=>{if(!confirm('Công bố đề cố định lớp '+grade+' cho học sinh? Đề sẽ được khóa theo mã kiểm tra.'))return;publish.disabled=true;try{const d=await api('/fixed/publish/'+grade,{method:'POST'});message.textContent='Đã công bố lớp '+grade+' · Mã đề: '+d.paper_id;await update()}catch(e){message.textContent='Chưa thể công bố: '+e.message;await update()}});
 return update}
const updates=[10,11,12].map(card);
if(token())Promise.all(updates.map(f=>f()));
document.getElementById('refreshBtn')?.addEventListener('click',()=>Promise.all(updates.map(f=>f())));
const authObserver=new MutationObserver(()=>{if(!root.classList.contains('hidden')&&token())Promise.all(updates.map(f=>f()))});
authObserver.observe(root,{attributes:true,attributeFilter:['class']});
})();
