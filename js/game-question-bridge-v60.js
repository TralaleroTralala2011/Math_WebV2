/* MATH_WEB V60: question-loader shared by 3 learning games per topic.
   Strict per-run question identity across requests and sources; no invented answers. */
(function(){
  'use strict';
  const canon = text => String(text || '').normalize('NFKC').replace(/[−–]/g,'-')
       .replace(/\s*([=+*/;(),?:])\s*/g,'$1').replace(/\s+/g,' ')
       .trim().replace(/[\s.!?]+$/,'').toLocaleLowerCase('vi-VN');
  function key(question){ return canon(question && (question.text || question.question) || ''); }
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
          if(!topicQuestionValid(q))continue;
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
  window.MathWebGameQuestions={requestBatch:getBatch,questionKey:key};
})();
