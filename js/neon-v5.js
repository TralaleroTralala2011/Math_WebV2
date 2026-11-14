/* Shared MATH_WEB V5 student UI: one navigation, consistent desktop/mobile. */
(()=>{'use strict';
const page=(location.pathname.split('/').pop()||'index.html').toLowerCase();
if(page==='admin.html')return;
const body=document.body;if(!body)return;body.classList.add('mw-v5');
const root=document.createElement('header');root.id='mw-v5-header';root.setAttribute('aria-label','Thanh điều hướng MATH_WEB');
const entries=[['index.html','⌂','Trang chủ'],['practise.html','◎','Luyện tập'],['learn.html','▤','Học tập'],['learning-path.html','⌁','Lộ trình học'],['battle.html','♜','Battle'],['chat.html','▣','Bạn bè & Chat'],['account.html','♙','Tài khoản']];
const activeGroup={'practice.html':'practise.html','learning.html':'learn.html','geometry-learning.html':'learn.html','learning-progress.html':'learning-path.html','study-suite.html':'learn.html','geometry-studio.html':'learn.html'};
const active=activeGroup[page]||page;
const bar=document.createElement('div');bar.className='mw-v5-inner';
const menu=document.createElement('button');menu.className='mw-v5-menu';menu.type='button';menu.textContent='☰';menu.setAttribute('aria-label','Mở menu');menu.setAttribute('aria-expanded','false');
const logo=document.createElement('a');logo.href='index.html';logo.className='mw-v5-logo';logo.innerHTML='<b>∑</b> MATH<em>WEB</em>';
const nav=document.createElement('nav');nav.className='mw-v5-nav';nav.setAttribute('aria-label','Chức năng người học');
for(const [href,emoji,label] of entries){const a=document.createElement('a');a.href=href;a.textContent=emoji+'  '+label;if(active===href){a.classList.add('active');a.setAttribute('aria-current','page')}nav.append(a)}
const actions=document.createElement('div');actions.className='mw-v5-actions';
const search=document.createElement('input');search.className='mw-v5-search';search.placeholder='Tìm chủ đề, bài học...';search.setAttribute('aria-label','Tìm chủ đề');
search.addEventListener('keydown',e=>{if(e.key==='Enter'&&search.value.trim())location.href='learn.html?search='+encodeURIComponent(search.value.trim())});
const bell=document.createElement('a');bell.href='account.html';bell.className='mw-v5-icon';bell.textContent='♧';bell.title='Thông báo tài khoản';bell.setAttribute('aria-label','Thông báo và tài khoản');
const account=document.createElement('a');account.href='login.html';account.className='mw-v5-account';account.textContent='Đăng nhập';
try{if(localStorage.getItem('mathweb_token')){account.href='account.html';account.textContent='Tài khoản'}}catch(e){}
menu.addEventListener('click',()=>{const open=root.classList.toggle('open');menu.setAttribute('aria-expanded',String(open))});
nav.addEventListener('click',()=>{root.classList.remove('open');menu.setAttribute('aria-expanded','false')});
actions.append(search,bell,account);bar.append(menu,logo,nav,actions);root.append(bar);body.prepend(root);
const dock=document.createElement('nav');dock.className='mw-v5-navdock';dock.setAttribute('aria-label','Điều hướng nhanh trên điện thoại');
for(const [href,emoji,label] of [entries[0],entries[1],entries[2],entries[3],entries[4]]){const a=document.createElement('a');a.href=href;const ico=document.createElement('span');ico.textContent=emoji;const text=document.createTextNode(label);a.append(ico,text);if(active===href)a.classList.add('active');dock.append(a)}body.append(dock);
if(page==='account.html')home();
function home(){
 const user={};try{Object.assign(user,JSON.parse(localStorage.getItem('mathweb_profile')||localStorage.getItem('mathweb_user')||'{}')||{})}catch(e){}
 const dash=document.createElement('div');dash.className='mw-v5-canvas mw-v5-home';
 dash.innerHTML=`<div class="mw-v5-row" style="margin-bottom:22px"><div><h1 class="mw-v5-title">Chào mừng trở lại, <span id="mw-v5-username">bạn!</span> 👋</h1><p class="mw-v5-sub">Cùng MATH_WEB chinh phục Toán học mỗi ngày. Mọi chức năng trong một không gian học tập thống nhất.</p></div><div class="mw-v5-pill">∑ Tư duy · Kiến thức · Tiến bộ</div></div>
 <div class="mw-v5-grid"><article class="mw-v5-card"><h2>✧ Tiến trình XP & cấp độ</h2><div class="mw-v5-lead"><div class="mw-v5-ring"><div class="mw-v5-ring-inner"><div>Cấp độ<br><b id="mw-v5-level">1</b></div></div></div><div><div class="mw-v5-kpi" id="mw-v5-xp">0 XP</div><div class="mw-v5-progress" style="width:155px"><span id="mw-v5-xp-bar" style="width:0%"></span></div><p>Tiếp tục luyện tập để tăng XP</p></div></div></article>
 <article class="mw-v5-card"><h2>♨ Chuỗi học tập</h2><div class="mw-v5-kpi" style="font-size:29px" id="mw-v5-streak">Theo dõi tiến độ</div><p>12 tuần gần đây</p><div class="mw-v5-heat" id="mw-v5-heat"></div><p style="font-size:12px">Hoạt động của bạn sẽ được cập nhật từ dữ liệu học tập đã lưu.</p></article>
 <article class="mw-v5-card"><h2>▤ Chủ đề tiếp theo</h2><svg viewBox="0 0 260 116" width="100%" role="img" aria-label="Minh họa đồ thị parabol"><path d="M10 95H247M130 8V110" stroke="#789bb7" fill="none"/><path d="M44 10Q130 177 216 10" fill="none" stroke="#1be9f3" stroke-width="4" stroke-linecap="round"/><path d="M10 25H247M10 60H247" stroke="#16416b" stroke-width=".8"/></svg><h3>Học Toán theo chủ đề</h3><p>Khám phá lý thuyết, video, ví dụ và ôn tập phù hợp với trình độ.</p><a class="mw-v5-btn mw-v5-gradient" href="learn.html">Tiếp tục học →</a></article></div>
 <div class="mw-v5-quick"><a class="mw-v5-card" href="practise.html"><span>◎</span>Luyện tập<small>Làm bài, củng cố kiến thức</small></a><a class="mw-v5-card" href="learn.html"><span>▤</span>Học tập<small>Kiến thức và video bài giảng</small></a><a class="mw-v5-card" href="learning-path.html"><span>⌁</span>Lộ trình học<small>Kiểm tra đầu vào và cá nhân hóa</small></a><a class="mw-v5-card" href="battle.html"><span>♜</span>Battle<small>Thi đấu và xếp hạng</small></a><a class="mw-v5-card" href="chat.html"><span>▣</span>Chat<small>Trao đổi với bạn bè</small></a></div>
 <div class="mw-v5-grid"><article class="mw-v5-card"><h2>▥ Tiến độ theo khối lớp</h2><p>Đánh giá năng lực từng khối lớp từ bài kiểm tra đầu vào.</p><div id="mw-v5-grade-progress"></div></article><article class="mw-v5-card"><h2>✧ AI gia sư cá nhân</h2><p>Nhận diện điểm cần cải thiện từ câu trả lời đúng, sai và bỏ qua. Tư vấn luyện tập phù hợp theo từng chủ đề.</p><p>✓ Phân tích kết quả · ✓ Gợi ý ôn tập · ✓ Theo dõi tiến bộ</p><a class="mw-v5-btn mw-v5-gradient" href="learning-path.html">Nhận gợi ý học tập →</a></article><article class="mw-v5-card"><h2>◎ Gợi ý ôn tập hôm nay</h2><p>Chọn lớp và hoàn thành bài kiểm tra đầu vào để nhận 3 chủ đề học đầu tiên.</p><a href="learning-path.html" class="mw-v5-btn">Xem lộ trình của tôi →</a><p style="font-size:12px">Các chỉ số chỉ hiển thị khi có dữ liệu, không sử dụng số giả lập.</p></article></div>`;
 const accountMain=body.querySelector('#accountPage');
 if(accountMain){dash.id='mw-account-dashboard';accountMain.parentNode.insertBefore(dash,accountMain)}else body.append(dash);
 dash.querySelector('#mw-v5-username').textContent=(user.username||'bạn')+'!';
 dash.querySelector('#mw-v5-level').textContent=String(user.level??1);
 dash.querySelector('#mw-v5-xp').textContent=String(user.xp??0)+' XP';
 const heat=dash.querySelector('#mw-v5-heat');for(let i=0;i<84;i++){const s=document.createElement('i');s.title='Chưa có dữ liệu hoạt động lịch sử';heat.append(s)}
 const progress=dash.querySelector('#mw-v5-grade-progress');for(const grade of [10,11,12]){const row=document.createElement('p');const a=document.createElement('a');a.href='learning-path.html?grade='+grade;a.textContent='Toán '+grade+' →';row.append(a,document.createTextNode(' · Chọn để đánh giá'));progress.append(row)}
 }
})();
