/* Shared on-demand YouTube lesson browser. YouTube videos remain hosted by YouTube. */
window.MathWebVideos = (() => {
  const cache = new Map();
  const safeId = id => typeof id === 'string' && /^[A-Za-z0-9_-]{11}$/.test(id);
  function player(id, title) {
    const frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/' + id + '?rel=0';
    frame.title = title || 'Bài giảng Toán';
    frame.loading = 'lazy'; frame.allowFullscreen = true;
    frame.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.style.cssText = 'display:block;width:100%;aspect-ratio:16/9;border:0;border-radius:16px;background:#10192c';
    return frame;
  }
  async function render(container, grade, title, verifiedId, area = "learning") {
    if (!container) return;
    const marker = grade + ':' + title + ':' + area;
    container.dataset.videoTopic = marker;
    container.replaceChildren();
    const search = document.createElement('a');
    search.href = 'https://www.youtube.com/results?search_query=' + encodeURIComponent('Toán ' + grade + ' ' + title + ' bài giảng');
    search.target = '_blank'; search.rel = 'noopener noreferrer';
    search.textContent = 'Tìm thêm video trên YouTube ↗';
    const msg = document.createElement('p'); msg.className = 'muted';
    msg.textContent = 'Đang tìm bài giảng phù hợp…'; container.append(msg);
    // Curated local catalogue works on GitHub Pages without localhost backend.
    const catalogue = await fetch('learn-assets/curated-videos.json').then(r=>r.ok?r.json():{}).catch(()=>({}));
    if (container.dataset.videoTopic !== marker) return;
    const topicKey = String(grade) + ':' + title.normalize('NFC').trim().toLocaleLowerCase('vi');
    const otherArea = area === 'learning' ? 'path' : 'learning';
    const reserved = new Set((catalogue[topicKey]?.[otherArea] || []).map(v => v.id));
    const seen = new Set();
    const curated = (catalogue[topicKey]?.[area] || []).filter(v => {
      if (!safeId(v.id) || v.status !== 'verified' || reserved.has(v.id) || seen.has(v.id)) return false;
      seen.add(v.id); return true;
    }).slice(0, 3);
    if(curated.length){
      renderVideos(curated,container,search,player);
      return;
    }
    if (safeId(verifiedId) && !((catalogue[topicKey]?.[area] || []).length || (catalogue[topicKey]?.[area === 'learning' ? 'path' : 'learning'] || []).some(v => v.id === verifiedId))) {
      container.replaceChildren(player(verifiedId, 'Bài giảng ' + title), search);
      return;
    }
    try {
      const key = marker.toLowerCase();
      let result = cache.get(key);
      if (!result) {
        const url = (location.hostname === 'localhost' || location.hostname === '127.0.0.1' ? 'http://127.0.0.1:8000' : '') + '/api/learning/videos?grade=' + encodeURIComponent(grade) + '&topic=' + encodeURIComponent(title);
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 8500);
        try {
          const response = await fetch(url, {signal:controller.signal});
          if (!response.ok) throw Error('Video API unavailable');
          result = await response.json(); cache.set(key, result);
        } finally { clearTimeout(timer); }
      }
      if (container.dataset.videoTopic !== marker) return;
      container.replaceChildren();
      if (result.videos?.length) {
        const heading = document.createElement('p'); heading.className = 'muted';
        heading.textContent = 'Video gợi ý từ YouTube. Chọn video để phát ngay trong trang.';
        const list = document.createElement('div'); list.className = 'mw-video-list'; list.setAttribute('aria-label','Danh sách video cuộn ngang');
        const stage = document.createElement('div'); stage.className = 'mw-video-stage';
        const existingIds = new Set((catalogue[topicKey]?.[area === 'learning' ? 'path' : 'learning'] || []).map(v=>v.id));
        const seenIds = new Set();
        result.videos.forEach(v => {
          if (!safeId(v.id) || existingIds.has(v.id) || seenIds.has(v.id)) return;
          seenIds.add(v.id);
          const btn = document.createElement('button'); btn.type = 'button';
          btn.className = 'mw-video-card';
          const img = document.createElement('img'); img.src = v.thumbnail;
          img.alt = ''; img.loading = 'lazy';
          const info = document.createElement('span');
          const name = document.createElement('strong'); name.textContent = v.title;
          const channel = document.createElement('small'); channel.textContent = v.channel;
          info.append(name, channel); btn.append(img, info);
          btn.onclick = () => {stage.replaceChildren(player(v.id, v.title));};
          list.append(btn);
        });
        const nav=document.createElement('div');nav.className='mw-video-nav';
        for(const [symbol,dir,label] of [['←',-1,'Video trước'],['→',1,'Video tiếp']]){
          const b=document.createElement('button');b.type='button';b.textContent=symbol;b.setAttribute('aria-label',label);
          b.onclick=()=>list.scrollBy({left:dir*Math.max(250,list.clientWidth*.8),behavior:'smooth'});nav.append(b);
        }
        if(list.children.length<3){const warning=document.createElement('p');warning.className='muted';warning.textContent='Hiện chỉ xác minh được '+list.children.length+' video cho chủ đề này; chưa đủ mục tiêu 3 video.';container.append(warning)}
        if (!list.children.length) { msg.textContent='Chưa có video phù hợp không trùng với khu vực còn lại.'; container.append(msg,search); return; }
        container.append(heading, stage, nav, list, search);
      } else {
        msg.textContent = result.message || 'Chưa tìm được video nhúng phù hợp. Bạn vẫn có thể học lý thuyết hoặc làm bài tập.';
        container.append(msg, search);
      }
    } catch {
      if (container.dataset.videoTopic !== marker) return;
      msg.textContent = 'Chưa có video đã kiểm duyệt cho chủ đề này. Bạn vẫn có thể học lý thuyết và làm bài tập.';
      container.replaceChildren(msg, search);
    }
  }
  function renderVideos(videos,container,search,makePlayer){
    const heading=document.createElement('p');heading.className='muted';heading.textContent='Video đã được biên tập cho khu vực này.';
    const stage=document.createElement('div');stage.className='mw-video-stage';
    const list=document.createElement('div');list.className='mw-video-list';
    videos.slice(0,3).forEach((v,i)=>{
      const b=document.createElement('button');b.type='button';b.className='mw-video-card';
      const im=document.createElement('img');im.src='https://i.ytimg.com/vi/'+v.id+'/hqdefault.jpg';im.alt='';im.loading='lazy';
      const info=document.createElement('span');const strong=document.createElement('strong');strong.textContent=(i+1)+'. '+v.title;
      const small=document.createElement('small');small.textContent=v.channel||'YouTube';info.append(strong,small);b.append(im,info);
      b.onclick=()=>stage.replaceChildren(makePlayer(v.id,v.title));list.append(b);
    });
    stage.append(makePlayer(videos[0].id,videos[0].title));container.replaceChildren(heading,stage,list,search);
    if(videos.length<3){const warn=document.createElement('p');warn.className='muted';warn.textContent='Đã kiểm duyệt '+videos.length+'/3 video; các vị trí còn lại đang chờ bổ sung.';container.append(warn)}
  }
  return {render};
})();
