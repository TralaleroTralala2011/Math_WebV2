/* MATH_WEB V60: question-loader shared by 3 learning games per topic.
   Strict per-run question identity across requests and sources; no invented answers. */
(function(){
  'use strict';
  const canon = text => String(text || '').normalize('NFKC').replace(/[−–]/g,'-')
       .replace(/\s*([=+*/;(),?:])\s*/g,'$1').replace(/\s+/g,' ')
       .trim().replace(/[\s.!?]+$/,'').toLocaleLowerCase('vi-VN');
  function key(question){ return canon(question && (question.text || question.question) || ''); }
  // Extra browser-side protection for a verified mislabeled Word topic.
  // The API is the authoritative gate, but deployed frontends may talk to an
  // older Render backend, so never render a known unrelated exercise anyway.
  const plain = value => String(value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'')
       .replace(/đ/g,'d').replace(/Đ/g,'D').toLocaleLowerCase('vi-VN')
       .replace(/[^a-z0-9\s]/g,' ').replace(/\s+/g,' ').trim();
  function relevant(topic, question){
    if(topic!=='g10_geom_quadrilaterals_properties') return true;
    const t=plain(question&& (question.text || question.question));
    return /\b(hinh binh hanh|hinh thoi)\b/.test(t)
        || (/\btu giac\b/.test(t)
         && /\b(duong cheo|canh doi|goc doi|hai cap canh|trung diem|song song|bang nhau)\b/.test(t));
  }
  async function getBatch(opts){
    const {api,game,stage,history=[],state,normalizeQuestion,topicQuestionValid} = opts;
    const topic = String(game && game.topicId || '');
    if(!topic) throw new Error('Chủ đề chưa có mã ngân hàng câu hỏi.');
    state.mwQuestionKeys = state.mwQuestionKeys || new Set();
    const seen = state.mwQuestionKeys;
    const level = stage === 1 ? 'easy' : stage === 2 ? 'medium' : 'hard';
    const types = stage === 1 ? ['multiple_choice','mixed','short_answer']
                : stage === 2 ? ['short_answer','mixed','multiple_choice']
                : ['mixed','multiple_choice','short_answer'];
    const attempts = [
      {difficulty:level, question_type:types[0], count:8},
      {difficulty:'medium', question_type:types[1], count:8},
      {difficulty:'medium', question_type:types[2], count:5},
      {difficulty:'easy', question_type:'mixed', count:3},
    ];
    const collected = [];
    const historyText = [...(history||[]).filter(x=>x&&typeof x==='object')];
    const gameId = `${game.knowledgeId||game.engine||topic}_${game.title||'game'}_stage${stage}`;
    let lastError = '';
    for(const config of attempts){
      if(collected.length>=8) break;
      try{
        const response = await fetch(`${api}/api/ai/practice/session`, {
          method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({grade: Number(game.grade||10), topics:[topic],
            count: Math.min(config.count,8-collected.length),
            difficulty:config.difficulty,question_type:config.question_type,
            problem_mode:false,history:historyText,game_id:gameId})
        });
        if(!response.ok){
          const detail=await response.text();
          lastError=`HTTP ${response.status}: ${detail.slice(0,100)}`;
          continue;
        }
        const data=await response.json();
        for(const raw of (Array.isArray(data.questions)?data.questions:[])){
          const q=normalizeQuestion(raw);
          if(!topicQuestionValid(q) || !relevant(topic,q))continue;
          const k=key(q);
          if(!k || seen.has(k))continue;
          seen.add(k);
          historyText.push({question:q.text, fingerprint:q.fingerprint,
            structure_fingerprint:q.structure_fingerprint,template_family:q.template_family,
            variation_key:q.variation_key,archetype:q.archetype});
          collected.push(q);
        }
      }catch(error){ lastError=String(error&&error.message||error); }
    }
    state.batch=(state.batch||0)+1;
    if(!collected.length){
      console.warn('[MATH_WEB] Không tải được câu hỏi', {topic,grade:game.grade,stage,error:lastError});
    }
    return collected;
  }

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

  window.MathWebGameQuestions={requestBatch:getBatch,questionKey:key};
})();
