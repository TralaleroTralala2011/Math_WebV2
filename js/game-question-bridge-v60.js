/* MATH_WEB V78: topic-wide, three-game, fail-closed anti-repeat gate.
   One run is shared by account + grade + topic across all three game pages.
   Numerical substitutions, exact text and reviewed Word form IDs do not
   constitute different exercises. The server also claims the structure. */
(function(){
  'use strict';
  const STORAGE_PREFIX = 'mathweb-topic-run-v78::';
  const RUN_TTL = 24 * 60 * 60 * 1000;
  const MAX_HISTORY = 500;
  const STRIP = /[\u0300-\u036f]/g;
  const STOP = new Set('cho hay tim tinh la cua trong voi mot cac va so duoc bao nhieu nao tu sau sau day ket qua gia tri biet rang neu thuoc xac dinh dung sai bai toan cau hoi lua chon phuong an'.split(' '));
  const clean = value => String(value ?? '').normalize('NFKC').toLowerCase()
    .normalize('NFD').replace(STRIP, '').replace(/đ/g, 'd')
    .replace(/[−–]/g, '-').replace(/×/g,'*').replace(/÷/g, '/')
    .replace(/\s+/g, ' ').trim()
    .replace(/^(?:cau\s*(?:hoi\s*)?(?:so\s*)?\d+\s*[:.\-)]\s*|kiem\s*tra\s*kien\s*thuc\s*[:：]\s*|sau\s*khi\s*phan\s*tich\s*du\s*kien\s*[,：]\s*)/i,'');
  const textOf = q => q && (q.question || q.text) || '';
  const shape = value => clean(value)
    .replace(/(?<![a-z])[-+]?\d+(?:[.,]\d+)?(?:\s*\/\s*\d+)?(?:[eE][-+]?\d+)?/g,' # ')
    .replace(/[^a-z#\^+*\/<>=!-]+/g, ' ').replace(/\s+/g, ' ').trim();
  const family = q => {
    const form = String(q.form_id || '').trim().toLowerCase();
    if (form && !['none','null','unknown'].includes(form)) return 'form:'+form;
    const template = String(q.template_family || '').trim().toLowerCase();
    return template && !/^(?:v254_|admin_bank_)\d+$/.test(template) ? 'family:'+template : '';
  };
  const tokens = value => {
    const out = new Map();
    for (const t of shape(value).match(/[a-z]+/g) || []) {
      if(t.length <= 1 || STOP.has(t)) continue;
      out.set(t, (out.get(t)||0)+1);
    }
    return out;
  };
  function sameMethod(a,b) {
    if(!textOf(a) || !textOf(b)) return false;
    if(clean(textOf(a)) === clean(textOf(b)) || shape(textOf(a)) === shape(textOf(b))) return true;
    if(family(a) && family(a) === family(b)) return true;
    const aa=tokens(textOf(a)),bb=tokens(textOf(b));
    let union=0, intersection=0;
    for(const t of new Set([...aa.keys(),...bb.keys()])) {
      const aCount=aa.get(t)||0,bCount=bb.get(t)||0;
      union+=Math.max(aCount,bCount);
      intersection+=Math.min(aCount,bCount);
    }
    return union>=7 && intersection>=5 && intersection/union>=0.80;
  }
  function currentUser(){
    try {
      const user = JSON.parse(localStorage.getItem('mathweb_user') || '{}');
      return String(user.id || user.player_id || user.username || 'guest');
    } catch(_){return 'guest'}
  }
  function storageKey(grade,topic){return STORAGE_PREFIX+encodeURIComponent(currentUser())+'::'+String(grade)+'::'+encodeURIComponent(topic)}
  function uniqueId(){
    return 'mw'+(typeof crypto!=='undefined'&&crypto.randomUUID ? crypto.randomUUID().replace(/-/g,'') : Date.now().toString(36)+Math.random().toString(36).slice(2));
  }
  function startRun(){return {id:uniqueId(),updated:Date.now(),history:[],games:[]}}
  function openTopicRun(grade,topic) {
    const key=storageKey(grade,topic);
    let cached=null;
    try{ cached=JSON.parse(localStorage.getItem(key)||'null'); }
    catch(_){ cached=null; }
    const valid = cached && /^[a-zA-Z0-9:_-]{3,100}$/.test(String(cached.id||''))
      && Array.isArray(cached.history) && cached.history.length<=MAX_HISTORY
      && Number.isFinite(cached.updated) && Date.now()-cached.updated<RUN_TTL && cached.updated<=Date.now()+60000;
    const initial=valid?cached:startRun();
    try{localStorage.setItem(key,JSON.stringify(initial));}
    catch(_){throw new Error('Không thể lưu lịch sử lượt chơi; đã chặn phát câu hỏi để tránh trùng.')}
    const read=()=>{
      const fresh=JSON.parse(localStorage.getItem(key)||'null');
      if(!fresh || fresh.id!==initial.id || !Array.isArray(fresh.history)) throw new Error('Lượt chơi đã đổi ở tab khác, hãy tải lại trang.');
      return fresh;
    };
    const history=()=>read().history;
    const claim=q=>{
      const entry={question:String(textOf(q)).slice(0,2300),form_id:q.form_id||'',
        fingerprint:q.fingerprint||'',structure_fingerprint:q.structure_fingerprint||'',
        template_family:q.template_family||'',variation_key:q.variation_key||'',
        archetype:q.archetype||''};
      if(!entry.question.trim())return false;
      // Read on each claim so navigation or another tab cannot bypass ledger.
      const data=read();
      if(data.history.some(old=>sameMethod(entry,old)))return false;
      if(data.history.length>=MAX_HISTORY)throw new Error('Đã đạt giới hạn dạng trong lượt; bắt đầu lượt mới để tiếp tục.');
      data.history.push(entry);data.updated=Date.now();
      localStorage.setItem(key,JSON.stringify(data));
      // Verify the save; fail closed if browser storage silently discarded it.
      if(!read().history.some(h=>h.question===entry.question))throw new Error('Không xác nhận được lưu câu hỏi đã dùng.');
      return true;
    };
    return {id:initial.id,history,claim,count:()=>history().length,reset:()=>{
      const next=startRun();localStorage.setItem(key,JSON.stringify(next));return next.id;
    }};
  }
  function addRunStatus(game,run){
    if(!document || !document.querySelector) return;
    let host=document.getElementById('mw-topic-run-info');
    if(!host){
      host=document.createElement('div');host.id='mw-topic-run-info';
      host.setAttribute('role','status');
      host.style.cssText='margin:8px 0 12px;padding:9px 12px;border:1px solid #2563eb55;border-radius:12px;background:#0b2039;color:#e7f3ff;font-size:12px;line-height:1.5;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px';
      const label=document.createElement('span');label.id='mw-topic-run-count';host.append(label);
      const reset=document.createElement('button');reset.type='button';reset.textContent='↻ Lượt mới';
      reset.style.cssText='border:1px solid #93c5fd;border-radius:9px;background:#1d4ed8;color:white;padding:6px 10px;cursor:pointer;font:inherit';
      reset.addEventListener('click',()=>{
        if(typeof window.confirm==='function' && !window.confirm('Bắt đầu lượt mới cho chủ đề này? Lịch sử chống trùng của lượt hiện tại sẽ được đặt lại.'))return;
        run.reset();location.reload();
      });
      host.append(reset);
      const target=document.querySelector('.meta')||document.querySelector('.question-meta')||document.querySelector('.arena');
      if(target && target.parentNode)target.parentNode.insertBefore(host,target);
    }
    const info=document.getElementById('mw-topic-run-count');
    if(info)info.textContent=`🧩 Chủ đề ${game.knowledgeId || game.topicId}: ${run.count()} dạng đã dành riêng cho lượt này, không lặp giữa 3 trò chơi.`;
  }
  const plain=value=>clean(value).replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
  function relevant(topic, question){
    if(topic!=='g10_geom_quadrilaterals_properties')return true;
    const t=plain(textOf(question));
    return /\b(hinh binh hanh|hinh thoi)\b/.test(t)
      || (/\btu giac\b/.test(t)&&/\b(duong cheo|canh doi|goc doi|hai cap canh|trung diem|song song|bang nhau)\b/.test(t));
  }
  async function getBatch(opts){
    const {api,game,stage,state,normalizeQuestion,topicQuestionValid}=opts;
    const topic=String(game && game.topicId || '');
    if(!topic)throw new Error('Chủ đề chưa có mã ngân hàng câu hỏi.');
    const run=openTopicRun(Number(game.grade||10),topic);
    state.mwQuestionKeys=state.mwQuestionKeys||new Set();
    const level=stage===1?'easy':stage===2?'medium':'hard';
    const types=stage===1?['multiple_choice','mixed','short_answer']:
      stage===2?['short_answer','mixed','multiple_choice']:
      ['mixed','multiple_choice','short_answer'];
    const attempts=[
      {difficulty:level,question_type:types[0],count:8},
      {difficulty:'medium',question_type:types[1],count:8},
      {difficulty:'easy',question_type:types[2],count:5},
      {difficulty:'hard',question_type:'mixed',count:4},
    ];
    const collected=[];
    const gameId=`${game.knowledgeId||game.engine||topic}_${game.title||'game'}_stage${stage}`;
    let lastError='';
    addRunStatus(game,run);
    for(const config of attempts){
      if(collected.length>=8)break;
      try{
        const response=await fetch(`${api}/api/ai/practice/session`,{
          method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({grade:Number(game.grade||10),topics:[topic],
            count:Math.min(config.count,8-collected.length),
            difficulty:config.difficulty,question_type:config.question_type,
            problem_mode:false,history:run.history(),game_id:gameId,run_id:run.id})
        });
        if(!response.ok){lastError=`HTTP ${response.status}: ${(await response.text()).slice(0,150)}`;continue;}
        const data=await response.json();
        for(const raw of (Array.isArray(data.questions)?data.questions:[])){
          const q=normalizeQuestion(raw);
          if(!topicQuestionValid(q)||!relevant(topic,q))continue;
          if(!run.claim(q))continue;
          state.mwQuestionKeys.add(clean(textOf(q)));
          collected.push(q);
          addRunStatus(game,run);
        }
      }catch(error){lastError=String(error?.message||error);}
    }
    state.batch=(state.batch||0)+1;
    window.MathWebGameQuestions.lastError=lastError;
    if(!collected.length)console.warn('[MATH_WEB] Không còn dạng mới độc lập trong lượt chơi hoặc backend lỗi', {topic,grade:game.grade,stage,lastError});
    return collected;
  }
  window.MathWebGameQuestions={
    requestBatch:getBatch,
    questionKey:q=>clean(textOf(q)),
    openTopicRun, sameMethod,
    resetTopicRun:game=>openTopicRun(Number(game.grade||10),String(game.topicId||'')).reset(),
    lastError:''
  };
})();

(function(){
  'use strict';
  // Optional authenticated activity sync; the server marks these as UNVERIFIED.
  // Events are never used to calculate XP or alter authoritative test results.
  const activityStorageKey = 'mw-activity-queue-v74';
  const eventTypes = new Set(['question_answered','question_skipped','game_completed']);
  function currentOwner(){
    try { const u=JSON.parse(localStorage.getItem('mathweb_user')||'{}'); return String(u.id||u.player_id||''); }
    catch(_){return '';}
  }
  function queueRead(){
    try{const rows=JSON.parse(localStorage.getItem(activityStorageKey)||'[]');return Array.isArray(rows)?rows.slice(-100):[];}
    catch(_){return [];}
  }
  function queueWrite(rows){try{localStorage.setItem(activityStorageKey,JSON.stringify(rows.slice(-100)));}catch(_){}}
  let flushing=false;
  async function flushActivity(){
    if(flushing) return;
    const token=(()=>{try{return localStorage.getItem('mathweb_token')||'';}catch(_){return '';}})();
    const owner=currentOwner();
    if(!token||!owner)return;
    flushing=true;
    try{
      let pending=queueRead();
      for(let i=0;i<100 && pending.length;i++){
        const itemIndex=pending.findIndex(item=>item.owner===owner);
        if(itemIndex<0) break; // Preserve events belonging to a different account.
        const item=pending[itemIndex];
        let res;
        try{
          res=await fetch((window.MATHWEB_API_URL||'').replace(/\/$/,'')+'/api/activity/events', {
            method:'POST',headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},
            body:JSON.stringify(item.event),keepalive:true,
          });
        }catch(_){break;}
        if(!res.ok) break;
        pending.splice(itemIndex,1);queueWrite(pending);
      }
    }finally{flushing=false;}
  }
  function recordActivity(type,question,selected,correct,game,progress){
    if(!eventTypes.has(type))return;
    const owner=currentOwner();
    let token='';try{token=localStorage.getItem('mathweb_token')||'';}catch(_){}
    if(!owner||!token)return;
    const g=game||{};
    const event={
      event_id:(typeof crypto!=='undefined' && crypto.randomUUID ? crypto.randomUUID() : 'ev'+Date.now()+Math.random().toString(36).slice(2)),
      event_type:type,
      game_id:String(g.title||g.engine||'').slice(0,120),
      topic:String(g.topicId||g.knowledgeId||g.topic||'').slice(0,160),
      question_text:String(question&&(question.text||question.question)||'').slice(0,3000),
      selected_answer:String(selected??'').slice(0,1000),
      is_correct:correct===null||correct===undefined?null:Boolean(correct),
      progress:Number.isFinite(Number(progress))?Math.max(0,Math.min(100,Math.round(Number(progress)))):null,
    };
    const pending=queueRead();pending.push({owner,event});queueWrite(pending);void flushActivity();
  }
  window.MathWebActivity={recordActivity,flushActivity};
  window.addEventListener('online',()=>void flushActivity());
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>void flushActivity(),{once:true});
  else void flushActivity();

})();
