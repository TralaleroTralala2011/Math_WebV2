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
  async function render(container, grade, title, verifiedId) {
    if (!container) return;
    const marker = grade + ':' + title;
    container.dataset.videoTopic = marker;
    container.replaceChildren();
    const search = document.createElement('a');
    search.href = 'https://www.youtube.com/results?search_query=' + encodeURIComponent('Toán ' + grade + ' ' + title + ' bài giảng');
    search.target = '_blank'; search.rel = 'noopener noreferrer';
    search.textContent = 'Tìm thêm video trên YouTube ↗';
    const msg = document.createElement('p'); msg.className = 'muted';
    msg.textContent = 'Đang tìm bài giảng phù hợp…'; container.append(msg);
    if (safeId(verifiedId)) {
      container.replaceChildren(player(verifiedId, 'Bài giảng ' + title), search);
      return;
    }
    try {
      const key = marker.toLowerCase();
      let result = cache.get(key);
      if (!result) {
        const url = 'http://127.0.0.1:8000/api/learning/videos?grade=' + encodeURIComponent(grade) + '&topic=' + encodeURIComponent(title);
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
        const list = document.createElement('div'); list.className = 'mw-video-list';
        const stage = document.createElement('div'); stage.className = 'mw-video-stage';
        result.videos.forEach(v => {
          if (!safeId(v.id)) return;
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
        container.append(heading, stage, list, search);
      } else {
        msg.textContent = result.message || 'Chưa tìm được video nhúng phù hợp. Bạn vẫn có thể học lý thuyết hoặc làm bài tập.';
        container.append(msg, search);
      }
    } catch {
      if (container.dataset.videoTopic !== marker) return;
      msg.textContent = 'Chưa kết nối được thư viện video. Hãy kiểm tra backend hoặc dùng liên kết YouTube.';
      container.replaceChildren(msg, search);
    }
  }
  return {render};
})();
