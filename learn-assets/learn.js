"use strict";
let currentVideoId=null;
const $=id=>document.getElementById(id);let topics=[],lessons={},diagnostic=[],current=null,quizIndex=0,answered=false,correctCount=0,wrongCount=0,quizPoints=0,quizBank=[],quizMistakes=[];
const safe=(x)=>String(x??'');
function fillList(id,values){const el=$(id);el.replaceChildren();for(const value of values){const li=document.createElement('li');li.textContent=safe(value);el.append(li)}}
function filter(){const grade=Number($('grade').value),term=$('search').value.trim().toLocaleLowerCase('vi');const matches=topics.filter(t=>t.grade===grade&&t.title.toLocaleLowerCase('vi').includes(term));const select=$('topic'),old=select.value;select.replaceChildren();for(const t of matches){const o=document.createElement('option');o.value=t.id;o.textContent=t.title;select.append(o)}if(matches.some(t=>t.id===old))select.value=old;$('count').textContent=`${matches.length} chủ đề phù hợp`}
function key(){return 'mathweb_learn_progress_'+current.id}
function getProgress(){try{return JSON.parse(localStorage.getItem(key()))||{}}catch{return {}}}
function saveProgress(v){try{localStorage.setItem(key(),JSON.stringify({...getProgress(),...v}))}catch{}}
function progress(){const p=getProgress(),percent=Math.round((Number(!!p.read)+Number(!!p.example)+Number(!!p.quiz))*100/3);$('bar').style.width=percent+'%';$('progress-label').textContent='Tiến độ trên thiết bị: '+percent+'%'}
function tab(name){document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('hidden',t.id!==name));if(!current)return;if(name==='example')saveProgress({read:true});if(name==='quiz')saveProgress({read:true,example:true});progress()}
function openTopic(id){current=topics.find(t=>t.id===id);if(!current)return;const lesson=lessons[current.id];$('heading').textContent=current.title;$('tag').textContent='Toán '+current.grade;$('summary').textContent=lesson?.summary||'Danh mục kiến thức hiện có; nội dung bài giảng chi tiết chưa được biên soạn và kiểm chứng cho chủ đề này.';fillList('goals',lesson?.goals||['Nắm khái niệm và điều kiện áp dụng','Tìm hiểu các kiến thức con được liệt kê','Luyện tập với câu hỏi phù hợp chủ đề']);fillList('formulas',lesson?.formulas||['Chưa có công thức đã được xác minh trong hệ thống bài học.']);fillList('subtopics',current.subtopics?.length?current.subtopics:['Chưa có danh sách kiến thức con']);$('example-q').textContent=lesson?.example?.question||'Chưa có ví dụ được kiểm chứng cho chủ đề này.';fillList('example-steps',lesson?.example?.steps||[]);$('example-a').textContent=lesson?.example?.answer?'Kết quả: '+lesson.example.answer:'';$('video-link').href='https://www.youtube.com/results?search_query='+encodeURIComponent('Toán '+current.grade+' '+current.title+' bài giảng');const faq=$('faq-content');faq.replaceChildren();const questions=lesson?.faq||[{q:'Bài học này cần nhớ điều gì?',a:lesson?.summary||'Đọc mục Kiến thức và những nội dung con của chủ đề.'},{q:'Làm sao luyện tập sau khi học?',a:'Mở mục Video & luyện tập rồi chọn Chuyển sang luyện tập.'}];for(const f of questions){const d=document.createElement('details');d.className='faq-item';const q=document.createElement('summary');q.textContent=f.q;const a=document.createElement('p');a.textContent=f.a;d.append(q,a);faq.append(d)}const player=$('video-player');player.replaceChildren();player.dataset.videoTopic='';currentVideoId=lesson?.youtube_id||null;quizIndex=0;correctCount=0;wrongCount=0;quizPoints=0;quizMistakes=[];quizBank=buildTopicQuiz(current.id);showQuiz();tab('knowledge');progress();history.replaceState(null,'','?grade='+current.grade+'&topic='+encodeURIComponent(current.id));$('status').textContent='Đã mở bài: '+current.title}
function buildTopicQuiz(id){
 const raw=[...(lessons[id]?.quiz||[]),...diagnostic.filter(q=>q.topic===id)];
 const seen=new Set(),out=[];
 for(const q of raw){if(!q||!Array.isArray(q.choices)||q.choices.length<2||!Number.isInteger(q.correct)||q.correct<0||q.correct>=q.choices.length)continue;
 const signature=JSON.stringify([String(q.q||'').trim(),q.choices,q.correct]);if(seen.has(signature))continue;seen.add(signature);out.push(q)}
 for(let i=out.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[out[i],out[j]]=[out[j],out[i]]}return out;
}
function quizResult(){
 const completed=quizPoints>=100;
 $('quiz-q').textContent=completed?'Đã đạt 100 điểm! Hoàn thành lượt luyện tập.':'Đã hết câu hỏi đã kiểm chứng. Chưa đạt 100 điểm.';
 $('quiz-count').textContent=`Tổng kết: ${quizPoints}/100 điểm · ${correctCount} câu đúng · ${wrongCount} câu sai · ${correctCount+wrongCount} câu đã làm.`;
 $('feedback').replaceChildren();
 const heading=document.createElement('strong');heading.textContent='Các dạng bài cần ôn tiếp:';$('feedback').append(heading);
 if(!quizMistakes.length){$('feedback').append(document.createTextNode(' Chưa ghi nhận dạng bài sai.'))}else{
  const ul=document.createElement('ul'),counts=new Map();for(const m of quizMistakes)counts.set(m,(counts.get(m)||0)+1);
  for(const [kind,n] of counts){const li=document.createElement('li');li.textContent=kind+' ('+n+' câu sai)';ul.append(li)}$('feedback').append(ul)
 }
 saveProgress({quiz:completed,quizScore:quizPoints,quizCorrect:correctCount,quizWrong:wrongCount,quizMistakes,quizAt:Date.now()});progress();
}
function showQuiz(){
 answered=false;$('choices').replaceChildren();$('feedback').replaceChildren();$('next').classList.add('hidden');
 if(!quizBank.length){$('quiz-q').textContent='Chủ đề này chưa có câu hỏi đã kiểm chứng để luyện tập.';$('quiz-count').textContent='0/100 điểm';return}
 if(quizPoints>=100||quizIndex>=quizBank.length){quizResult();return}
 const item=quizBank[quizIndex];$('quiz-q').textContent=item.q;
 $('quiz-count').textContent=`Câu ${quizIndex+1}/${quizBank.length} · ${quizPoints}/100 điểm · Đúng ${correctCount} · Sai ${wrongCount}`;
 item.choices.forEach((choice,i)=>{const b=document.createElement('button');b.className='choice';b.textContent=String.fromCharCode(65+i)+'. '+choice;b.onclick=()=>{
  if(answered)return;answered=true;const ok=i===item.correct;
  if(ok){correctCount++;quizPoints=Math.min(100,quizPoints+5)}else{wrongCount++;quizPoints=Math.max(0,quizPoints-1);quizMistakes.push(item.kind||item.type||item.skill||item.q)}
  $('feedback').textContent=(ok?'Chính xác. ':'Chưa đúng. ')+(item.why||'');
  [...$('choices').children].forEach((el,j)=>{el.disabled=true;el.classList.add(j===item.correct?'correct':j===i?'wrong':'')});
  $('quiz-count').textContent=`Câu ${quizIndex+1}/${quizBank.length} · ${quizPoints}/100 điểm · Đúng ${correctCount} · Sai ${wrongCount}`;
  $('next').textContent=quizPoints>=100?'Xem tổng kết':'Câu tiếp theo';$('next').classList.remove('hidden')
 };$('choices').append(b)})
}
async function init(){try{const responses=await Promise.all([fetch('learn-assets/topics.json'),fetch('learn-assets/verified-lessons.json'),fetch('learn-assets/diagnostic-bank.json')]);if(responses.some(r=>!r.ok))throw Error('Không tải được thư viện');[topics,lessons,diagnostic]=await Promise.all(responses.map(r=>r.json()));filter();const params=new URLSearchParams(location.search),id=params.get('topic'),t=topics.find(x=>x.id===id);if(t){$('grade').value=String(t.grade);filter();$('topic').value=t.id;openTopic(t.id)}else if(params.has('grade')&&['10','11','12'].includes(params.get('grade'))){$('grade').value=params.get('grade');filter();if($('topic').value)openTopic($('topic').value)}else if($('topic').value)openTopic($('topic').value);$('status').textContent=`Đã tải ${topics.length} chủ đề`;}catch(e){$('status').textContent='Không thể tải dữ liệu bài học. Kiểm tra kết nối và thử tải lại trang.'}}
$('grade').onchange=()=>{filter();if($('topic').value)openTopic($('topic').value)};let searchTimer;$('search').oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{filter();if($('topic').value)openTopic($('topic').value)},120)};$('topic').onchange=()=>{if($('topic').value)openTopic($('topic').value)};document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>tab(b.dataset.tab));$('next').onclick=()=>{quizIndex++;showQuiz()};init();
// Fetch video recommendations only when the video tab is opened.
const originalTab=tab;tab=function(name){originalTab(name);if(name==='video'&&current&&window.MathWebVideos){window.MathWebVideos.render($('video-player'),current.grade,current.title,currentVideoId)}};


// Expanded, reviewed knowledge sections, rendered without replacing existing lesson components.
function mwShowKnowledgeSections(){
 const old=document.getElementById('mw-knowledge-sections');if(old)old.remove();
 if(!current)return;const data=lessons[current.id];if(!Array.isArray(data?.sections)||!data.sections.length)return;
 const target=document.getElementById('formulas')||document.getElementById('theory');if(!target)return;
 const panel=document.createElement('section');panel.id='mw-knowledge-sections';panel.style.cssText='margin:18px 0;padding:18px;border:1px solid #d8d2f6;border-radius:16px;background:rgba(125,100,230,.05)';
 const heading=document.createElement('h3');heading.textContent='Chuyên đề kiến thức chi tiết';panel.append(heading);
 for(const part of data.sections){const details=document.createElement('details');details.style.cssText='padding:10px 0;border-bottom:1px solid #ded9ed';const title=document.createElement('summary');title.style.cssText='cursor:pointer;font-weight:700';title.textContent=part.level+' · '+part.title;const p=document.createElement('p');p.textContent=part.details;details.append(title,p);panel.append(details)}
 target.insertAdjacentElement('afterend',panel);
}

const mwOriginalOpenTopic=openTopic;openTopic=function(id){const result=mwOriginalOpenTopic(id);mwShowKnowledgeSections();return result};
