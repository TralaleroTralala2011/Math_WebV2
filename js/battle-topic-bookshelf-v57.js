/* V57 Battle THPT full-feature book picker. Backend selects and validates shared questions. */
(function(){'use strict';
  let root=null,frame=null,activeId=null,matchData=null,poll=null,submitting=false;
  let catalog=null,onPlaying=null,readyToInit=false;
  const API=()=>String(window.MATHWEB_API_BASE||window.MATHWEB_API_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
  const auth=()=>({Authorization:'Bearer '+(localStorage.getItem('mathweb_token')||''),Accept:'application/json'});
  const esc=v=>String(v||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  async function readJson(response){
    const data=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(data.detail||data.message||`HTTP ${response.status}`);
    return data;
  }
  function ensure(){
    if(root)return;
    root=document.createElement('div');root.id='mwBattleShelf';root.hidden=true;
    root.setAttribute('role','dialog');root.setAttribute('aria-modal','true');root.setAttribute('aria-label','Tủ sách Toán THPT chọn chủ đề Battle');
    root.innerHTML=`<div class="mw-bs-frame-wrap"><iframe title="Tủ sách Toán THPT · Chọn chủ đề thi đấu" id="mwBsFrame" src="battle-topic-library.html?v=57"></iframe></div>
    <section class="mw-bs-wait" hidden role="status" aria-live="polite"><div class="mw-bs-wait-card"><div class="mw-bs-moon">☾</div><h2>Đã chọn chủ đề</h2><p id="mwBsWaitText">Đang chờ người chơi còn lại xác nhận…</p><div class="mw-bs-spinner" aria-hidden="true"></div><small>Đồng hồ thi đấu chỉ bắt đầu khi cả hai đã xác nhận. Cả hai nhận cùng một bộ đề.</small></div></section>
    <p class="mw-bs-error" hidden role="alert"></p>`;
    document.body.appendChild(root);
    frame=root.querySelector('#mwBsFrame');
    frame.addEventListener('load',()=>{readyToInit=true;postCatalog()});
    window.addEventListener('message',onMessage);
  }
  function error(message){
    if(!root)return;
    const e=root.querySelector('.mw-bs-error');e.textContent=message;e.hidden=false;
  }
  function displayWaiting(message){
    if(!root)return;
    const wait=root.querySelector('.mw-bs-wait');wait.hidden=false;
    root.querySelector('.mw-bs-frame-wrap').hidden=true;
    root.querySelector('#mwBsWaitText').textContent=message||'Đang chờ người chơi còn lại xác nhận…';
  }
  function postCatalog(){
    if(!frame || !readyToInit || !catalog)return;
    frame.contentWindow?.postMessage({type:'mathweb:battle-catalog-init',grade:Number(matchData.grade),topics:catalog},location.origin);
  }
  function onMessage(event){
    if(!root || root.hidden || event.origin!==location.origin || event.source!==frame?.contentWindow)return;
    const data=event.data;
    if(!data||typeof data!=='object')return;
    if(data.type==='mathweb:battle-library-ready'){
      readyToInit=true;postCatalog();return;
    }
    if(data.type==='mathbook:selected'){
      const books=Array.isArray(data.payload?.books)?data.payload.books:[];
      const ids=books.map(b=>b.topicId);
      if(ids.length<1||ids.length>3||new Set(ids).size!==ids.length||ids.some(id=>!catalog?.some(t=>t.id===id))){
        error('Lựa chọn không hợp lệ. Hãy tải lại trang Battle để thử lại.');return;
      }
      submit(ids);
    }
  }
  async function getMatch(){
    return readJson(await fetch(`${API()}/api/matchmaking/match/${encodeURIComponent(activeId)}`,{headers:auth(),cache:'no-store'}));
  }
  async function beginPlaying(id){
    const cb=onPlaying;close();
    if(typeof cb==='function')cb(id);
    else document.dispatchEvent(new CustomEvent('mathweb:battle-topics-ready',{detail:{matchId:id}}));
  }
  async function submit(ids){
    if(submitting||!activeId||matchData?.topic_selection?.my_ready)return;
    submitting=true;
    displayWaiting('Đang lưu lựa chọn và kiểm tra trận đấu…');
    try{
      const data=await readJson(await fetch(`${API()}/api/matchmaking/match/${encodeURIComponent(activeId)}/topics`,{
        method:'POST',headers:{...auth(),'Content-Type':'application/json'},body:JSON.stringify({topics:ids})
      }));
      if(data.status==='PLAYING'){await beginPlaying(activeId);return;}
      matchData.topic_selection={...matchData.topic_selection,my_ready:true,my_choices:ids};
      displayWaiting('Đã chốt '+ids.length+' chủ đề. Đang chờ đối thủ xác nhận…');
    }catch(e){error('Không thể lưu lựa chọn: '+e.message+' Vui lòng kiểm tra kết nối và tải lại trang Battle.');}
    finally{submitting=false;}
  }
  async function show(match,callback){
    if(!match||!match.id)return;
    ensure();
    const id=String(match.id);
    if(activeId!==id){activeId=id;catalog=null;readyToInit=false;frame.src='battle-topic-library.html?v=57&match='+encodeURIComponent(id);}
    matchData=match;onPlaying=callback;root.hidden=false;
    root.querySelector('.mw-bs-wait').hidden=true;
    root.querySelector('.mw-bs-frame-wrap').hidden=false;
    root.querySelector('.mw-bs-error').hidden=true;
    if(match.topic_selection?.my_ready)displayWaiting('Bạn đã chốt '+(match.topic_selection.my_choices?.length||0)+' chủ đề. Chờ người chơi còn lại…');
    else {
      try{
        const data=await readJson(await fetch(`${API()}/api/matchmaking/topic-catalog?grade=${encodeURIComponent(match.grade)}`,{headers:auth(),cache:'no-store'}));
        if(activeId!==id||root.hidden)return;
        catalog=Array.isArray(data.topics)?data.topics:[];
        if(!catalog.length){error('Chưa có chủ đề hợp lệ từ ngân hàng câu hỏi cho khối này.');return;}
        postCatalog();
      }catch(e){error('Không tải được danh sách chủ đề từ backend: '+e.message);return;}
    }
    if(poll)clearInterval(poll);
    poll=setInterval(async()=>{
      if(root.hidden||!activeId){clearInterval(poll);poll=null;return;}
      try{
        const data=await getMatch();
        matchData=data;
        if(data.status==='PLAYING'){await beginPlaying(data.id);return;}
        if(['CANCELLED','REJECTED','EXPIRED','FINISHED'].includes(data.status)){
          error('Trận đấu đã kết thúc hoặc bị hủy. Hãy trở lại danh sách Battle.');return;
        }
        if(data.topic_selection?.my_ready){displayWaiting('Đã chốt chủ đề. Đang chờ đối thủ hoàn tất…');}
      }catch(_){if(matchData?.topic_selection?.my_ready)displayWaiting('Mất kết nối tạm thời, đang thử lại…');}
    },1800);
  }
  function close(){
    if(root)root.hidden=true;
    if(poll){clearInterval(poll);poll=null;}
  }
  window.MathWebBattleTopicBookshelf={show,close};
})();
