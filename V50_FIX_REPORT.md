# MATH_WEB V50 | Luyện tập / Bạn bè / Battle / Mobile navigation

## Nguồn và phạm vi

Được tạo từ **MATH_WEB_V49_CREDITS_UPDATE_20261114.zip**.
Chỉ chỉnh sửa đúng 6 tệp gốc: `practice.html`, `practise.html`,
`js/account.js`, `js/battle.js`, `backend/app/matchmaking/routes.py`,
`css/v42-shared-navbar-flush.css`. Mọi tệp gốc còn lại được bảo toàn nguyên nội dung
(đối chiếu SHA-256). Hai file mới là báo cáo này và kiểm thử V50.
Không đụng cơ sở dữ liệu, Admin, tài khoản, ngân hàng câu hỏi, trang hình học,
Học tập hoặc Lộ trình học.

## Sửa lỗi cụ thể

1. Hai URL `practice.html` và `practise.html` có cùng nội dung giao diện
   theo bản `practise.html` đẹp hơn, cùng chạy `js/practise.js` gốc và bộ trò chơi cũ.
   Thay phần popup từ `<section>` sang native `<dialog>` và bật bộ điều khiển popup V47,
   tránh lớp phủ tối che mất khung.
2. Tài khoản: sửa lệch ID DOM giữa HTML và JS (`friendPlayerId`,
   `searchFriendButton`, `friendList`, `friendRequests`).
   Cập nhật lời mời sau khi gửi và kiểm tra lời mời mới theo chu kỳ 10s khi tab hiện.
3. Battle: chấp nhận lời mời bằng **một API** chuyển trạng thái trực tiếp sang
   `PLAYING`, lưu `started_at` trên server, tránh hai thiết bị chờ lệnh bắt đầu khác nhau.
   `/match/{id}` trả `server_now` + `duration_seconds` để đồng hồ hai thiết bị
   lấy chung mốc 5 phút từ backend. `/start` cũ vẫn tương thích.
4. Battle tự chọn (không chọn chủ đề): chọn ngẫu nhiên tối đa 5 chủ đề có câu hỏi
   trắc nghiệm lưu trong ngân hàng của khối 10/11/12. Lọc đáp án và kiểm tra
   câu hỏi vẫn chạy trên server như V49; các chủ đề đã chọn thủ công giữ nguyên.
5. Mobile: header sticky trên đầu; dock năm chức năng fixed tại đáy màn hình,
   tôn trọng safe-area và chừa khoảng cuối trang, không chồng nội dung.

## Kiểm tra đã thực hiện

- 25/25 bài kiểm thử API, hồi quy liên quan V22/V37/V47/V48/V50 đạt.
- Chromium DOM sandbox không cần truy cập localhost: 147 thẻ chủ đề được
  render; popup mở/đóng, 3 trò chơi + nút AI xuất hiện, không có JS exception.
- DOM sandbox account: tìm theo Player ID, hiển thị người chơi, gửi lời mời,
  đổi nhãn thành Đã gửi lời mời, không có JS exception.
- Mobile DOM: header sticky top và bottom dock fixed đáy.
- Node --check js/account.js và js/battle.js; Python compileall; CRC toàn ZIP.
- Bộ test mở rộng khác: 16 đạt, 2 lỗi trước đó ở difficulty.normalize()
  và solver.equivalent(). Các tệp đó y nguyên V49 nên không sửa ngoài phạm vi.

## Chưa được xác minh thực tế

- Không thể kết nối để thử hai thiết bị thật trên Render/GitHub Pages trong môi
  trường này. Cần triển khai cùng phiên bản frontend GitHub Pages + backend Render
  và kiểm tra login, lời mời, WebSocket/presence, đồng hồ và danh sách bạn.
- Render Free nếu dùng SQLite trên lưu trữ tạm có thể làm mất dữ liệu giữa deploy;
  không nên xóa hay khởi tạo lại DB hiện tại.
- Không có bằng chứng toàn bộ ngân hàng câu hỏi V254 đã được thẩm định.
