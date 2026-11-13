/* V48: optional bank-backed exercise panel on Learning and Roadmap.
 * It never touches official placement/roadmap assessment scores or page state.
 */
(() => {
  'use strict';
  const pathname = location.pathname.toLowerCase();
  const learning = pathname.endsWith('/learn.html');
  const roadmap = pathname.endsWith('/learning-path.html');
  if (!learning && !roadmap) return;
  const BASE = String(window.MATHWEB_API_BASE || window.MATHWEB_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
  const make = (tag, className, content) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (content !== undefined) element.textContent = content;
    return element;
  };
  const token = () => { try { return localStorage.getItem('mathweb_token') || ''; } catch (_) { return ''; } };
  const get = async (path, options = {}) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 16000);
    try {
      const response = await fetch(BASE + path, {
        ...options,
        signal: controller.signal,
        headers: { Accept: 'application/json', ...(options.body ? {'Content-Type': 'application/json'} : {}), ...(token() ? { Authorization: 'Bearer ' + token() } : {}) }
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : `HTTP ${response.status}`);
      return payload;
    } finally { clearTimeout(timer); }
  };
  function init() {
    const root = make('section', 'mw-v48-bank-panel');
    root.setAttribute('aria-label', 'Bài tập bổ trợ từ ngân hàng toán');
    const title = make('h2', '', '✍️ Luyện tập bổ trợ theo chủ đề');
    const disclaimer = make('p', 'mw-v48-disclaimer', 'Bài luyện tập tự chọn từ ngân hàng hiện có. Câu V254 là ứng viên chưa được kiểm định độc lập; kết quả không thay thế bài kiểm tra đầu vào hoặc điểm Lộ trình học.');
    const controls = make('div', 'mw-v48-controls');
    const gradeLabel = make('label', '', 'Khối lớp');
    const gradeSelect = make('select');
    gradeSelect.setAttribute('aria-label', 'Khối lớp để lấy bài tập bổ trợ');
    [10, 11, 12].forEach(g => { const opt = make('option','',`Toán ${g}`); opt.value = String(g); gradeSelect.append(opt); });
    const topicLabel = make('label', '', 'Chủ đề');
    const topicSelect = make('select');
    topicSelect.setAttribute('aria-label', 'Chủ đề của bài tập bổ trợ');
    const start = make('button','mw-v48-primary','Tải 5 câu luyện tập');
    start.type = 'button';
    gradeLabel.append(gradeSelect); topicLabel.append(topicSelect); controls.append(gradeLabel,topicLabel,start);
    const status = make('p','mw-v48-status','Chọn chủ đề và tải câu hỏi.');
    status.setAttribute('role','status');
    const area = make('div','mw-v48-question-area');
    root.append(title,disclaimer,controls,status,area);
    const anchor = learning ? document.querySelector('main.wrap .layout') : document.getElementById('matrix-assessment-panel');
    if (!anchor) return;
    anchor.insertAdjacentElement('afterend',root);
    let batch = [], index = 0;
    const setStatus = message => { status.textContent = message; };
    function clear() { area.replaceChildren(); batch = []; index = 0; }
    async function loadTopics() {
      clear(); topicSelect.replaceChildren();
      topicSelect.disabled = true;
      setStatus('Đang tải danh sách chủ đề...');
      try {
        const topics = await get('/api/ai/knowledge?grade=' + gradeSelect.value);
        if (!Array.isArray(topics)) throw new Error('Danh sách chủ đề không hợp lệ.');
        topics.forEach(item => {
          if (!item || !item.id) return;
          const opt = make('option', '', String(item.name || item.title || item.id));
          opt.value = String(item.id);
          topicSelect.append(opt);
        });
        if (learning) {
          const active = document.getElementById('topic')?.value;
          if (active && [...topicSelect.options].some(o => o.value === active)) topicSelect.value = active;
        }
        topicSelect.disabled = !topicSelect.options.length;
        setStatus(topicSelect.disabled ? 'Chưa tìm thấy chủ đề.' : 'Sẵn sàng. Các câu trả lời sẽ được chấm trên backend.');
      } catch (error) {
        setStatus('Không tải được danh sách từ backend: ' + error.message);
      }
    }
    function renderQuestion() {
      area.replaceChildren();
      if (index >= batch.length) {
        setStatus('Đã hoàn thành lượt luyện tập bổ trợ.');
        return;
      }
      const q = batch[index];
      const number = make('p','mw-v48-qcount',`Câu ${index+1}/${batch.length}`);
      const prompt = make('h3','mw-v48-prompt',String(q.question || ''));
      const choices = make('div','mw-v48-options');
      const feedback = make('p','mw-v48-feedback');
      feedback.setAttribute('aria-live','polite');
      const next = make('button','mw-v48-primary','Câu tiếp theo');
      next.type='button';next.hidden=true;
      next.addEventListener('click',()=>{index++;renderQuestion();});
      let locked = false;
      const submit = async value => {
        if (locked) return;
        locked = true;
        const buttons = [...choices.querySelectorAll('button')];
        buttons.forEach(button => {button.disabled = true;});
        feedback.textContent = 'Đang chấm đáp án...';
        try {
          const res = await get('/api/ai/questions/'+encodeURIComponent(q.id)+'/answer',{
            method:'POST',body:JSON.stringify({answer:value})
          });
          feedback.textContent = `${res.correct ? '✓ Chính xác.' : '✗ Chưa đúng.'} Đáp án: ${res.correct_answer ?? ''}. ${res.solution ?? ''}`;
          next.hidden=false;
        } catch (error) {
          feedback.textContent = 'Chưa thể chấm câu này: '+error.message;
          next.hidden=false;
        }
      };
      if (Array.isArray(q.options) && q.options.length >= 2) {
        q.options.forEach(option=>{
          const b=make('button','mw-v48-option',String(option)); b.type='button';
          b.addEventListener('click',()=>submit(option)); choices.append(b);
        });
      } else {
        const input = make('input');input.type='text';input.placeholder='Nhập câu trả lời';input.setAttribute('aria-label','Nhập câu trả lời');
        const b = make('button','mw-v48-primary','Trả lời'); b.type='button';
        b.addEventListener('click',()=>{if(input.value.trim())submit(input.value.trim());});
        choices.append(input,b);
      }
      const source = make('p','mw-v48-source',q.source === 'Question_Bank_V254 (draft; unverified)' ? 'Nguồn: V254 · Ứng viên chưa thẩm định độc lập' : 'Nguồn: ' + String(q.source || 'Ngân hàng câu hỏi hiện có'));
      area.append(number,prompt,source,choices,feedback,next);
    }
    gradeSelect.addEventListener('change',loadTopics);
    start.addEventListener('click',async()=>{
      if (!topicSelect.value) return;
      clear();start.disabled=true;setStatus('Đang chuẩn bị bộ câu hỏi...');
      try {
        const data = await get('/api/ai/practice/session',{
          method:'POST',body:JSON.stringify({grade:Number(gradeSelect.value),topics:[topicSelect.value],count:5,difficulty:'medium',question_type:'multiple_choice'})
        });
        batch = Array.isArray(data.questions) ? data.questions : [];
        if (!batch.length) throw new Error('Chủ đề này chưa có câu hỏi có thể dùng.');
        setStatus('Bộ câu hỏi bổ trợ đã sẵn sàng.');
        renderQuestion();
      } catch (error) {setStatus('Không thể lấy câu hỏi: '+error.message);}
      finally {start.disabled=false;}
    });
    const priorGrade = (learning ? document.getElementById('grade')?.value : null) || new URLSearchParams(location.search).get('grade') || '10';
    gradeSelect.value = ['10','11','12'].includes(priorGrade) ? priorGrade : '10';
    loadTopics();
    if (learning) document.getElementById('grade')?.addEventListener('change',()=>{
      const active = document.getElementById('grade')?.value;
      if (['10','11','12'].includes(active) && gradeSelect.value !== active) { gradeSelect.value = active; loadTopics(); }
    });
    if (learning) document.getElementById('topic')?.addEventListener('change',()=>{
      const chosen = document.getElementById('topic')?.value;
      if ([...topicSelect.options].some(o => o.value === chosen)) topicSelect.value = chosen;
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
