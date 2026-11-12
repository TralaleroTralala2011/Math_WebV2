/* Admin-only additions: auditable batch generation and real coverage counters. */
(()=>{'use strict';const qf=document.getElementById('mw-v5-admin-qf');if(!qf)return;
const token=()=>{try{return localStorage.getItem('mathweb_admin_token')||''}catch{return ''}};
const base=(window.MATHWEB_API_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
async function api(path,options={}){const r=await fetch(base+'/api/admin/qf2'+path,{...options,headers:{Authorization:'Bearer '+token(),...(options.headers||{})}});const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:'HTTP '+r.status);return data}
const bar=qf.querySelector('.mw-v5-row');if(!bar)return;
const batch=document.createElement('button');batch.type='button';batch.className='mw-v5-btn';batch.textContent='✦ Sinh 9 dạng kiểm tra · 90 câu';batch.title='3 khối lớp, 3 chủ đề, 9 dạng toán ứng viên; không tự duyệt';bar.append(batch);
const placementExpansion=document.createElement('button');placementExpansion.type='button';placementExpansion.className='mw-v5-btn';placementExpansion.textContent='✦ Bổ sung đề đầu vào · 6 dạng / 60 câu';placementExpansion.title='Lớp 10: tập hợp; lớp 11: cấp số nhân; lớp 12: tiếp tuyến. Chỉ tạo ứng viên.';bar.append(placementExpansion);
placementExpansion.addEventListener('click',async()=>{
 placementExpansion.disabled=true;
 const msg=document.getElementById('mw-v7-admin-generation');
 if(msg)msg.textContent='Đang sinh ứng viên và kiểm tra công thức...';
 try{const data=await api('/generate/placement-expansion',{method:'POST'});
  if(msg)msg.textContent=`Đã tạo ${data.created_forms} dạng, ${data.created_questions} câu ứng viên; đã tồn tại ${data.already_present}. Chưa có câu nào được tự động phê duyệt.`;
  document.getElementById('v5-qf-refresh')?.click();
 }catch(err){if(msg)msg.textContent='Không tạo được ứng viên: '+err.message}
 finally{placementExpansion.disabled=false}
});
const v20Batch=document.createElement('button');v20Batch.type='button';v20Batch.className='mw-v5-btn';
v20Batch.textContent='✦ Đề đầu vào V20 · 31 dạng / 310 câu';
v20Batch.title='Chỉ dành cho Admin: tạo 31 dạng ứng viên, KHÔNG tự duyệt hoặc công bố đề';
bar.append(v20Batch);
v20Batch.addEventListener('click',async()=>{
 v20Batch.disabled=true;const msg=document.getElementById('mw-v7-admin-generation');
 if(msg)msg.textContent='Đang kiểm tra và tạo câu hỏi ứng viên trong hàng chờ...';
 try{const d=await api('/generate/placement-v20-review-batch',{method:'POST'});
  if(msg)msg.textContent=`V20: tạo mới ${d.created_forms}/${d.candidate_forms} dạng, ${d.created_questions} câu ứng viên. ${d.already_present} dạng đã có. Chỉ giáo viên kiểm duyệt mới có thể phê duyệt. ${d.errors?.length?'Có lỗi: '+d.errors.map(x=>x.topic_id).join(', '):''}`;
  document.getElementById('v5-qf-refresh')?.click();
 }catch(err){if(msg)msg.textContent='Không tạo được bộ ứng viên V20: '+err.message}
 finally{v20Batch.disabled=false}
});
const status=document.createElement('p');status.id='mw-v7-admin-generation';status.setAttribute('role','status');status.textContent='Bộ sinh có kiểm chứng công thức: 3 chủ đề thuộc lớp 10, 11, 12. Các dạng vẫn chờ Admin kiểm tra độc lập.';qf.append(status);
batch.addEventListener('click',async()=>{batch.disabled=true;status.textContent='Đang sinh và kiểm tra công thức...';try{
 const d=await api('/generate/verified-batch',{method:'POST'});
 status.textContent=`Tạo mới ${d.created_forms} dạng ứng viên, ${d.created_questions} câu; đã tồn tại ${d.already_present} dạng. ${d.errors?.length?'Lỗi: '+d.errors.map(x=>x.title).join(', '):'Chờ duyệt độc lập.'}`;
 document.getElementById('v5-qf-refresh')?.click();
}catch(e){status.textContent='Không thể sinh bộ đề: '+e.message}finally{batch.disabled=false}});
const coverage=document.createElement('section');coverage.className='mw-v7-admin-coverage';coverage.innerHTML='<h3>▥ Độ phủ ngân hàng đầu vào theo lớp</h3><p id="mw-v7-admin-coverage-note">Đang kiểm tra độ phủ thực tế...</p><div id="mw-v7-admin-coverage-grid"></div>';qf.after(coverage);
async function loadCoverage(){if(!token())return;try{const d=await api('/coverage');const grid=coverage.querySelector('#mw-v7-admin-coverage-grid');grid.replaceChildren();for(const g of d.grades){const card=document.createElement('article');const title=document.createElement('h4');title.textContent='Toán '+g.grade;card.append(title);for(const [label,value] of [['Chủ đề',g.topic_count],['Có câu hỏi',g.topics_with_questions],['Đủ 3 câu/mức',g.topics_meeting_3_per_tier],['Đủ 30 câu đã duyệt',g.topics_with_30_questions]]){const p=document.createElement('p');p.textContent=label+': '+value+'/'+g.topic_count;card.append(p)}grid.append(card)}coverage.querySelector('#mw-v7-admin-coverage-note').textContent=d.note}catch(e){coverage.querySelector('#mw-v7-admin-coverage-note').textContent='Không đọc được độ phủ: '+e.message}}
loadCoverage();document.getElementById('v5-qf-refresh')?.addEventListener('click',loadCoverage);
// A real prioritized review queue, calculated from the current database.
const queue=document.createElement('section');queue.className='mw-v7-admin-coverage';
const qhead=document.createElement('h3');qhead.textContent='Ưu tiên kiểm định đề đầu vào · 150 chủ đề';queue.append(qhead);
const qnote=document.createElement('p');qnote.textContent='Đang lấy số câu thiếu theo từng mức và số câu cần bổ sung cho đề 30 câu...';queue.append(qnote);
const qlist=document.createElement('div');qlist.id='mw-v15-audit-queue';queue.append(qlist);coverage.after(queue);
async function loadAuditQueue(){try{
 const d=await api('/coverage-detail');const sorted=[...(d.topics||[])].sort((a,b)=>{
  const gaps=x=>Object.values(x.missing_by_difficulty||{}).reduce((s,n)=>s+n,0);
  return gaps(b)-gaps(a)||b.missing_to_30-a.missing_to_30||a.grade-b.grade||a.title.localeCompare(b.title);
 });
 qnote.textContent=`Đã duyệt đủ 30 câu: ${d.certified_topic_exams}/${d.topic_count} chủ đề · Còn thiếu ${d.total_missing_certified_questions} lượt câu cho đề 30 câu và ${d.total_tier_gaps} lượt câu cho độ phủ 3 mức.`;
 qlist.replaceChildren();for(const t of sorted.slice(0,12)){
  const card=document.createElement('article');const name=document.createElement('strong');name.textContent=`Lớp ${t.grade} · ${t.title}`;card.append(name);
  const p=document.createElement('p');p.textContent=`Đã duyệt: ${t.approved_questions} · Thiếu đề 30 câu: ${t.missing_to_30} · Thiếu Nền tảng/Trung cấp/Nâng cao: ${Object.values(t.missing_by_difficulty).join('/')}`;card.append(p);qlist.append(card);
 }
 }catch(err){qnote.textContent='Không đọc được báo cáo kiểm định: '+err.message}}
loadAuditQueue();document.getElementById('v5-qf-refresh')?.addEventListener('click',loadAuditQueue);
const exportCoverage=document.createElement('button');exportCoverage.type='button';exportCoverage.className='mw-v5-btn';exportCoverage.textContent='↓ Xuất kiểm định 150 chủ đề (JSON)';exportCoverage.addEventListener('click',async()=>{exportCoverage.disabled=true;try{const data=await api('/coverage-detail');const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='MATH_WEB_COVERAGE_AUDIT_150_TOPICS.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),5000)}catch(err){coverage.querySelector('#mw-v7-admin-coverage-note').textContent=err.message}finally{exportCoverage.disabled=false}});coverage.append(exportCoverage);
const lesson=document.createElement('section');lesson.className='mw-v7-admin-coverage';lesson.innerHTML='<h3>✓ Kiểm định câu hỏi học liệu hiện có</h3><p>Chỉ quản trị viên có thể kiểm tra đáp án, lời giải và xác nhận độ khó. Câu bị từ chối sẽ không xuất hiện trong bài đầu vào.</p><div class="mw-v5-row"><label for="mw-v7-review-grade">Khối lớp</label><select id="mw-v7-review-grade"><option value="10">Lớp 10</option><option value="11">Lớp 11</option><option value="12">Lớp 12</option></select><button class="mw-v5-btn" id="mw-v7-review-reload" type="button">Nạp câu học liệu</button></div><p id="mw-v7-review-progress" role="status"></p><div id="mw-v7-review-list"></div><div class="mw-v5-row"><button type="button" id="mw-v7-review-prev" class="mw-v5-btn">← Trang trước</button><button type="button" id="mw-v7-review-next" class="mw-v5-btn">Trang sau →</button></div>';coverage.after(lesson);
let reviewOffset=0;
async function loadLessons(){if(!token())return;const grade=Number(lesson.querySelector('#mw-v7-review-grade').value);const progress=lesson.querySelector('#mw-v7-review-progress'),list=lesson.querySelector('#mw-v7-review-list');progress.textContent='Đang tải...';list.replaceChildren();try{
 const d=await api('/lesson-queue?grade='+grade+'&offset='+reviewOffset+'&limit=10');progress.textContent=`Đã kiểm tra ${d.reviewed}/${d.total} câu · Trang ${Math.floor(reviewOffset/10)+1}`;
 for(const q of d.questions){const card=document.createElement('details');card.className='mw-v5-review-entry';const heading=document.createElement('summary');heading.textContent=`${q.title} · Câu ${q.index+1} · ${q.status}`;card.append(heading);
 const body=document.createElement('div');body.className='mw-v5-review-panel';const text=document.createElement('p');text.textContent=q.question;body.append(text);const choices=document.createElement('p');choices.textContent=q.choices.length?q.choices.map((x,i)=>String.fromCharCode(65+i)+'. '+x).join('  |  '):'Tự luận / Đúng-Sai';body.append(choices);const answer=document.createElement('p');answer.textContent='Đáp án: '+(typeof q.answer==='number'&&q.choices.length?q.choices[q.answer]:q.answer);body.append(answer);const why=document.createElement('p');why.textContent='Lời giải: '+q.explanation;body.append(why);
 const tier=document.createElement('select');tier.setAttribute('aria-label','Mức độ đã kiểm chứng');for(const label of ['nền tảng','trung cấp','nâng cao']){const opt=document.createElement('option');opt.value=label;opt.textContent=label;tier.append(opt)}tier.value=q.difficulty||'nền tảng';body.append(tier);
 const notes=document.createElement('textarea');notes.rows=2;notes.placeholder='Ghi chú kiểm tra độc lập, ít nhất 20 ký tự';body.append(notes);
 const verified=document.createElement('input');verified.type='checkbox';const verifyLabel=document.createElement('label');verifyLabel.append(verified,document.createTextNode(' Tôi đã đối chiếu tính đúng đắn của câu và lời giải.'));body.append(verifyLabel);
 const row=document.createElement('div');row.className='mw-v5-row';const msg=document.createElement('p');msg.setAttribute('role','status');for(const [label,approved] of [['✓ Duyệt',true],['✕ Loại câu lỗi',false]]){const button=document.createElement('button');button.className='mw-v5-btn';button.type='button';button.textContent=label;button.addEventListener('click',async()=>{button.disabled=true;try{const data=await api('/lesson-questions/'+encodeURIComponent(q.topic_id)+'/'+q.index+'/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({approved,difficulty:tier.value,independently_checked:verified.checked,notes:notes.value})});msg.textContent='Đã cập nhật: '+data.status;await loadCoverage()}catch(e){msg.textContent=e.message}finally{button.disabled=false}});row.append(button)}body.append(row,msg);card.append(body);list.append(card)}
 lesson.querySelector('#mw-v7-review-prev').disabled=reviewOffset===0;lesson.querySelector('#mw-v7-review-next').disabled=reviewOffset+10>=d.total;
 }catch(e){progress.textContent='Không tải được câu học liệu: '+e.message}}
lesson.querySelector('#mw-v7-review-grade').addEventListener('change',()=>{reviewOffset=0;loadLessons()});lesson.querySelector('#mw-v7-review-reload').addEventListener('click',loadLessons);
lesson.querySelector('#mw-v7-review-prev').addEventListener('click',()=>{reviewOffset=Math.max(0,reviewOffset-10);loadLessons()});lesson.querySelector('#mw-v7-review-next').addEventListener('click',()=>{reviewOffset+=10;loadLessons()});
loadLessons();

})();
