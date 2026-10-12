(() => {
  const API = window.MATHWEB_API_URL || 'http://127.0.0.1:8000';
  const p = new URLSearchParams(location.search);
  const topic = p.get('topic') || 'menh_de';
  const grade = Number(p.get('grade') || 10);
  const mode = p.get('mode') || 'blitz';
  const name = p.get('name') || 'Thử thách Toán';
  const config = {
    blitz: { label: '⚡ Đấu tốc độ', seconds: 20 },
    boss: { label: '👹 Đấu Boss', seconds: 25 },
    puzzle: { label: '🧩 Giải mật mã', seconds: 35 }
  }[mode] || { label: '⚡ Đấu tốc độ', seconds: 20 };
  const $ = id => document.getElementById(id);
  const state = { questions: [], index: 0, progress: 0, points: 0, correct: 0, wrong: 0, blank: 0, answered: 0, batch: 0, history: [], locked: false, finished: false, seconds: config.seconds, timer: null, pendingNext: false };
  const recordKey = `mathweb_game_records_v3::universal::${topic}::${mode}`;
  $('title').textContent = `${config.label} • ${name}`;
  $('subtitle').textContent = `Toán ${grade} • Đúng +5 điểm • Sai −1 điểm • Đạt 100 để hoàn thành`;
  $('hp').previousElementSibling.textContent = '📈 Tiến độ';
  $('combo').previousElementSibling.textContent = '✅ Đúng';
  $('timer').previousElementSibling.textContent = '⏱️ Giây';
  $('next').textContent = '📘 Đọc xong, câu tiếp theo';
  const context = document.createElement('div'); context.id = 'problemContext'; context.hidden = true; $('question').insertAdjacentElement('beforebegin', context);
  const diagram = document.createElement('div'); diagram.id = 'diagram'; diagram.hidden = true; $('question').insertAdjacentElement('afterend', diagram);
  const record = document.createElement('p'); record.id = 'record'; $('subtitle').insertAdjacentElement('afterend', record);
  const extraStyle = document.createElement('style'); extraStyle.textContent = `#problemContext,#diagram{margin:12px 0;padding:12px;border-radius:14px;border:1px solid rgba(125,211,252,.2);background:rgba(255,255,255,.035);line-height:1.7}#diagram[hidden],#problemContext[hidden]{display:none}#diagram svg{display:block;width:100%;max-height:260px}.short-answer-wrap{display:flex;gap:8px;flex-wrap:wrap}.short-answer-input{flex:1;min-width:180px;padding:13px;border:1px solid #46617d;border-radius:12px;background:#101d31;color:#eef6ff;font:inherit}.statement-list{display:grid;gap:8px}.statement-row{display:flex;gap:10px;padding:10px;border:1px solid #344963;border-radius:10px}.feedback-head{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}.solution-detail{margin-top:10px;padding-top:10px;border-top:1px solid #344963;line-height:1.8}.celebration-overlay{position:relative;overflow:hidden;padding:24px}.celebration-card{position:relative;z-index:2;max-width:650px;margin:auto;padding:28px;border-radius:22px;background:linear-gradient(145deg,#152844,#2a194b);text-align:center}.celebration-card h2{color:#ffe28a;font-size:clamp(28px,5vw,44px)}.celebration-card h3{color:#8ceaff}.celebration-art{font-size:48px;animation:mw-pop .7s infinite alternate}.final-score{font-size:44px;font-weight:900}.confetti{position:absolute;inset:0;overflow:hidden;pointer-events:none}.confetti i{position:absolute;top:-15px;width:8px;height:14px;animation:mw-fall 3s linear forwards}@keyframes mw-fall{to{top:105%;transform:rotate(800deg)}}@keyframes mw-pop{to{transform:scale(1.06) rotate(2deg)}}`; document.head.appendChild(extraStyle);
  function readRecord() { try { return JSON.parse(localStorage.getItem(recordKey) || '{}'); } catch { return {}; } }
  function saveRecord(finished = false) { const old = readRecord(); const next = { ...old, bestProgress: Math.max(old.bestProgress || 0, state.progress), liveProgress: state.progress, livePoints: state.points, correct: state.correct, wrong: state.wrong, answered: state.answered, lastPlayed: new Date().toISOString() }; if (finished) { next.plays = (old.plays || 0) + 1; next.lastProgress = state.progress; } try { localStorage.setItem(recordKey, JSON.stringify(next)); } catch {} $('record').textContent = `🏅 Kỷ lục đã lưu: ${next.bestProgress || 0}/100 • Đã chơi ${next.plays || 0} lần`; }
  function safe(v) { return String(v ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }
  function isGeometry() { return /^(hinh|geometry|toa_do|vector|goc|duong_tron|mat_phang|khong_gian|he_thuc_luong|tuong_giao|mat_cau|the_tich)/i.test(topic); }
  function normalize(q) { const options = q.options || q.choices || []; return { ...q, text: q.question || q.text || 'Câu hỏi', question_type: q.question_type || (options.length ? 'multiple_choice' : 'short_answer'), options: options.map(o => typeof o === 'object' && o ? (o.value ?? o.label ?? String(o)) : o), statements: Array.isArray(q.statements) ? q.statements : [], statement_answers: Array.isArray(q.statement_answers) ? q.statement_answers : [], solution: q.solution || q.explanation || '', diagram: q.diagram || null }; }
  async function fetchBatch() {
    const found = [];
    if (isGeometry()) {
      try { const r = await fetch(`${API}/api/ai/practice/session`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({grade,topics:[topic],count:3,problem_parts:4,difficulty:['easy','medium','hard'][state.batch%3],question_type:'multiple_choice',problem_mode:true,history:state.history.slice(-30),game_id:`universal_${mode}_${topic}`}) }); if (!r.ok) throw new Error(); const d = await r.json(); found.push(...(d.questions || []).map(normalize)); } catch {}
    } else {
      const types = ['multiple_choice','short_answer','true_false'];
      for (let i=0;i<types.length;i++) {
        const history = [...state.history.slice(-24), ...found.slice(-12).map(q=>({fingerprint:q.fingerprint,structure_fingerprint:q.structure_fingerprint,template_family:q.template_family,variation_key:q.variation_key,archetype:q.archetype}))].slice(-30);
        try { const r = await fetch(`${API}/api/ai/practice/session`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({grade,topics:[topic],count:4,difficulty:['easy','medium','hard'][(state.batch+i)%3],question_type:types[(state.batch+i)%3],history,game_id:`universal_${mode}_${topic}`}) }); if (!r.ok) throw new Error(); const d = await r.json(); found.push(...(d.questions || []).map(normalize)); } catch {}
      }
    }
    state.batch++;
    for (let i=found.length-1;i>0;i--) { const j=Math.floor(Math.random()*(i+1)); [found[i],found[j]]=[found[j],found[i]]; }
    return found;
  }
  function drawDiagram(q) {
    const d = q.diagram; diagram.hidden = !(d || isGeometry()); if (diagram.hidden) { diagram.innerHTML=''; return; }
    let svg = '';
    const line=(a,b,c,d,stroke='#58d9f7')=>`<line x1="${a}" y1="${b}" x2="${c}" y2="${d}" stroke="${stroke}" stroke-width="2" stroke-linecap="round"/>`;
    const label=(x,y,t)=>`<text x="${x}" y="${y}" fill="#dcecff" font-size="14" font-weight="700">${safe(t)}</text>`;
    if(d?.points && typeof d.points==='object' && !Array.isArray(d.points)) { const entries=Object.entries(d.points).filter(([,v])=>Array.isArray(v)&&v.length>=2); if(entries.length>=3){const xs=entries.map(([,v])=>+v[0]||0),ys=entries.map(([,v])=>+v[1]||0),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),sx=v=>40+(v-minX)/Math.max(1,maxX-minX)*300,sy=v=>180-(v-minY)/Math.max(1,maxY-minY)*135,pts=Object.fromEntries(entries.map(([k,v])=>[k,[sx(+v[0]||0),sy(+v[1]||0)]]));svg=(d.segments||[]).map(s=>pts[s[0]]&&pts[s[1]]?line(...pts[s[0]],...pts[s[1]]):'').join('')+entries.map(([k])=>label(pts[k][0]+6,pts[k][1]-6,k)).join('');} }
    if(!svg && (d?.type==='circle'||d?.shape==='circle')) svg=`<circle cx="190" cy="95" r="58" fill="rgba(88,217,247,.06)" stroke="#58d9f7" stroke-width="2"/>${line(190,95,248,95)}${label(177,88,'O')}${label(215,87,'r')}`;
    if(!svg) svg=`${line(55,165,330,165)}${line(55,165,55,35)}${line(55,35,330,165)}${label(38,180,'A')}${label(334,180,'B')}${label(40,28,'C')}`;
    diagram.innerHTML=`<b>📐 Hình minh họa</b><svg viewBox="0 0 390 210" role="img" aria-label="Hình học minh họa">${svg}</svg><small>${safe(d?.caption || 'Hình minh họa hỗ trợ quan sát. Dùng số liệu trong đề làm căn cứ tính toán.')}</small>`;
  }
  function render() {
    clearInterval(state.timer);
    if (state.progress >= 100) return finish();
    if (state.index >= state.questions.length) { $('question').textContent='Đang chuẩn bị câu hỏi mới…'; fetchBatch().then(qs=>{state.questions.push(...qs); if(!qs.length) return finish(); render();}); return; }
    const q=state.questions[state.index]; state.locked=false; state.pendingNext=false; state.seconds=config.seconds;
    $('questionNo').textContent=`Câu ${state.answered+1}`; $('difficulty').textContent=`Tiến độ ${state.progress}/100`; $('hp').textContent=state.progress; $('combo').textContent=state.correct; $('score').textContent=state.points; $('timer').textContent=state.seconds; $('progressBar').style.width=`${state.progress}%`; $('question').textContent=q.text;
    context.hidden=!(q.problem_context||q.context); context.textContent=q.problem_context||q.context||''; drawDiagram(q); $('feedback').textContent=''; $('feedback').className='feedback'; $('next').hidden=true; const box=$('options'); box.replaceChildren();
    if(q.question_type==='true_false' && q.statements.length){ const wrap=document.createElement('div'); wrap.className='statement-list'; q.statements.forEach(st=>{const row=document.createElement('label');row.className='statement-row';const cb=document.createElement('input');cb.type='checkbox';const tx=document.createElement('span');tx.textContent=st;row.append(cb,tx);wrap.append(row)});const send=document.createElement('button');send.className='option';send.textContent='Kiểm tra các nhận định';send.onclick=()=>answer([...wrap.querySelectorAll('input')].map(x=>x.checked),q,null);box.append(wrap,send); }
    else if(q.question_type==='short_answer'||!q.options.length){const wrap=document.createElement('div');wrap.className='short-answer-wrap';const input=document.createElement('input');input.className='short-answer-input';input.placeholder='Nhập đáp án…';const send=document.createElement('button');send.className='option';send.textContent='Kiểm tra đáp án';send.onclick=()=>answer(input.value,q,null);input.addEventListener('keydown',e=>{if(e.key==='Enter')send.click()});wrap.append(input,send);box.append(wrap)}
    else q.options.forEach((v,i)=>{const b=document.createElement('button');b.className='option';b.textContent=`${String.fromCharCode(65+i)}. ${v}`;b.onclick=()=>answer(v,q,b);box.append(b)});
    state.timer=setInterval(()=>{state.seconds--; $('timer').textContent=state.seconds; if(state.seconds<=0){clearInterval(state.timer);answer('',q,null,true)}},1000); saveRecord();
  }
  function localCompare(a,b){if(Array.isArray(a)&&Array.isArray(b))return JSON.stringify(a)===JSON.stringify(b);return String(a??'').trim().toLowerCase().replace(/\s+/g,'')===String(b??'').trim().toLowerCase().replace(/\s+/g,'')}
  async function answer(value,q,button,timeout=false){if(state.locked||state.progress>=100)return;state.locked=true;clearInterval(state.timer);$('options').querySelectorAll('button,input').forEach(x=>x.disabled=true);let result=null,correct=false;try{if(q.id){const r=await fetch(`${API}/api/ai/questions/${encodeURIComponent(q.id)}/answer`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer:value})});if(r.ok){result=await r.json();correct=!!result.correct}else correct=q.question_type==='true_false'?localCompare(value,q.statement_answers):localCompare(value,q.answer)}else correct=q.question_type==='true_false'?localCompare(value,q.statement_answers):localCompare(value,q.answer)}catch{correct=q.question_type==='true_false'?localCompare(value,q.statement_answers):localCompare(value,q.answer)}
    if(button)button.classList.add(correct?'correct':'wrong');state.answered++;if(correct){state.correct++;state.progress=Math.min(100,state.progress+5);state.points+=5}else{state.wrong++;state.progress=Math.max(0,state.progress-1);state.points=Math.max(0,state.points-1)}
    const answerText=q.question_type==='true_false'?q.statement_answers.map((v,i)=>`${String.fromCharCode(65+i)}: ${v?'Đúng':'Sai'}`).join(' • '):(result?.correct_answer??q.answer);const solution=result?.solution||result?.explanation||q.solution||q.hint||'Xác định dữ kiện, chọn quy tắc phù hợp, tính từng bước rồi thay kết quả vào điều kiện ban đầu để kiểm tra.';const msg=correct?'🎉 Chính xác! Làm tốt lắm!':'💡 Chưa đúng lần này. Hãy đọc lời giải rồi thử tiếp nhé!';$('feedback').className=`feedback ${correct?'good':'bad'}`;$('feedback').innerHTML=`<div class="feedback-head"><b>${msg}${timeout?' Hết giờ.':''}</b><span>${correct?'+5 điểm':'−1 điểm'}</span></div><div class="solution-detail"><p><b>Đáp án đúng:</b> ${safe(answerText)}</p><b>📚 Lời giải chi tiết</b><div>${safe(solution).replace(/\n/g,'<br>')}</div><p>${correct?'Đọc lời giải để ghi nhớ cách làm.':'So sánh bài làm của bạn với từng bước để tìm chỗ khác nhau.'}</p></div>`;
    $('hp').textContent=state.progress;$('combo').textContent=state.correct;$('score').textContent=state.points;$('difficulty').textContent=`Tiến độ ${state.progress}/100`;$('progressBar').style.width=`${state.progress}%`;state.history.push({fingerprint:q.fingerprint,structure_fingerprint:q.structure_fingerprint,template_family:q.template_family,variation_key:q.variation_key,archetype:q.archetype});state.history=state.history.slice(-40);saveRecord();$('next').hidden=false;$('next').textContent=state.progress>=100?'🎉 Xem màn chúc mừng':'📘 Đọc xong, câu tiếp theo';state.pendingNext=true;if(state.progress>=100)setTimeout(finish,650);
  }
  $('next').onclick=()=>{if(!state.pendingNext)return;if(state.progress>=100)return finish();state.index++;state.pendingNext=false;render()};
  function finish(){if(state.finished)return;state.finished=true;clearInterval(state.timer);saveRecord(true);$('arena').hidden=true;$('result').hidden=false;$('result').innerHTML=`<div class="celebration-overlay"><div class="confetti"></div><div class="celebration-card"><div class="celebration-art">🎊 🥳 🎉</div><div class="eyebrow">MATH WEB • CHALLENGE COMPLETE</div><h2>CONGRATULATIONS!</h2><h3>WELL DONE, YOU'RE THE BEST!</h3><p>Bạn đã hoàn thành tiến độ 100%. Thành tích đã được lưu trên thiết bị này.</p><div class="final-score">100/100</div><p>Đúng: ${state.correct} • Sai: ${state.wrong} • Điểm: ${state.points}</p><button onclick="location.reload()">🔄 Chơi lại</button><button onclick="location.href='../../practise.html'">← Về luyện tập</button></div></div>`;const host=$('result').querySelector('.confetti'),colors=['#38d9ff','#a970ff','#4ade80','#ffd166','#fb7185','#fff'];for(let i=0;i<90;i++){const b=document.createElement('i');b.style.left=Math.random()*100+'%';b.style.animationDelay=Math.random()*2+'s';b.style.background=colors[i%colors.length];host.append(b)}}
  async function start(){try{state.questions=await fetchBatch()}catch{}if(!state.questions.length){$('question').textContent='Không tải được câu hỏi. Hãy kiểm tra backend ở cổng 8000.';$('feedback').textContent='Nếu backend chưa chạy, hãy khởi động bằng START_BACKEND.bat.';return}render()}
  window.addEventListener('beforeunload',()=>saveRecord()); start();
})();
