/* Server-graded placement + gated 3-topic roadmap. Does not expose answers before submission. */
(()=>{'use strict';
const app=document.getElementById('mw-v5-roadmap');if(!app)return;
const API=(window.MATHWEB_API_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
const grades=[10,11,12];let grade=Number(new URLSearchParams(location.search).get('grade'))||10;
if(!grades.includes(grade))grade=10;
let status=null,coverage=null,attempt=null,answers={},cursor=0,working=false;
let saveTimer=null,saveRevision=0,saveInFlight=false;
const geoStudentPreviews=new Map();let geoQuestionWindow=null;
window.addEventListener('message',event=>{
 if(event.origin!==location.origin||event.source!==geoQuestionWindow||!attempt)return;
 const data=event.data;
 if(data?.type!=='MATHWEB_GEOMETRY_STUDENT_PNG')return;
 if(typeof data.qid!=='string'||!attempt.questions.some(q=>q.qid===data.qid))return;
 if(typeof data.image!=='string'||!data.image.startsWith('data:image/png;base64,')||data.image.length>1300000)return;
 geoStudentPreviews.set(data.qid,data.image);
 if(attempt.questions[cursor]?.qid===data.qid)exam();
});
const legacy=document.querySelector('main');if(legacy)legacy.hidden=true;
const token=()=>{try{return localStorage.getItem('mathweb_token')||''}catch{return ''}};
async function call(url,options={}){const r=await fetch(API+'/api/roadmap-v2'+url,{...options,headers:{'Content-Type':'application/json','Authorization':'Bearer '+token(),...(options.headers||{})}});let data;try{data=await r.json()}catch{data={detail:'Không đọc được phản hồi API'}}if(!r.ok)throw Object.assign(new Error(typeof data.detail==='string'?data.detail:data.detail?.message||'Không thể thực hiện yêu cầu'),{data,status:r.status});return data}

// Serialize autosave requests: otherwise a slow older request can overwrite
// a newer answer when a student advances rapidly through a long fixed paper.
function scheduleSave(){
 if(!attempt)return;
 saveRevision++;
 clearTimeout(saveTimer);
 const indicator=document.getElementById('mw-v7-save-state');
 if(indicator)indicator.textContent='Đang chờ lưu bản nháp…';
 saveTimer=setTimeout(flushDraft,420);
}
async function flushDraft(){
 if(!attempt||saveInFlight)return;
 const snapshotId=attempt.attempt_id;
 const revision=saveRevision;
 const snapshot=JSON.stringify({answers:{...answers}});
 saveInFlight=true;
 try{
  await call('/draft/'+encodeURIComponent(snapshotId),{method:'POST',body:snapshot});
  if(attempt?.attempt_id===snapshotId && revision===saveRevision){
   const indicator=document.getElementById('mw-v7-save-state');
   if(indicator)indicator.textContent='✓ Bản nháp đã lưu trên máy chủ';
  }
 }catch(e){
  if(attempt?.attempt_id===snapshotId && revision===saveRevision){
   const indicator=document.getElementById('mw-v7-save-state');
   if(indicator)indicator.textContent='⚠ Chưa lưu được bản nháp: '+e.message;
  }
 }finally{
  saveInFlight=false;
  // Coalesce all edits made while saving into the next complete snapshot.
  if(attempt && (attempt.attempt_id!==snapshotId || saveRevision>revision)){
   clearTimeout(saveTimer);saveTimer=setTimeout(flushDraft,0);
  }
 }
}
function html(node,markup){node.innerHTML=markup;return node}
function el(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function btn(label,callback,extra=''){const b=el('button','mw-v5-btn '+extra,label);b.type='button';b.addEventListener('click',callback);return b}
function section(){app.replaceChildren();app.className='mw-v5-canvas mw-v6-roadmap';const head=el('div','mw-v6-roadmap-intro');const left=el('div');const title=el('h1','mw-v5-title','Lộ trình học cá nhân hóa 🚀');const intro=el('p','mw-v5-sub','Bắt đầu bằng bài kiểm tra đầu vào, phân tích đúng / sai / bỏ qua và chinh phục từng chặng 3 chủ đề.');left.append(title,intro);head.append(left,el('span','mw-v6-roadmap-flag','✦ Học đúng trọng tâm · Tiến bộ mỗi ngày'));app.append(head)}
function alertText(msg){const p=el('p','mw-v5-sub',msg);p.setAttribute('role','alert');app.append(p)}
function loading(){section();alertText('Đang đọc kết quả và độ phủ ngân hàng đề...')}
function item(title,body,cls='mw-v5-card'){const e=el('article',cls);e.append(el('h2','',title));if(body)e.append(el('p','',body));return e}
async function refresh(){loading();if(!token()){section();const c=item('🔒 Yêu cầu đăng nhập','Đăng nhập tài khoản học sinh trước khi sử dụng lộ trình. Tài khoản Admin không được tham gia lộ trình người học.');const a=el('a','mw-v5-btn mw-v5-gradient','Đăng nhập →');a.href='login.html';c.append(a);app.append(c);return}
 try{status=await call('/status/'+grade);coverage=status.coverage;show()}catch(err){
 section();
 const card=item('Lộ trình đang tạm gián đoạn','Không thể tải dữ liệu lộ trình từ máy chủ. Thử kết nối lại sẽ không xóa kết quả học tập đã lưu.');
 card.classList.add('mw-v40-connection-card');
 const detail=el('p','mw-v40-connection-detail',err.status===404?'API lộ trình chưa được triển khai trên backend (404). Cần cập nhật Render cùng phiên bản website.':err.status===401?'Phiên đăng nhập không còn hợp lệ. Hãy đăng nhập lại.':'Kết nối chưa thành công: '+err.message);
 card.append(detail);
 const actions=el('div','mw-v40-actions');
 actions.append(btn('↻ Thử kết nối lại',()=>refresh(),'mw-v5-gradient'));
 const learn=el('a','mw-v5-btn','📚 Mở thư viện học tập');learn.href='learn.html?grade='+grade;actions.append(learn);
 card.append(actions);app.append(card);
}
}
function gradeSelect(){const wrap=item('① Chọn lớp để bắt đầu','Chọn đúng khối lớp để hệ thống sử dụng ngân hàng câu hỏi tương ứng.');const row=el('div','mw-v6-grade-buttons');grades.forEach(g=>{const b=btn('Lớp '+g,()=>{grade=g;try{localStorage.setItem('mw-v6-grade',String(g))}catch{}attempt=null;answers={};cursor=0;refresh()},grade===g?'mw-v5-gradient':'');b.setAttribute('aria-pressed',String(grade===g));row.append(b)});wrap.append(row);return wrap}
function overviewCard(){const c=item('② Đề đầu vào CỐ ĐỊNH · Toán '+grade,'Mỗi lớp có đề riêng, gồm 3 câu đã duyệt ở từng mức Nền tảng / Trung cấp / Nâng cao cho MỖI chủ đề. Đề chỉ được mở sau khi giáo viên kiểm chứng và công bố.');const row=el('div','mw-v6-tier-chips');for(const d of ['Nền tảng','Trung cấp','Nâng cao'])row.append(el('span','mw-v5-pill','✦ '+d));c.append(row);if(coverage){const p=el('p','');p.style.fontSize='12px';p.textContent=`Độ phủ hiện có: ${coverage.topics_with_questions}/${coverage.topic_count} chủ đề có câu hỏi; ${coverage.topics_meeting_3_per_tier}/${coverage.topic_count} đạt tối thiểu 3 câu/mức. Không tự nhận câu thiếu nhãn là đã kiểm định.`;c.append(p)}
 const fixed=status?.fixed_exam;if(fixed){const line=el('p','mw-v5-sub',`Đề cố định: ${fixed.selected}/${fixed.required} câu đủ điều kiện chọn · ${fixed.topics_with_format_diversity}/${fixed.topics_required} chủ đề có ≥2 kiểu trả lời · ${fixed.published_valid?'✓ Đã công bố':'🔒 Chưa công bố'}.`);c.append(line);}
 return c}
function aiCard(){const c=item('③ AI Phân tích & cá nhân hóa','✓ Lưu từng câu đúng / sai / bỏ qua\n✓ Ước lượng năng lực theo mức độ\n✓ Nhận diện điểm mạnh, điểm cần cải thiện\n✓ Tự động ưu tiên chủ đề ôn luyện');c.querySelector('p').style.whiteSpace='pre-line';c.append(el('div','mw-v5-pill','🤖 Gia sư thích ứng từ dữ liệu thực'));return c}
function show(){section();const row=el('div','mw-v5-grid');row.append(gradeSelect(),overviewCard(),aiCard());app.append(row);if(!status?.official_placement_complete){
 const gate=el('section','mw-v6-lock');gate.append(el('div','mw-v6-lock-icon','🔒'));
 const copy=el('div','mw-v6-lock-copy');const ready=!!status?.fixed_exam?.published_valid;
 copy.append(el('h2','',ready?'Đề đầu vào cố định đã sẵn sàng':'Đề đầu vào cố định đang chờ kiểm chứng và xuất bản'),
 el('p','',ready?'Chọn đúng lớp, làm đầy đủ bài kiểm tra. Mỗi chủ đề có 9 câu đã duyệt ở 3 mức; bài được lưu tự động để làm tiếp.':'Chưa đủ câu hỏi đã duyệt để đánh giá khách quan. Không sử dụng câu ứng viên để chấm năng lực hoặc tự mở khóa lộ trình.'));
 if(!status?.placement_complete)copy.append(el('p','', 'Bạn chưa từng làm bài đầu vào. Có thể thử bài luyện tập trong khi chờ đề chính thức.'));
 if(status?.placement_complete)copy.append(el('p','', 'Kết quả bài thử cũ vẫn được lưu nhưng không thay thế đề đầu vào cố định.'));
 gate.append(copy);
 if(ready)gate.append(btn('Bắt đầu đề cố định lớp '+grade+' →',()=>begin('fixed_placement'),'mw-v5-gradient'));
 else{const b=btn('Chưa thể mở đề chính thức',()=>{},'');b.disabled=true;gate.append(b);
 const link=el('a','mw-v5-btn','Ôn luyện trong thư viện →');link.href='learn.html?grade='+grade;gate.append(link);
 gate.append(btn('Làm bài thử (không đánh giá năng lực)',()=>begin('placement')))}
 app.append(gate);return}
 const result=status.diagnostic||{};const panel=item('✓ Kết quả đánh giá năng lực · Toán '+grade);panel.style.marginTop='18px';if(result.diagnostic_completeness&&!result.diagnostic_completeness.three_tiers_complete){panel.append(el('p','mw-v5-sub',result.diagnostic_completeness.disclaimer))}const summary=el('div','mw-v5-row');const score=el('div','mw-v5-kpi',`${result.correct||0}/${result.total||0} câu đúng`);summary.append(score);const counts=el('p','',`✓ Đúng: ${result.correct||0}  ·  ✕ Sai: ${result.wrong||0}  ·  ○ Bỏ qua: ${result.skipped||0}`);summary.append(counts);panel.append(summary);const brow=el('div','mw-v5-row');const isSharedFixed=result.mode==='fixed_placement';brow.append(btn(isSharedFixed?'Xem phân tích theo chủ đề':'Xem lại từng câu',()=>review(result)),btn('Xuất hồ sơ đánh giá',()=>review(result)));panel.append(brow);app.append(panel);
 if(!status.placement_validated){
   const warn=item('🔒 Lộ trình chính thức chưa thể mở','Bài vừa làm là đánh giá thử: ngân hàng chưa đủ 3 câu đã duyệt ở từng mức cho tất cả chủ đề lớp '+grade+'. Không dùng kết quả thiếu kiểm chứng để khẳng định năng lực hoặc mở khóa bài thi 30 câu.');
   warn.classList.add('mw-v15-provisional');
   const verified=result.verified_score||{};
   warn.append(el('p','mw-v15-evidence',`Bằng chứng đã kiểm chứng: ${verified.total||0}/${result.total||0} câu · Đúng ${verified.correct||0} · Sai ${verified.wrong||0} · Bỏ qua ${verified.skipped||0}.`));
   const gaps=result.assessment_quality?.topics_missing_verified_tiers;
   if(typeof gaps==='number')warn.append(el('p','',`Còn ${gaps}/${coverage.topic_count} chủ đề chưa đạt yêu cầu ba mức độ.`));
   const link=el('a','mw-v5-btn mw-v5-gradient','Mở thư viện học tập để ôn luyện →');link.href='learn.html?grade='+grade;warn.append(link);
   app.append(warn);showTutor();return;
 }
 drawRoadmap();showTutor()}
function drawRoadmap(){const c=item('▤ Lộ trình học · 3 chủ đề mỗi chặng','Mỗi chủ đề có lý thuyết, video, bài tập, góc thắc mắc và bài kiểm tra tổng hợp 30 câu. Đạt từ 25/30 để hoàn thành. Hoàn thành cả 3 chủ đề mới mở khóa chặng tiếp theo.');c.classList.add('mw-v6-roadmap-section');const map=new Map((status.mastery||[]).map(x=>[x.topic_id,x]));const list=coverage.topics;const ordering=status.diagnostic?.roadmap_order||[];const ordered=ordering.map(id=>list.find(t=>t.id===id)).filter(Boolean);ordered.push(...list.filter(t=>!ordering.includes(t.id)));
 let activeGroup=0;for(let g=0;g<Math.ceil(ordered.length/3);g++){const prior=ordered.slice((g-1)*3,g*3);if(g>0&&!prior.every(t=>(map.get(t.id)?.best_score||0)>=25))break;activeGroup=g}
 const header=el('div','mw-v5-row');header.append(el('span','mw-v5-pill',`Quy tắc: ≥25/30 · Hoàn thành 3 chủ đề để mở chặng kế tiếp`),el('span','mw-v5-pill',`Đã hoàn thành ${ordered.filter(t=>(map.get(t.id)?.best_score||0)>=25).length}/${ordered.length} chủ đề`));c.append(header);
 const grid=el('div','mw-v6-roadmap-grid');grid.style.marginTop='16px';const maxVisible=Math.min(ordered.length,(activeGroup+1)*3);for(let i=0;i<maxVisible;i++){const t=ordered[i];const best=map.get(t.id)?.best_score||0;const card=item(`${i+1}. ${t.title}`);card.classList.add('mw-v6-topic');if(best>=25)card.classList.add('done');card.append(el('p','',best>=25?'✓ Đã hoàn thành · Điểm cao nhất '+best+'/30':best?'Đang học · Điểm cao nhất '+best+'/30':'Chưa bắt đầu'));
 const tiers=el('span','mw-v5-pill',`Toán ${grade} · ${t.certified||0}/30 câu đã kiểm chứng`);card.append(tiers);const controls=el('div','mw-v5-row');controls.style.marginTop='12px';const a=el('a','mw-v5-btn','▤ Lý thuyết · Video · FAQ');a.href='learn.html?grade='+grade+'&topic='+encodeURIComponent(t.id);controls.append(a);const b=btn('Kiểm tra 30 câu',()=>begin('topic',t.id),best>=25?'':'mw-v5-gradient');controls.append(b);card.append(controls);grid.append(card)}c.append(grid);
 const timeline=el('div','mw-v6-timeline');const groups=Math.ceil(ordered.length/3);const shown=Math.min(groups,7);for(let g=0;g<shown;g++){const segment=ordered.slice(g*3,g*3+3);const complete=segment.every(t=>(map.get(t.id)?.best_score||0)>=25);const node=el('div','mw-v6-timeline-step'+(complete?' done':g===activeGroup?' active':''));node.append(el('span','',complete?'✓':g<=activeGroup?'▶':'🔒'),el('small','',`Chặng ${g+1}`));timeline.append(node)}if(groups>shown)timeline.append(el('span','mw-v5-pill',`+${groups-shown} chặng`));c.append(timeline);app.append(c);
 const note=item('Tình trạng ngân hàng câu hỏi','Đề chính thức chỉ sử dụng câu đã được Admin kiểm chứng độc lập. Câu ứng viên chưa duyệt không được tính để đạt 25/30 và mở khóa.');note.style.marginTop='15px';const link=el('a','mw-v5-btn','Mở thư viện học tập →');link.href='learn.html';note.append(link);app.append(note)}
async function showTutor(){
 const selected=grade;
 const panel=item('✦ Gia sư AI · Lộ trình thích ứng theo bài làm',
  'Mỗi câu đã kiểm chứng chỉ được dùng một lần để cập nhật mức thành thạo. Kết quả là ước lượng hỗ trợ học tập, không phải chứng nhận năng lực chuẩn hóa.');
 panel.style.marginTop='18px';panel.id='mw-v5-live-tutor';panel.classList.add('mw-v23-ai-panel');app.append(panel);
 try{
  const plan=await call('/tutor-plan/'+selected);
  if(selected!==grade||!panel.isConnected)return;
  const model=plan.trained_predictor||(await call('/tutor/'+selected)).online_training;
  if(model){
   const learned=el('p','mw-v5-sub',`Mô hình AI học trực tuyến: ${model.examples} câu đã dùng để cập nhật hệ số · ${model.ready_for_soft_suggestions?'Đang hỗ trợ chọn mức luyện':'Cần thêm bằng chứng để dự đoán'} · Chưa hiệu chuẩn trên học sinh đại diện.`);
   learned.setAttribute('role','status');panel.append(learned);
   const audit=document.createElement('details');audit.className='mw-v25-evidence-details';
   const heading=document.createElement('summary');heading.textContent='Vì sao AI có hoặc chưa có đủ dữ liệu dự đoán?';audit.append(heading);
   const facts=el('p','mw-v5-sub',`Dữ liệu: ${model.examples} câu đã chấm · ${model.topics_with_3_examples||0} chủ đề có ≥3 câu · ${model.tiers_with_4_examples||0} mức độ có ≥4 câu · ${model.evaluated_after_warmup||0} lần kiểm tra dự đoán theo thời gian.`);
   audit.append(facts);
   if(model.held_forward_brier!==null&&model.held_forward_brier!==undefined){
    audit.append(el('p','mw-v5-sub',`Sai số dự đoán: ${model.held_forward_brier}; mốc tham chiếu: ${model.reference_brier}. Điểm sai số nhỏ không đồng nghĩa đã được hiệu chuẩn trên học sinh thực tế.`));
   }
   for(const reason of (model.readiness_reasons||[]))audit.append(el('p','mw-v25-readiness-note','• '+reason));
   if(model.ready_for_soft_suggestions)audit.append(el('p','mw-v5-sub','Đã đủ điều kiện gợi ý THỬ NGHIỆM, không dùng để phân loại năng lực chính thức.'));
   panel.append(audit);
  }
  const retrain=btn('↻ Huấn luyện lại AI từ bài đã chấm',async()=>{
   retrain.disabled=true;
   try{
    const trained=await call('/tutor/retrain/'+selected,{method:'POST'});
    panel.append(el('p','mw-v5-sub',`Đã tái huấn luyện từ ${trained.training.examples} câu đã kiểm chứng. Đây là dự đoán hỗ trợ học tập, không phải chứng nhận trình độ.`));
    if(selected===grade)setTimeout(()=>show(),200);
   }catch(e){panel.append(el('p','mw-v5-sub','Không thể huấn luyện lại: '+e.message))}
   finally{retrain.disabled=false}
  });panel.append(retrain);
  if(plan.status!=='ready'){
   panel.append(el('p','mw-v5-sub',plan.message||'Chưa đủ dữ liệu đã kiểm chứng để xây dựng lộ trình chính thức.'));
   return;
  }
  const summary=el('div','mw-v23-summary');
  summary.append(el('span','mw-v5-pill',`Chặng ${plan.current_stage}/${plan.total_stages}`));
  summary.append(el('span','mw-v5-pill',`Còn ${plan.stage_remaining}/3 chủ đề cần hoàn thành`));
  summary.append(el('span','mw-v5-pill',`${plan.trained_answers} câu trả lời đã dùng để học`));
  panel.append(summary);
  panel.append(el('p','mw-v5-sub','AI tự cập nhật sau mỗi bài đã chấm, ưu tiên những câu trả lời sai được xác minh. Câu bỏ qua không bị kết luận là sai. Chỉ ba chủ đề thuộc chặng hiện tại được đề xuất.'));
  const grid=el('div','mw-v5-grid mw-v23-tutor-grid');
  for(const rec of plan.topics){
   const score=rec.mastery_estimate===null?'chưa đủ dữ liệu xác định':`ước lượng ${rec.mastery_estimate}%`;
   const card=item((rec.completed?'✓ ':'')+rec.title,`${score} · ${rec.verified_answered} câu đã đánh giá · ${rec.confidence}`);
   card.classList.add('mw-v23-topic-card');
   card.append(el('p','mw-v23-reason',rec.reason));
   card.append(el('p','mw-v5-sub',`Đúng ${rec.correct} · Sai ${rec.wrong} · Bỏ qua ${rec.skipped} · Mức ưu tiên: ${rec.focus_tier}`));
   if(rec.focus_basis)card.append(el('p','mw-v5-sub',rec.focus_basis));
   if(rec.online_prediction_ready&&rec.predicted_correct_by_tier){
    const chances=['nền tảng','trung cấp','nâng cao'].map(t=>{
     const p=rec.predicted_correct_by_tier[t];
     return typeof p==='number'?`${t}: khoảng ${Math.round(p*10)*10}%`:null;
    }).filter(Boolean);
    if(chances.length)card.append(el('p','mw-v24-prediction',`Dự đoán thử nghiệm khả năng làm đúng câu MỚI (chưa hiệu chuẩn): ${chances.join(' · ')}`));
   }
   const steps=el('ol','mw-v23-steps');
   for(const step of rec.learning_steps){const li=el('li','',step.label);steps.append(li)}
   card.append(steps);
   const controls=el('div','mw-v5-row');
   const link=el('a','mw-v5-btn','📘 Học đúng chủ đề →');link.href=rec.learning_url;
   controls.append(link);
   if(!rec.completed)controls.append(btn('Làm bài kiểm tra 30 câu',()=>begin('topic',rec.topic_id),'mw-v5-gradient'));
   card.append(controls);grid.append(card);
  }
  panel.append(grid);
  panel.append(el('p','mw-v5-sub',plan.notice+' '+plan.unlock_condition));
  const exportData=btn('⬇ Xuất dữ liệu đã dùng để cá nhân hóa (JSON)',async()=>{
   try{const privateData=await call('/tutor-data/'+selected);
    const blob=new Blob([JSON.stringify(privateData,null,2)],{type:'application/json'});
    const link=document.createElement('a');link.href=URL.createObjectURL(blob);
    link.download=`MATHWEB_AI_HO_SO_LOP_${selected}.json`;link.click();
    setTimeout(()=>URL.revokeObjectURL(link.href),5000);
   }catch(e){panel.append(el('p','mw-v5-sub','Không xuất được hồ sơ: '+e.message))}
  });panel.append(exportData);
 }catch(e){if(panel.isConnected)panel.append(el('p','','Không đọc được lộ trình AI: '+e.message))}
}
function goToQuestion(index){
 if(!attempt)return;
 cursor=Math.max(0,Math.min(attempt.total-1,index));
 try{sessionStorage.setItem('mw-placement-cursor:'+attempt.attempt_id,String(cursor))}catch{}
 scheduleSave();exam();
}
function examNavigation(){
 const nav=el('div','mw-v17-exam-nav');
 const answered=attempt.questions.filter(q=>Object.prototype.hasOwnProperty.call(answers,q.qid)).length;
 nav.append(el('p','mw-v5-sub',`Đã trả lời ${answered}/${attempt.total} · Còn ${attempt.total-answered} câu chưa làm`));
 const topicSelect=el('select','mw-v17-topic-jump');
 topicSelect.setAttribute('aria-label','Chuyển đến chủ đề trong bài kiểm tra');
 const visited=new Set();
 attempt.questions.forEach((q,i)=>{
  if(visited.has(q.topic_id))return;visited.add(q.topic_id);
  const option=el('option','',`${q.title} · câu ${i+1}`);option.value=String(i);
  topicSelect.append(option);
 });
 const activeTopic=attempt.questions[cursor].topic_id;
 const first=attempt.questions.findIndex(q=>q.topic_id===activeTopic);
 topicSelect.value=String(first);
 topicSelect.addEventListener('change',()=>goToQuestion(Number(topicSelect.value)));
 nav.append(topicSelect);
 nav.append(btn('Đến câu chưa làm',()=>{
  const next=attempt.questions.findIndex((q,i)=>i>cursor&&!Object.prototype.hasOwnProperty.call(answers,q.qid));
  const firstMissing=attempt.questions.findIndex(q=>!Object.prototype.hasOwnProperty.call(answers,q.qid));
  if(next>=0)goToQuestion(next);else if(firstMissing>=0)goToQuestion(firstMissing);
 },'mw-v17-jump'));
 return nav;
}
async function begin(mode,topicId=null){if(working)return;working=true;loading();try{attempt=await call('/start',{method:'POST',body:JSON.stringify({grade,mode,topic_id:topicId})});geoStudentPreviews.clear();answers=attempt.draft_answers||{};try{cursor=Math.max(0,Math.min(attempt.total-1,Number(sessionStorage.getItem('mw-placement-cursor:'+attempt.attempt_id))||0))}catch{cursor=0}exam()}catch(e){show();alertText(e.message+(e.data?.detail?.available!==undefined?` (hiện có ${e.data.detail.available}/30 câu)` :''))}finally{working=false}}
function exam(){section();if(attempt.mode==='placement'&&attempt.assessment_quality&&!attempt.assessment_quality.complete_three_tier_coverage){const quality=attempt.assessment_quality;const caveat=el('p','mw-v5-sub',`Đánh giá thử, chưa đủ độ phủ: ${quality.reviewed_items} câu đã duyệt; ${quality.unreviewed_items} câu ứng viên; ${quality.topics_missing_verified_tiers} chủ đề thiếu 3 câu/mức. Chỉ câu đã duyệt được dùng để cập nhật ước lượng năng lực.`);caveat.setAttribute('role','status');app.append(caveat)}if(attempt.mode==='fixed_placement')app.append(examNavigation());const q=attempt.questions[cursor];const c=item(attempt.mode==='fixed_placement'?'Đề đầu vào CỐ ĐỊNH · Toán '+grade:attempt.mode==='placement'?'Bài thử đầu vào · Toán '+grade:'Kiểm tra chủ đề · 30 câu');c.append(el('div','mw-v5-kpi',`${cursor+1} / ${attempt.total}`));c.append(el('div','mw-v5-progress'));c.lastChild.append(el('span'));c.lastChild.lastChild.style.width=(100*(cursor+1)/attempt.total).toFixed(1)+'%';c.append(el('h2','',q.question));c.append(el('p','',q.title+' · '+(q.difficulty||'Chưa phân loại độ khó')));
 // Draw a constrained diagram INSIDE the question. Do not fabricate unverified measurements.
 const inline=window.MATHWEB_INLINE_GEOMETRY?.render(q);
 if(inline)c.append(inline);
 const grid=el('div','mw-v5-options');
 if(q.question_type==='multiple_choice'){q.choices.forEach((option,i)=>{const b=el('button',answers[q.qid]===i?'selected':'',String.fromCharCode(65+i)+'. '+option);b.onclick=()=>{answers[q.qid]=i;scheduleSave();exam()};grid.append(b)})}
 else if(q.question_type==='true_false'){['Đúng','Sai'].forEach(value=>{const b=el('button',answers[q.qid]===value?'selected':'',value);b.onclick=()=>{answers[q.qid]=value;scheduleSave();exam()};grid.append(b)})}
 else {const input=el('input');input.type='text';input.placeholder='Nhập câu trả lời của bạn';input.setAttribute('aria-label','Câu trả lời tự luận');input.value=answers[q.qid]??'';input.addEventListener('input',()=>{if(input.value.trim())answers[q.qid]=input.value.trim();else delete answers[q.qid];scheduleSave()});grid.append(input)}c.append(grid);
 const bar=el('div','mw-v5-row');bar.style.marginTop='20px';const prev=btn('← Câu trước',()=>{goToQuestion(cursor-1)});prev.disabled=cursor===0;bar.append(prev,btn('Bỏ qua',()=>{delete answers[q.qid];scheduleSave();if(cursor<attempt.total-1)goToQuestion(cursor+1);else exam()}));
 if(cursor<attempt.total-1)bar.append(btn('Câu tiếp →',()=>goToQuestion(cursor+1),'mw-v5-gradient'));
 else bar.append(btn('Nộp bài và phân tích →',submit,'mw-v5-gradient'));
 if(attempt.mode==='fixed_placement'&&cursor<attempt.total-1)bar.append(btn('Nộp bài',submit));
 c.append(bar);app.append(c);const saveState=el('p','mw-v5-sub','Bản nháp tự động lưu khi bạn chọn hoặc nhập đáp án.');saveState.id='mw-v7-save-state';app.append(saveState);app.append(el('p','mw-v5-sub',`Đã chọn đáp án: ${Object.keys(answers).length}/${attempt.total}. Câu không trả lời được tính là bỏ qua. Kết quả do máy chủ chấm.`))}
async function submit(){
 if(working||!attempt)return;
 const unanswered=attempt.questions.filter(q=>!Object.prototype.hasOwnProperty.call(answers,q.qid)).length;
 const message=unanswered>0
  ?`Bạn còn ${unanswered} câu chưa trả lời. Các câu này sẽ tính là bỏ qua. Bạn chắc chắn muốn nộp bài?`
  :'Bạn muốn nộp bài và xem kết quả chấm trên máy chủ?';
 if(!window.confirm(message))return;
 clearTimeout(saveTimer);working=true;loading();try{const results=await call('/submit/'+encodeURIComponent(attempt.attempt_id),{method:'POST',body:JSON.stringify({answers})});attempt=null;status=await call('/status/'+grade);show();review(results)}catch(e){if(attempt)exam();alertText(e.message)}finally{working=false}}
function review(results){const old=document.getElementById('mw-v5-reviews');if(old)old.remove();const box=el('section','mw-v5-card');box.id='mw-v5-reviews';box.style.marginTop='20px';box.append(el('h2','','Kết quả theo đúng thứ tự làm bài'));box.append(el('p','',`Đúng ${results.correct} · Sai ${results.wrong} · Bỏ qua ${results.skipped} / ${results.total}.`));
 if(results.review_notice)box.append(el('p','mw-v5-sub',results.review_notice));
 if(results.mode==='fixed_placement')box.append(el('p','mw-v5-sub',
   'Lưu ý: Bài đầu vào chỉ có giá trị mô tả kết quả trên nội dung đã duyệt. '
   +'Chưa có bằng chứng hiệu chuẩn để kết luận chính xác năng lực của mọi học sinh. '
   +'Câu bỏ qua được thống kê nhưng không tự động xem là không biết kiến thức.'));
 const list=el('div','mw-v5-review');(results.review||[]).forEach(item=>{const article=el('article');article.dataset.verdict=item.verdict;const heading=el('h3','',`Câu ${item.number} · ${item.topic} · ${item.verdict==='correct'?'✓ Đúng':item.verdict==='wrong'?'✕ Sai':'○ Bỏ qua'}`);article.append(heading,el('p','',item.question),el('p','',`Bạn chọn: ${item.answer===undefined||item.answer===null?'Bỏ qua':typeof item.answer==='number'&&item.choices.length?item.choices[item.answer]||'Không hợp lệ':item.answer}`),el('p','',`Đáp án: ${item.expected}`),el('p','',`Lời giải: ${item.explanation}`));list.append(article)});box.append(list);
 if(results.objective_evidence?.topics?.length){
 const evidence=el('section','mw-v5-card');evidence.append(el('h2','','Đánh giá theo chủ đề và mức độ'));
 evidence.append(el('p','mw-v5-sub','Điểm toàn bài có tính câu bỏ qua. Khoảng Wilson 95% dưới đây chỉ tính trên các câu đã trả lời; bỏ qua là thiếu bằng chứng chứ không tự động được xem là sai năng lực. Kết quả chưa phải chứng nhận năng lực chuẩn hóa.'));
 const focus=results.objective_evidence.topics.map(t=>({topic:t,miss:Object.values(t.tiers).reduce((n,v)=>n+v.wrong+v.skipped,0)})).sort((a,b)=>b.miss-a.miss).slice(0,3);
 function detailCard(t){const card=item(t.title);for(const [tier,v] of Object.entries(t.tiers)){
 card.append(el('p','',`${tier}: ${v.correct}/${v.answered??(v.correct+v.wrong)} đúng trên số câu đã trả lời · ${v.skipped} bỏ qua · ${v.feedback} · Khoảng Wilson cho câu đã làm: ${v.wilson_95_percent?.join('–')||'chưa có'}%`));}return card}
 for(const f of focus)evidence.append(detailCard(f.topic));
 // A long fixed form spans 49-51 topics. Show every topic on demand while
 // avoiding a wall of 150 tier summaries on mobile by default.
 const all=document.createElement('details');all.className='mw-v19-all-diagnostics';
 const title=document.createElement('summary');title.textContent=`Xem đầy đủ ${results.objective_evidence.topics.length} chủ đề và 3 mức độ`;all.append(title);
 const rest=el('div','mw-v5-grid');for(const t of results.objective_evidence.topics)rest.append(detailCard(t));all.append(rest);evidence.append(all);box.append(evidence)}
 const exportButton=btn('Xuất hồ sơ kết quả (JSON)',()=>{const blob=new Blob([JSON.stringify(results,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`MATHWEB_NANG_LUC_LOP_${grade}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),5000)});box.prepend(exportButton);app.append(box);box.scrollIntoView({behavior:'smooth',block:'start'})}
refresh();
})();
