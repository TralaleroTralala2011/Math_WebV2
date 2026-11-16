/* MATH_WEB V76: consent-first, friends-only one-to-one calls.
   WebRTC media is peer-to-peer and never recorded by this feature. */
(() => {
  'use strict';
  const root = document.querySelector('.conversation-header');
  if (!root) return;
  const style = document.createElement('link');
  style.rel = 'stylesheet'; style.href = 'css/chat-calls-v76.css?v=76';
  document.head.appendChild(style);
  const controls = document.createElement('div');
  controls.className = 'mw-call-toolbar';
  controls.innerHTML = `<button type="button" id="mw-open-profile" title="Xem hồ sơ" aria-label="Xem hồ sơ">👤 Hồ sơ</button><button type="button" id="mw-call-audio" title="Gọi thoại" aria-label="Gọi thoại">📞</button><button type="button" id="mw-call-video" title="Gọi video" aria-label="Gọi video">🎥</button>`;
  root.appendChild(controls);
  const overlay = document.createElement('section');
  overlay.className = 'mw-call-overlay'; overlay.hidden = true;
  overlay.setAttribute('role','dialog'); overlay.setAttribute('aria-modal','true');
  overlay.setAttribute('aria-label','Cuộc gọi MATH WEB');
  overlay.innerHTML = `<div class="mw-call-card"><div class="mw-call-heading"><div><strong id="mw-call-title">Cuộc gọi MATH WEB</strong><p id="mw-call-status" role="status">Đang kết nối…</p></div><button id="mw-call-close" type="button" aria-label="Kết thúc cuộc gọi">✕</button></div><div id="mw-call-videos" class="mw-call-videos"><video id="mw-remote-video" autoplay playsinline></video><video id="mw-local-video" autoplay playsinline muted></video></div><audio id="mw-remote-audio" autoplay></audio><div class="mw-call-actions"><button id="mw-call-accept" type="button" hidden>✓ Chấp nhận</button><button id="mw-call-mic" type="button" hidden>🎙️ Tắt mic</button><button id="mw-call-camera" type="button" hidden>📷 Tắt camera</button><button id="mw-call-hangup" type="button">✕ Từ chối / Kết thúc</button></div><small>Chỉ kết nối với bạn bè. Mic và camera được bật sau khi bạn đồng ý.</small></div>`;
  document.body.appendChild(overlay);
  const $ = id => document.getElementById(id);
  const audioBtn = $('mw-call-audio'), videoBtn = $('mw-call-video'), profileBtn = $('mw-open-profile');
  const acceptBtn = $('mw-call-accept'), micBtn = $('mw-call-mic'), cameraBtn = $('mw-call-camera');
  const remoteVideo = $('mw-remote-video'), localVideo = $('mw-local-video'), remoteAudio = $('mw-remote-audio');
  const statusNode = $('mw-call-status'), titleNode = $('mw-call-title'), videoBox = $('mw-call-videos');
  const state = {socket:null, ready:false, callId:null, peerId:null, mode:null, role:null, phase:'idle', pc:null, local:null, remote:null, pendingIce:[], reconnect:null, ringTimer:null, closing:false, generation:0};
  const token = () => (localStorage.getItem('mathweb_token') || '').trim();
  const activeFriend = () => window.MATHWEB_CHAT?.getSelectedFriend?.() || null;
  const userId = friend => Number(friend?.id || 0);
  const escapeText = s => String(s ?? '').slice(0,120);
  function setStatus(s){ statusNode.textContent = s; }
  function callUi(mode){ overlay.hidden = false; videoBox.hidden = mode !== 'video'; $('mw-call-accept').hidden = true; micBtn.hidden = true; cameraBtn.hidden = true; titleNode.textContent = mode === 'video' ? '🎥 Cuộc gọi video' : '📞 Cuộc gọi thoại'; }
  function safeSend(payload){
    const ws = state.socket;
    if (!ws || ws.readyState !== WebSocket.OPEN || !state.ready) return false;
    try {ws.send(JSON.stringify(payload));return true;} catch (_) {return false;}
  }
  function cleanup(){
    state.generation++;
    if(state.ringTimer){clearTimeout(state.ringTimer);state.ringTimer=null;}
    if(state.pc){try{state.pc.ontrack=null;state.pc.onicecandidate=null;state.pc.close();}catch(_){} state.pc=null;}
    if(state.local){state.local.getTracks().forEach(t=>t.stop());state.local=null;}
    state.remote=null;state.pendingIce=[];
    localVideo.srcObject=null;remoteVideo.srcObject=null;remoteAudio.srcObject=null;
    state.callId=null;state.peerId=null;state.mode=null;state.role=null;state.phase='idle';
    overlay.hidden=true;acceptBtn.hidden=true;micBtn.hidden=true;cameraBtn.hidden=true;
  }
  function endCall(reason='end'){
    if(state.phase !== 'idle'){
      const type = state.phase==='incoming' ? 'call-reject' : 'call-end';
      if(state.callId) safeSend({type,call_id:state.callId});
      else if(state.role==='caller') safeSend({type:'call-cancel'});
    }
    cleanup();
  }
  async function startMedia(){
    const generation=state.generation;
    if(!navigator.mediaDevices?.getUserMedia || !window.RTCPeerConnection) throw Error('Trình duyệt không hỗ trợ cuộc gọi WebRTC.');
    const stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true},video:state.mode==='video'?{width:{ideal:640},height:{ideal:360}}:false});
    // Permission prompts can outlive a cancelled call; immediately release late tracks.
    if(generation!==state.generation || state.phase==='idle'){stream.getTracks().forEach(t=>t.stop());throw Error('Cuộc gọi đã kết thúc.');}
    state.local=stream;
    if(state.mode==='video') localVideo.srcObject=stream;
    micBtn.hidden=false;cameraBtn.hidden=state.mode!=='video';
    return stream;
  }
  function createPeer(){
    // STUN works for many networks. A TURN relay is necessary for stricter NATs.
    const pc = new RTCPeerConnection({iceServers:[{urls:['stun:stun.l.google.com:19302','stun:stun1.l.google.com:19302']}]});
    state.pc=pc; // Preserve ICE candidates that arrived before peer creation.
    state.local.getTracks().forEach(track=>pc.addTrack(track,state.local));
    pc.onicecandidate=ev=>{
      if(ev.candidate && state.callId) safeSend({type:'call-ice',call_id:state.callId,payload:ev.candidate.toJSON()});
    };
    pc.ontrack=ev=>{
      if(!state.remote) state.remote = new MediaStream();
      if(!state.remote.getTracks().some(t=>t.id===ev.track.id)) state.remote.addTrack(ev.track);
      const output = state.mode==='video'?remoteVideo:remoteAudio;
      output.srcObject = state.remote;
      output.play().catch(()=>setStatus('Nhấn vào khung cuộc gọi để bật âm thanh.'));
      setStatus('Đang trò chuyện');
    };
    pc.onconnectionstatechange=()=>{
      if(pc!==state.pc) return;
      if(pc.connectionState==='failed') setStatus('Không thể kết nối trực tiếp. Mạng của bạn có thể cần máy chủ TURN.');
      else if(pc.connectionState==='connected') setStatus('Đã kết nối');
    };
    return pc;
  }
  async function drainIce(){
    if(!state.pc?.remoteDescription) return;
    const pending=state.pendingIce.splice(0);
    for(const cand of pending){try{await state.pc.addIceCandidate(cand);}catch(e){console.warn('ICE candidate lỗi',e);}}
  }
  function chosenPeer(){const f=activeFriend();return f && userId(f)>0?f:null;}
  function openProfile(){
    const f=chosenPeer();const playerId=f?.player_id;
    if(!playerId) return;
    location.href='user-profile.html?player_id='+encodeURIComponent(playerId);
  }
  profileBtn.addEventListener('click',openProfile);
  function initiate(mode){
    const friend=chosenPeer();
    if(!friend){alert('Chọn bạn bè trước khi gọi.');return;}
    if(state.phase!=='idle'){setStatus('Bạn đã có cuộc gọi đang diễn ra.');return;}
    if(!state.ready){alert('Chưa kết nối tín hiệu gọi. Vui lòng thử lại.');return;}
    state.peerId=userId(friend);state.mode=mode;state.role='caller';state.phase='dialing';
    callUi(mode);setStatus('Đang gọi '+escapeText(friend.username || friend.player_id)+'…');
    safeSend({type:'call-request',peer_id:state.peerId,mode});
    state.ringTimer=setTimeout(()=>{if(['dialing','ringing'].includes(state.phase)){setStatus('Không có phản hồi.');endCall();}},45000);
  }
  audioBtn.addEventListener('click',()=>initiate('audio'));
  videoBtn.addEventListener('click',()=>initiate('video'));
  acceptBtn.addEventListener('click',async()=>{
    if(state.phase!=='incoming'||!state.callId)return;
    acceptBtn.disabled=true;setStatus('Đang xin quyền mic/camera…');
    try{
      await startMedia();
      if(state.phase!=='incoming')return;
      createPeer();
      state.phase='connecting';
      safeSend({type:'call-accept',call_id:state.callId});
      setStatus('Đang kết nối cuộc gọi…');
    }catch(e){setStatus('Không thể dùng mic/camera: '+e.message);safeSend({type:'call-reject',call_id:state.callId});setTimeout(cleanup,1500);}
    finally{acceptBtn.disabled=false;acceptBtn.hidden=true;}
  });
  $('mw-call-hangup').addEventListener('click',()=>endCall());
  $('mw-call-close').addEventListener('click',()=>endCall());
  micBtn.addEventListener('click',()=>{const t=state.local?.getAudioTracks()[0];if(!t)return;t.enabled=!t.enabled;micBtn.textContent=t.enabled?'🎙️ Tắt mic':'🔇 Bật mic';});
  cameraBtn.addEventListener('click',()=>{const t=state.local?.getVideoTracks()[0];if(!t)return;t.enabled=!t.enabled;cameraBtn.textContent=t.enabled?'📷 Tắt camera':'📷 Bật camera';});
  videoBox.addEventListener('click',()=>{remoteVideo.play().catch(()=>{});remoteAudio.play().catch(()=>{});});
  function onPacket(p){
    if(!p||typeof p!=='object')return;
    switch(p.type){
      case 'ready':state.ready=true;break;
      case 'call-ringing':
        if(state.phase!=='dialing')return;
        state.callId=p.call_id;state.phase='ringing';setStatus('Đang đổ chuông…');break;
      case 'incoming-call':
        if(state.phase!=='idle'){safeSend({type:'call-reject',call_id:p.call_id});return;}
        state.callId=p.call_id;state.peerId=Number(p.peer_id);state.mode=p.mode;state.role='callee';state.phase='incoming';
        callUi(p.mode);setStatus(escapeText(p.username)+' đang gọi '+(p.mode==='video'?'video':'thoại')+' cho bạn.');acceptBtn.hidden=false;
        state.ringTimer=setTimeout(()=>{if(state.phase==='incoming')endCall();},45000);
        break;
      case 'call-accepted':
        if(p.call_id!==state.callId||state.role!=='caller'||!['dialing','ringing'].includes(state.phase))return;
        if(state.ringTimer){clearTimeout(state.ringTimer);state.ringTimer=null;}
        state.phase='connecting';setStatus('Đang bật mic/camera…');
        (async()=>{try{
          await startMedia();if(state.phase!=='connecting')return;
          const callId=state.callId,pc=createPeer();const offer=await pc.createOffer();
          if(state.pc!==pc || state.callId!==callId)return;
          await pc.setLocalDescription(offer);
          if(state.pc!==pc || state.callId!==callId)return;
          safeSend({type:'call-offer',call_id:callId,payload:{type:offer.type,sdp:offer.sdp}});
        }catch(e){setStatus('Không thể bắt đầu cuộc gọi: '+e.message);endCall();}})();break;
      case 'call-offer':
        if(p.call_id!==state.callId||state.role!=='callee'||!state.pc)return;
        (async()=>{try{await state.pc.setRemoteDescription(new RTCSessionDescription(p.payload));await drainIce();
          const answer=await state.pc.createAnswer();await state.pc.setLocalDescription(answer);
          safeSend({type:'call-answer',call_id:state.callId,payload:{type:answer.type,sdp:answer.sdp}});
        }catch(e){setStatus('Không thể nhận cuộc gọi: '+e.message);endCall();}})();break;
      case 'call-answer':
        if(p.call_id!==state.callId||state.role!=='caller'||!state.pc)return;
        state.pc.setRemoteDescription(new RTCSessionDescription(p.payload)).then(drainIce).catch(()=>endCall());break;
      case 'call-ice':
        if(p.call_id!==state.callId)return;
        if(!state.pc?.remoteDescription){if(state.pendingIce.length<128)state.pendingIce.push(p.payload);return;}
        state.pc.addIceCandidate(p.payload).catch(()=>{});break;
      case 'call-ended':
        if(p.call_id!==state.callId)return;
        setStatus(p.reason==='rejected'?'Người nhận từ chối cuộc gọi.':'Cuộc gọi đã kết thúc.');
        cleanup();break;
      case 'call-error':
        if(state.phase==='idle')return;
        const error=escapeText(p.detail||'Không thể bắt đầu cuộc gọi.');cleanup();alert(error);break;
    }
  }
  function connect(){
    if(!token())return;
    let ws;
    try{
      const url=new URL(window.MATHWEB_API_URL||'http://127.0.0.1:8000');
      url.protocol=url.protocol==='https:'?'wss:':'ws:';
      url.pathname=url.pathname.replace(/\/$/,'')+'/api/live/calls';url.search='';
      ws=new WebSocket(url.toString());
    }catch(_){return;}
    state.socket=ws;state.ready=false;
    ws.onopen=()=>ws.send(JSON.stringify({type:'auth',token:token()}));
    ws.onmessage=e=>{try{onPacket(JSON.parse(e.data));}catch(err){console.warn('Call message',err);}};
    ws.onerror=()=>{};
    ws.onclose=e=>{
      if(state.socket!==ws)return;
      state.socket=null;state.ready=false;
      if(state.phase!=='idle')cleanup();
      if(e.code!==1008 && (!e.wasClean||e.code!==1000))state.reconnect=setTimeout(connect,3500);
    };
  }
  connect();
  window.addEventListener('beforeunload',()=>{if(state.reconnect)clearTimeout(state.reconnect);cleanup();if(state.socket)state.socket.close(1000,'page closing');});
})();
