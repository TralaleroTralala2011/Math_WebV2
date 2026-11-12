"use strict";
const $=id=>document.getElementById(id);let topics=[],lessons={},diagnostic=[],questions=[],idx=0,answers={},active=null,gamePoints=0,gameCorrect=0,gameWrong=0;
const storageKey=g=>{
 let user='';try{const raw=JSON.parse(localStorage.getItem('mathweb_user')||'{}');user=String(raw.id||raw.username||raw.user_id||'');}catch{}
 return 'mathweb_path_diagnostic_v2_'+encodeURIComponent(user||'unknown')+'_'+g;
};
function safeRead(g){try{return JSON.parse(localStorage.getItem(storageKey(g)))}catch{return null}}
function selectedGrade(){return Number($('grade').value)}
function available(){return topics.filter(t=>t.grade===selectedGrade()&&(diagnostic.some(q=>q.topic===t.id)||lessons[t.id]?.quiz?.length))}
function note(){const count=matrixQuestions.filter(q=>q.grade===selectedGrade()&&validMatrix(q)).length;$('testnote').textContent=count?`Khảo sát đầu vào Toán ${selectedGrade()}: 30 câu/lượt, chọn lần lượt 5 chủ đề, mỗi chủ đề 6 câu (3 trắc nghiệm, 2 đúng/sai, 1 trả lời ngắn), theo ma trận độ khó và lý thuyết/thực tế. Chấm điểm khi nộp bài, lưu kết quả và gợi ý lộ trình. Đây là đánh giá sơ bộ, không thay thế bài thi chuẩn hóa.`:'Khối này chưa có bộ câu hỏi đầu vào hoàn chỉnh. Không thể đánh giá năng lực.';$('start').disabled=count<6}

const DIAGNOSTIC_COUNT=30;
let matrixQuestions=[];
let choiceOrderCache=new Map();
const normalizeShort=value=>String(value??'').trim().toLowerCase().replace(/\s+/g,' ').replace(/,/g,'.');
// Numeric equivalence for short answers. No eval/Function; any invalid input returns null.
// Supports decimals, fractions, parenthesized arithmetic, sqrt/√, π and exponents.
function parseNumericShort(raw){
 let s=normalizeShort(raw).replace(/[−–]/g,'-').replace(/×/g,'*').replace(/÷/g,'/').replace(/π/g,'pi').replace(/√/g,'sqrt');
 if(!s||s.length>100||/[^0-9a-z+\-*/^().]/.test(s))return null;
 s=s.replace(/(\d)(sqrt|pi|\()/g,'$1*$2').replace(/(\))(\d|pi|sqrt|\()/g,'$1*$2').replace(/(pi)(\d|pi|sqrt|\()/g,'$1*$2');
 const tokens=s.match(/sqrt|pi|(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?|[()+\-*/^]/g);
 if(!tokens||tokens.join('')!==s||tokens.length>80)return null;
 let i=0;
 const expression=()=>{let v=term();while(tokens[i]==='+'||tokens[i]==='-'){const op=tokens[i++],b=term();v=op==='+'?v+b:v-b}return v};
 const term=()=>{let v=unary();while(tokens[i]==='*'||tokens[i]==='/'){const op=tokens[i++],b=unary();v=op==='*'?v*b:v/b}return v};
 const unary=()=>{if(tokens[i]==='+'){i++;return unary()}if(tokens[i]==='-'){i++;return -unary()}return power()};
 const power=()=>{let v=atom();if(tokens[i]==='^'){i++;v=Math.pow(v,unary())}return v};
 const atom=()=>{const t=tokens[i++];if(t==='('){const v=expression();if(tokens[i++]!==')')throw Error('parentheses');return v}if(t==='sqrt'){let v;if(tokens[i]==='('){i++;v=expression();if(tokens[i++]!==')')throw Error('sqrt')}else{v=atom()}return Math.sqrt(v)}if(t==='pi')return Math.PI;if(t===undefined||!/^(?:\d|\.)/.test(t))throw Error('number');return Number(t)};
 try{const result=expression();return i===tokens.length&&Number.isFinite(result)?result:null}catch{return null}
}
function equivalentShort(given,expected){
 if(given===undefined||given===null)return false;
 if(normalizeShort(given)===normalizeShort(expected))return true;
 const a=parseNumericShort(given),b=parseNumericShort(expected);
 return a!==null&&b!==null&&Math.abs(a-b)<=1e-8*Math.max(1,Math.abs(a),Math.abs(b));
}
function shuffledChoices(choices){
 const indexed=choices.map((text,index)=>({text,index}));
 for(let i=indexed.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[indexed[i],indexed[j]]=[indexed[j],indexed[i]]}
 return indexed;
}
const MATRIX_SLOTS=[['nen_tang','ly_thuyet','trac_nghiem'],['nen_tang','ly_thuyet','dung_sai'],['trung_cap','ly_thuyet','trac_nghiem'],['trung_cap','thuc_te','trac_nghiem'],['kho','ly_thuyet','dung_sai'],['kho','thuc_te','tra_loi_ngan']];
function validMatrix(q){
 if(!q||!Number.isInteger(q.slot)||q.slot<1||q.slot>6||typeof q.question!=='string'||!q.question.trim()||typeof q.solution!=='string'||!q.solution.trim()||q.answer===undefined||q.answer===null||!String(q.answer).trim())return false;
 const [difficulty,context,format]=MATRIX_SLOTS[q.slot-1];
 if(q.difficulty!==difficulty||q.context!==context||q.format!==format)return false;
 if(format==='trac_nghiem')return Array.isArray(q.choices)&&q.choices.length===4&&q.choices.every(x=>typeof x==='string'&&x.trim())&&new Set(q.choices.map(x=>x.trim().toLowerCase())).size===4&&Number.isInteger(q.correct)&&q.correct>=0&&q.correct<4&&q.answer===q.choices[q.correct];
 if(format==='dung_sai')return ['true','false'].includes(String(q.answer));
 return String(q.answer).trim().length>0;
}
function makeTest(){
 const grade=selectedGrade(),bank=matrixQuestions.filter(q=>q.grade===grade&&validMatrix(q)),groups=new Map();
 for(const q of bank){if(!groups.has(q.topic_id))groups.set(q.topic_id,[]);groups.get(q.topic_id).push(q)}
 const complete=[];
 for(const [id,group] of groups){
  const sorted=group.slice().sort((a,b)=>a.slot-b.slot);
  if(sorted.length!==6||sorted.some((q,i)=>q.slot!==i+1))continue;
  const topic=topics.find(t=>t.id===id&&t.grade===grade);
  if(topic)complete.push({topic,rows:sorted});
 }
 // Cover different topics on consecutive attempts without counting untested topics as weak.
 // Keep entire six-question topic blocks, preserving every matrix ratio.
 if(!complete.length){questions=[];return 0}
 const rotationKey=storageKey(grade)+'_next_topic_index';
 let start=0;
 try{const saved=Number(localStorage.getItem(rotationKey));if(Number.isSafeInteger(saved)&&saved>=0)start=saved%complete.length}catch{}
 const topicCount=Math.min(Math.floor(DIAGNOSTIC_COUNT/6),complete.length);
 const selected=Array.from({length:topicCount},(_,j)=>complete[(start+j)%complete.length]);
 questions=selected.flatMap(({topic,rows})=>rows.map(q=>({topic,q})));
 choiceOrderCache.clear();
 try{localStorage.setItem(rotationKey,String((start+topicCount)%complete.length))}catch{}
 return questions.length;
}
// Restore an unfinished local assessment without advancing to another topic block.
function resumeDiagnosticDraft(){
 const grade=selectedGrade(),key='mathweb_diagnostic_draft_'+storageKey(grade);
 let draft;try{draft=JSON.parse(sessionStorage.getItem(key)||'null')}catch{return false}
 if(!draft||draft.grade!==grade||!Array.isArray(draft.ids)||draft.ids.length!==DIAGNOSTIC_COUNT)return false;
 const index=new Map(matrixQuestions.filter(q=>q.grade===grade&&validMatrix(q)).map(q=>[q.id,q]));
 const recovered=[];const seen=new Set();
 for(const id of draft.ids){if(typeof id!=='string'||seen.has(id))return false;seen.add(id);
  const q=index.get(id),topic=q&&topics.find(t=>t.id===q.topic_id&&t.grade===grade);
  if(!q||!topic)return false;recovered.push({q,topic});
 }
 // Require five complete blocks, not an arbitrary mix of formats or topics.
 for(let i=0;i<recovered.length;i+=6){const block=recovered.slice(i,i+6);
  if(block.length!==6||block.some((entry,j)=>entry.topic.id!==block[0].topic.id||entry.q.slot!==j+1))return false;
 }
 choiceOrderCache.clear();questions=recovered;idx=Number.isSafeInteger(draft.idx)?Math.max(0,Math.min(questions.length-1,draft.idx)):0;answers={};
 if(draft.answers&&typeof draft.answers==='object')for(const [key,v] of Object.entries(draft.answers)){
  const i=Number(key);if(!Number.isInteger(i)||i<0||i>=questions.length)continue;
  const q=questions[i].q;
  if(q.format==='trac_nghiem'&&Number.isInteger(v)&&v>=0&&v<4)answers[i]=v;
  else if(q.format==='dung_sai'&&['true','false'].includes(v))answers[i]=v;
  else if(q.format==='tra_loi_ngan'&&typeof v==='string'&&v.length<=200)answers[i]=v;
 }
 return true;
}
function renderQuestion(){
 if(idx>=questions.length){finish();return}
 const {topic,q}=questions[idx],root=$('choices');root.replaceChildren();
 $('counter').textContent=`Toán ${selectedGrade()} · Câu ${idx+1}/${questions.length} · ${topic.title} · ${q.difficulty.replace('_',' ')} · ${q.context.replace('_',' ')}`;
 $('question').textContent=q.question;
 const select=value=>{answers[idx]=value;$('next').disabled=false;saveDraft()};
 if(q.format==='trac_nghiem'){if(!choiceOrderCache.has(q.id))choiceOrderCache.set(q.id,shuffledChoices(q.choices));choiceOrderCache.get(q.id).forEach(({text:choice,index:originalIndex},i)=>{const b=document.createElement('button');b.type='button';b.textContent=String.fromCharCode(65+i)+'. '+choice;b.classList.toggle('selected',answers[idx]===originalIndex);b.onclick=()=>{[...root.children].forEach(x=>x.classList.remove('selected'));b.classList.add('selected');select(originalIndex)};root.append(b)});}
 else if(q.format==='dung_sai')for(const [value,label] of [['true','Đúng'],['false','Sai']]){const b=document.createElement('button');b.type='button';b.textContent=label;b.classList.toggle('selected',answers[idx]===value);b.onclick=()=>{[...root.children].forEach(x=>x.classList.remove('selected'));b.classList.add('selected');select(value)};root.append(b)}
 else {const input=document.createElement('input');input.type='text';input.placeholder='Nhập đáp án ngắn';input.autocomplete='off';input.style.cssText='width:100%;padding:12px;border:1px solid #777;border-radius:10px';input.value=answers[idx]??'';input.oninput=()=>{if(input.value.trim())select(input.value);else{delete answers[idx];$('next').disabled=true;saveDraft()}};root.append(input)}
 $('next').disabled=!Object.hasOwn(answers,idx);$('next').textContent=idx===questions.length-1?'Nộp bài khảo sát':'Câu tiếp theo';
}
function saveDraft(){try{sessionStorage.setItem('mathweb_diagnostic_draft_'+storageKey(selectedGrade()),JSON.stringify({answers,idx,grade:selectedGrade(),ids:questions.map(x=>x.q.id)}))}catch{}}
function finish(){
 const score={},mistakes=[],dimensions={difficulty:{},context:{},format:{}};let correctCount=0;
 for(let i=0;i<questions.length;i++){
  const {topic,q}=questions[i],given=answers[i];
  const ok=q.format==='trac_nghiem'?given===q.correct:q.format==='tra_loi_ngan'?equivalentShort(given,q.answer):normalizeShort(given)===normalizeShort(q.answer);
  if(ok)correctCount++;
  const s=score[topic.id]??={correct:0,total:0};s.total++;if(ok)s.correct++;
  for(const [name,key] of [['difficulty',q.difficulty],['context',q.context],['format',q.format]]){const cell=dimensions[name][key]??={correct:0,total:0};cell.total++;if(ok)cell.correct++}
  if(!ok)mistakes.push({topic:topic.title,question:q.question,answer:q.format==='dung_sai'?(q.answer==='true'?'Đúng':'Sai'):q.answer,explanation:q.solution,dimension:q.difficulty});
 }
 const result={grade:selectedGrade(),date:new Date().toISOString(),score,dimensions,points:Math.round(100*correctCount/Math.max(1,questions.length)),correctCount,wrongCount:mistakes.length,mistakes,completed:true,total:questions.length,version:4,coverage:Object.keys(score).length};
 try{
  const historyKey=storageKey(selectedGrade())+'_topic_history';
  const history=JSON.parse(localStorage.getItem(historyKey)||'{}');
  const merged=history&&typeof history==='object'&&!Array.isArray(history)?history:{};
  for(const [topicId,progress] of Object.entries(score))merged[topicId]={...progress,updated_at:result.date};
  localStorage.setItem(historyKey,JSON.stringify(merged));
  result.coverage_total=Object.keys(merged).length;
  localStorage.setItem(storageKey(selectedGrade()),JSON.stringify(result));
  sessionStorage.removeItem('mathweb_diagnostic_draft_'+storageKey(selectedGrade()));
 }catch{}
 $('quiz').classList.add('hidden');$('result').classList.remove('hidden');showResult(result);
}
function showResult(result){
 const score=result?.score||{},entries=Object.values(score),correct=entries.reduce((n,v)=>n+v.correct,0),total=entries.reduce((n,v)=>n+v.total,0);
 $('status').textContent=total?`Khảo sát Toán ${selectedGrade()}: ${correct}/${total} câu đúng`:'Chưa có bài kiểm tra';
 $('bar').style.width=(total?Math.round(correct/total*100):0)+'%';
 $('summary').textContent=total?`Lượt gần nhất: ${entries.length} chủ đề, ${total} câu. Tổng số chủ đề đã khảo sát qua các lượt: ${result?.coverage_total||entries.length}. Kết quả sơ bộ, chưa kiểm định độc lập; chủ đề chưa kiểm tra không được xem là yếu.`:'Chọn lớp và bắt đầu khảo sát.';
 $('result').replaceChildren();
 if(total){
  const h=document.createElement('h3');h.textContent=`Báo cáo năng lực: ${Math.round(correct/total*100)}/100 điểm`;$('result').append(h);
  const p=document.createElement('p');p.textContent=`Đúng ${correct}/${total} · Sai ${total-correct} · Phạm vi ${entries.length} chủ đề.`;$('result').append(p);
  const labels={nen_tang:'Nền tảng',trung_cap:'Trung cấp',kho:'Khó',ly_thuyet:'Lý thuyết',thuc_te:'Thực tế',trac_nghiem:'Trắc nghiệm',dung_sai:'Đúng/Sai',tra_loi_ngan:'Trả lời ngắn'};
  for(const [dim,values] of Object.entries(result.dimensions||{})){const sub=document.createElement('p');sub.textContent=(dim==='difficulty'?'Độ khó':dim==='context'?'Nội dung':'Hình thức')+': '+Object.entries(values).map(([k,v])=>`${labels[k]||k} ${v.correct}/${v.total}`).join(' · ');$('result').append(sub)}
  const weak=Object.entries(score).filter(([id,v])=>v.correct/v.total<.7).map(([id])=>topics.find(t=>t.id===id)?.title||id);
  const recommendation=document.createElement('p');recommendation.textContent=weak.length?'Ưu tiên ôn: '+weak.join('; '):'Chưa phát hiện chủ đề dưới 70% trong phạm vi đã khảo sát.';$('result').append(recommendation);
  // Transparent per-topic evidence: show the sample size instead of an unsupported mastery label.
  const breakdown=document.createElement('details');const heading=document.createElement('summary');heading.textContent='Chi tiết điểm từng chủ đề đã khảo sát';breakdown.append(heading);
  const breakdownList=document.createElement('ul');for(const [topicId,stat] of Object.entries(score)){const li=document.createElement('li');const label=topics.find(t=>t.id===topicId)?.title||topicId;li.textContent=`${label}: ${stat.correct}/${stat.total} câu đúng (${Math.round(100*stat.correct/Math.max(1,stat.total))}%). Chỉ mang tính tham khảo với ${stat.total} câu.`;breakdownList.append(li)}breakdown.append(breakdownList);$('result').append(breakdown);
  if(result.mistakes?.length){const h2=document.createElement('h3');h2.textContent='Xem lại câu sai và lời giải';$('result').append(h2);const ul=document.createElement('ul');for(const m of result.mistakes){const li=document.createElement('li');li.textContent=m.topic+': '+m.question+' | Đáp án: '+m.answer+' | '+m.explanation;ul.append(li)}$('result').append(ul)}
  const exportBtn=document.createElement('button');exportBtn.type='button';exportBtn.textContent='Tải báo cáo JSON';exportBtn.onclick=()=>{const blob=new Blob([JSON.stringify(result,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`mathweb-khao-sat-toan-${result.grade}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};$('result').append(exportBtn);
 }
 renderPath(score);
}
function renderPath(score={}){
 let history={};try{history=JSON.parse(localStorage.getItem(storageKey(selectedGrade())+'_topic_history')||'{}')||{}}catch{}
 score={...history,...score};
 const list=topics.filter(t=>t.grade===selectedGrade());list.sort((a,b)=>{const sa=score[a.id],sb=score[b.id];const ra=sa?sa.correct/sa.total:2,rb=sb?sb.correct/sb.total:2;return ra-rb});$('path').replaceChildren();list.forEach((t,i)=>{const v=score[t.id];const item=document.createElement('div');item.className='step';const node=document.createElement('div');node.className='node';node.textContent=String(i+1);const info=document.createElement('div');const title=document.createElement('strong');title.textContent=t.title;const desc=document.createElement('p');desc.textContent=v?`Đầu vào: ${v.correct}/${v.total} câu đúng · ${v.correct/v.total<.7?'Ưu tiên củng cố':'Có thể ôn nâng cao'}`:'Chưa đánh giá năng lực ở chủ đề này';const a=document.createElement('a');a.href='learn.html?topic='+encodeURIComponent(t.id);a.textContent='Mở bài học đầy đủ →';a.href='#journey-lesson';a.onclick=e=>{e.preventDefault();openJourney(t)};info.append(title,desc,a);item.append(node,info);item.tabIndex=0;item.setAttribute('role','button');item.setAttribute('aria-label','Mở bài học '+t.title);item.onclick=e=>{if(e.target.closest('a'))return;openJourney(t)};item.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openJourney(t)}};$('path').append(item)})}
$('start').onclick=()=>{const recovered=resumeDiagnosticDraft();if(!recovered){if(!makeTest())return;idx=0;answers={};saveDraft();}$('quiz').classList.remove('hidden');$('result').classList.add('hidden');renderQuestion()};
$('next').onclick=()=>{if(!Object.hasOwn(answers,idx))return;idx++;saveDraft();renderQuestion()};
$('retest').onclick=()=>{$('result').classList.add('hidden');$('quiz').classList.add('hidden');try{sessionStorage.removeItem('mathweb_diagnostic_draft_'+storageKey(selectedGrade()))}catch{}$('start').focus()};
$('grade').onchange=()=>{note();showResult(safeRead(selectedGrade()))};
Promise.all([fetch('learn-assets/topics.json'),fetch('learn-assets/verified-lessons.json'),fetch('learn-assets/diagnostic-bank.json'),fetch('learn-assets/assessment-matrix-questions.json')]).then(async rs=>{if(rs.some(r=>!r.ok))throw Error('fetch');[topics,lessons,diagnostic,matrixQuestions]=await Promise.all(rs.map(r=>r.json()));note();showResult(safeRead(selectedGrade()))}).catch(()=>{$('testnote').textContent='Không tải được dữ liệu khảo sát. Hãy chạy website qua máy chủ HTTP.';$('start').disabled=true});

// Journey lesson opens in-place. Existing free practice and learn pages remain independent.
let jlTopic=null,jlIndex=0,jlCorrect=0,jlWrong=0,jlPoints=0,jlMistakes=[],jlAnswered=false,jlBank=[];
function jlList(id,arr){const el=$(id);el.replaceChildren();for(const value of arr){const li=document.createElement('li');li.textContent=value;el.append(li)}}
function jlTab(name){for(const id of ['theory','video','exercise'])$('jl-'+id).classList.toggle('hidden',id!==name);document.querySelectorAll('[data-jl]').forEach(b=>b.classList.toggle('active',b.dataset.jl===name))}
function openJourney(t){jlTopic=t;jlIndex=0;jlCorrect=0;jlWrong=0;jlPoints=0;jlMistakes=[];jlBank=[];const unique=new Set();for(const q of [...diagnostic.filter(q=>q.topic===t.id),...(lessons[t.id]?.quiz||[])]){if(!window.MathWebQuestionMix?.valid(q))continue;const k=JSON.stringify([q.q,q.choices,q.correct]);if(unique.has(k))continue;unique.add(k);jlBank.push(q)}for(let i=jlBank.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[jlBank[i],jlBank[j]]=[jlBank[j],jlBank[i]]}if(window.MathWebQuestionMix)jlBank=MathWebQuestionMix.mix(jlBank);const l=lessons[t.id];$('jl-label').textContent='Toán '+t.grade+' · '+(l?'Bài giảng đã biên soạn':'Chủ đề cần ôn');$('jl-title').textContent=t.title;$('jl-summary').textContent=l?.summary||'Nội dung chi tiết chưa được biên soạn và kiểm chứng cho chủ đề này.';jlList('jl-formulas',l?.formulas||['Chưa có công thức được kiểm chứng.']);jlList('jl-subtopics',t.subtopics||[]);$('jl-example').textContent=l?.example?.question||'Chưa có ví dụ đã được kiểm chứng.';jlList('jl-steps',l?.example?.steps||[]);const player=$('jl-player');player.replaceChildren();player.dataset.videoTopic='';$('jl-video-search').href='https://www.youtube.com/results?search_query='+encodeURIComponent('Toán '+t.grade+' '+t.title+' bài giảng');$('jl-unsupported').textContent=l?'':'Bài học chi tiết đang được biên soạn. Các câu hỏi kiểm tra đầu vào vẫn có thể dùng để tự luyện.';jlTab('theory');jlQuiz();$('journey-lesson').classList.remove('hidden');document.body.style.overflow='hidden';$('jl-close').focus()}
function jlQuiz(){const bank=jlBank;const el=$('jl-choices');el.replaceChildren();$('jl-feedback').textContent='';$('jl-next').classList.add('hidden');jlAnswered=false;if(!bank.length){$('jl-question').textContent='Chưa có bài tập được kiểm chứng cho chủ đề này.';$('jl-counter').textContent='';return}if(jlPoints>=100||jlIndex>=bank.length){$('jl-question').textContent=`Điểm ${jlPoints}/100 · Đúng ${jlCorrect} · Sai ${jlWrong}. ${jlPoints>=100?"Đã đạt mục tiêu.":"Đã hết câu hỏi hiện có."}`;$('jl-counter').textContent='Các dạng cần ôn: '+(jlMistakes.length?[...new Set(jlMistakes)].join('; '):'Chưa ghi nhận câu sai.');try{localStorage.setItem('mathweb_journey_lesson_'+encodeURIComponent(jlTopic.id),JSON.stringify({correct:jlCorrect,wrong:jlWrong,points:jlPoints,mistakes:jlMistakes,total:jlIndex,at:Date.now()}))}catch{}return}const q=bank[jlIndex];$('jl-counter').textContent=`Câu ${jlIndex+1}/${bank.length} · ${jlPoints}/100 điểm`;$('jl-question').textContent=q.q;MathWebQuestionMix.render(el,q,(value,selected)=>{if(jlAnswered)return;jlAnswered=true;const ok=MathWebQuestionMix.grade(q,value);if(ok){jlCorrect++;jlPoints=Math.min(100,jlPoints+5)}else{jlWrong++;jlPoints=Math.max(0,jlPoints-1);jlMistakes.push(q.kind||q.type||q.skill||q.q)};const expected=MathWebQuestionMix.kind(q)==='multiple_choice'?String.fromCharCode(65+q.correct)+'. '+q.choices[q.correct]:(q.answer??q.correct_answer??q.correct);$('jl-feedback').textContent=(ok?'Chính xác, +5 điểm. ':'Chưa đúng, −1 điểm (không dưới 0). ')+(q.why||'')+' Đáp án đúng: '+expected;[...el.querySelectorAll('button,input')].forEach(x=>x.disabled=true);if(selected)selected.classList.add(ok?'correct':'wrong');$('jl-next').textContent=jlPoints>=100?'Tổng kết (100 điểm)':'Câu tiếp theo';$('jl-next').classList.remove('hidden')})}

function closeJourney(){$('journey-lesson').classList.add('hidden');document.body.style.overflow=''}
$('jl-close').onclick=closeJourney;$('journey-lesson').onclick=e=>{if(e.target===$('journey-lesson'))closeJourney()};document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('journey-lesson').classList.contains('hidden'))closeJourney()});document.querySelectorAll('[data-jl]').forEach(b=>b.onclick=()=>jlTab(b.dataset.jl));$('jl-next').onclick=()=>{jlIndex++;jlQuiz()};

// Lazy-load the YouTube catalog when the student opens the video tab.
const previousJlTab=jlTab;jlTab=function(name){previousJlTab(name);if(name==='video'&&jlTopic&&window.MathWebVideos){window.MathWebVideos.render($('jl-player'),jlTopic.grade,jlTopic.title,lessons[jlTopic.id]?.youtube_id,"path")}};

// Insert detailed topic sections only for lessons that contain reviewed material.
const mwOpenJourneyBase=openJourney;openJourney=function(t){mwOpenJourneyBase(t);const old=document.getElementById('mw-journey-knowledge');if(old)old.remove();const data=lessons[t.id];if(!Array.isArray(data?.sections)||!data.sections.length)return;const target=$('jl-subtopics');const box=document.createElement('section');box.id='mw-journey-knowledge';const h=document.createElement('h3');h.textContent='Kiến thức chuyên sâu theo cấp độ';box.append(h);for(const part of data.sections){const d=document.createElement('details');const s=document.createElement('summary');s.textContent=part.level+' · '+part.title;s.style.cssText='font-weight:700;cursor:pointer;padding:8px';const p=document.createElement('p');p.textContent=part.details;d.append(s,p);box.append(d)}target.insertAdjacentElement('afterend',box)};
