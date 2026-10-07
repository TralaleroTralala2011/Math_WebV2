(() => {
  const API = location.origin.startsWith('http') && location.port === '5500' ? 'http://127.0.0.1:8000' : 'http://127.0.0.1:8000';
  const p = new URLSearchParams(location.search);
  const topic = p.get('topic') || 'menh_de';
  const grade = Number(p.get('grade') || 10);
  const difficulty = p.get('difficulty') || 'medium';
  const mode = p.get('mode') || 'blitz';
  const name = p.get('name') || 'Thử thách Toán';
  const config = {
    blitz: {label:'⚡ Đấu tốc độ', count:10, seconds:20, hp:100, damage:0},
    boss: {label:'👹 Đấu Boss', count:8, seconds:25, hp:100, damage:18},
    puzzle: {label:'🧩 Giải mật mã', count:6, seconds:35, hp:100, damage:25}
  }[mode] || {label:'⚡ Đấu tốc độ',count:10,seconds:20,hp:100,damage:0};
  let questions=[], index=0, score=0, combo=0, hp=config.hp, timerId=null, locked=false, seconds=config.seconds;
  const $=id=>document.getElementById(id);
  $('title').textContent=`${config.label} • ${name}`;
  $('subtitle').textContent=`Toán ${grade} • ${difficulty==='easy'?'Nền tảng':difficulty==='hard'?'Nâng cao':'Trung cấp'}`;
  $('hp').textContent=hp;

  async function load(){
    try{
      const r=await fetch(`${API}/api/ai/questions`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({grade,topics:[topic],count:config.count,difficulty,question_type:'multiple_choice',game_id:`universal_${mode}_${topic}`})});
      const data=await r.json();
      if(!r.ok || !data.questions?.length) throw new Error(data.detail||'Không tạo được câu hỏi');
      questions=data.questions; render();
    }catch(e){$('question').textContent='Không tải được câu hỏi.';$('feedback').textContent=e.message+' Hãy kiểm tra backend đang chạy ở cổng 8000.';}
  }
  function render(){
    if(index>=questions.length){finish();return;}
    locked=false; clearInterval(timerId); seconds=config.seconds;
    const q=questions[index]; $('questionNo').textContent=`Câu ${index+1}/${questions.length}`; $('difficulty').textContent=difficulty==='easy'?'🔰 NỀN TẢNG':difficulty==='hard'?'🟣 NÂNG CAO':'🔵 TRUNG CẤP';
    $('question').textContent=q.question; $('feedback').textContent=''; $('feedback').className='feedback'; $('next').hidden=true;
    $('progressBar').style.width=`${index/questions.length*100}%`;$('timer').textContent=seconds;$('hp').textContent=hp;$('combo').textContent=combo;$('score').textContent=score;
    const box=$('options');box.replaceChildren();
    (q.options||[]).forEach((opt,i)=>{const b=document.createElement('button');b.className='option';b.textContent=`${String.fromCharCode(65+i)}. ${opt}`;b.onclick=()=>answer(opt,b);box.appendChild(b);});
    timerId=setInterval(()=>{seconds--; $('timer').textContent=seconds;if(seconds<=0){clearInterval(timerId);answer(null,null,true)}},1000);
  }
  async function answer(value,button,timeout=false){
    if(locked)return; locked=true; clearInterval(timerId); [...$('options').children].forEach(b=>b.disabled=true);
    const q=questions[index];
    try{
      const r=await fetch(`${API}/api/ai/questions/${q.id}/answer`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer:value===null?'':value})});
      const data=await r.json();
      if(data.correct){combo++;score+=100+combo*20+(seconds*3);if(button)button.classList.add('correct');$('feedback').textContent=`🎯 Chính xác! +${100+combo*20} điểm`;$('feedback').className='feedback good';}
      else{combo=0;hp=Math.max(0,hp-config.damage-(timeout?5:0));if(button)button.classList.add('wrong');$('feedback').textContent=`💡 ${timeout?'Hết giờ. ':''}Đáp án đúng: ${data.correct_answer}. ${data.solution||''}`;$('feedback').className='feedback bad';}
      $('hp').textContent=hp;$('combo').textContent=combo;$('score').textContent=score;$('next').hidden=false;
      if(hp<=0){$('next').textContent='Xem kết quả →';}
    }catch(e){$('feedback').textContent='Không thể chấm câu này. Hãy kiểm tra backend.';$('feedback').className='feedback bad';$('next').hidden=false;}
  }
  $('next').onclick=()=>{if(hp<=0){finish();return}index++;render();};
  function finish(){clearInterval(timerId);$('arena').hidden=true;$('result').hidden=false;$('resultTitle').textContent=hp>0?'🎉 Hoàn thành!':'💥 Boss đã hạ bạn!';$('resultText').textContent=`Bạn đạt ${score} điểm với ${combo} combo hiện tại. Hãy chơi lại để phá kỷ lục!`;}
  load();
})();
