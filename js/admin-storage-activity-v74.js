/* MATH_WEB V74: storage risk warnings and account-specific activity timeline.
   The API enforces admin authorization; nothing here is used as proof of grading. */
(function(){'use strict';
 const escape = value=>String(value??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
 const dateText=x=>x?new Date(x).toLocaleString('vi-VN'):'Chưa có';
 const labels={question_answered:'Đã trả lời câu hỏi',question_skipped:'Bỏ qua câu hỏi',game_completed:'Đạt mốc game',practice_started:'Bắt đầu luyện tập',topic_opened:'Mở chủ đề'};
 window.MWLoadStorage=async function(){
   const host=document.getElementById('mw-storage-status-v74');if(!host)return;
   host.classList.remove('hidden');host.className='notice';host.textContent='Đang kiểm tra trạng thái lưu trữ máy chủ…';
   try{
     const result=await api('/api/admin/storage-status');
     const risky=result.status==='risk';
     host.className='notice '+(risky?'error':'ok');
     host.textContent=(risky?'⚠ Nguy cơ mất dữ liệu: ':'ℹ Lưu trữ: ')+String(result.message||'')+
       (Array.isArray(result.concerns)&&result.concerns.length?' '+result.concerns.join(' '):'');
     const facts=document.getElementById('mw-v79-safety-facts');
     if(facts)facts.textContent='Tài khoản hiện có: '+(result.accounts_now??'chưa rõ')+
       ' · Mốc cao nhất đã ghi: '+(result.accounts_high_watermark??'chưa rõ')+
       ' · Điểm khôi phục trên máy chủ: '+(result.snapshot_count??0)+
       ' · Disk gắn riêng: '+(result.disk_mount_verified?'Đã phát hiện':'Chưa xác nhận')+
       ' · Bản sao lưu bên ngoài: CHƯA XÁC MINH';
   }catch(error){host.className='notice error';host.textContent='Không kiểm tra được nơi lưu dữ liệu: '+String(error.message||error)+'. Không thể kết luận tài khoản đã bị xóa.';}
 };
 document.addEventListener('DOMContentLoaded',()=>{
   const create=document.getElementById('mw-v79-snapshot');
   const note=document.getElementById('mw-v79-snapshot-msg');
   if(create&&note)create.addEventListener('click',async()=>{
     create.disabled=true;note.className='notice';note.textContent='Đang chụp bản sao SQLite nhất quán...';
     try{
       const result=await api('/api/admin/storage/snapshot',{method:'POST'});
       note.className='notice '+(result.ok?'ok':'error');
       note.textContent=result.ok?'Đã tạo điểm khôi phục. '+result.warning:String(result.reason||'Không tạo được bản sao lưu.');
       await window.MWLoadStorage();
     }catch(e){note.className='notice error';note.textContent='Sao lưu thất bại: '+e.message;}
     finally{create.disabled=false;}
   });
   document.getElementById('mw-v79-open-backup')?.addEventListener('click',()=>document.querySelector('.navbtn[data-page="update"]')?.click());
 });
 window.MWRenderUserExtras=function(data,host){
   if(!host||!data)return;
   const section=document.createElement('section');section.className='panel';section.style.marginTop='16px';
   const activity=Array.isArray(data.recent_activity)?data.recent_activity:[];
   const battles=Array.isArray(data.recent_battles)?data.recent_battles:[];
   const activityBody=activity.map(row=>`<tr><td>${escape(dateText(row.created_at))}</td><td>${escape(labels[row.event_type]||row.event_type)}</td><td>${escape(row.topic||'')}</td><td>${escape(row.question_text||'')}</td><td>${escape(row.selected_answer||'')}</td><td>${row.client_is_correct===null?'Chưa chấm':row.client_is_correct===1?'Báo đúng':'Báo sai'}</td></tr>`).join('');
   const battleBody=battles.map(row=>`<tr><td>${escape(dateText(row.finished_at||row.started_at))}</td><td>${escape(row.opponent_username||'Không có dữ liệu')}</td><td>${escape(row.status||'')}</td><td>${escape(row.own_correct??0)} đúng · ${escape(row.own_wrong??0)} sai</td></tr>`).join('');
   section.innerHTML=`<h3>Nhật ký học tập phía máy chủ · ${escape(data.activity_total??activity.length)} sự kiện</h3>
     <p class="muted">Các sự kiện từ trình duyệt chỉ dùng để theo dõi hoạt động, <strong>không phải kết quả chấm được kiểm chứng</strong>. Điểm XP và bài kiểm tra chính thức chỉ lấy từ backend.</p>
     <div class="tablewrap"><table><thead><tr><th>Thời gian</th><th>Hoạt động</th><th>Chủ đề</th><th>Câu hỏi</th><th>Đáp án nhập</th><th>Trạng thái báo về</th></tr></thead><tbody>${activityBody||'<tr><td colspan="6">Chưa có sự kiện đồng bộ về máy chủ.</td></tr>'}</tbody></table></div>
     <h3 style="margin-top:20px">Lịch sử Battle (từ máy chủ)</h3>
     <div class="tablewrap"><table><thead><tr><th>Thời gian</th><th>Đối thủ</th><th>Trạng thái</th><th>Kết quả</th></tr></thead><tbody>${battleBody||'<tr><td colspan="4">Chưa có trận Battle được lưu.</td></tr>'}</tbody></table></div>`;
   host.appendChild(section);
 };
})();
