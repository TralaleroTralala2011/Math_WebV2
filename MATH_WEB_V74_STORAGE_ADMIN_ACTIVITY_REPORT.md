# MATH_WEB V74 | Bảo vệ dữ liệu, Admin và nhật ký học tập

## Phạm vi thay đổi
- Bắt đầu từ ZIP **MATH_WEB V73**. Không chỉnh sửa câu hỏi trong Word, JSON, JSONL hoặc các cơ sở dữ liệu ngân hàng câu hỏi.
- Thêm API ghi nhận **sự kiện học tập từ trình duyệt của người đã đăng nhập** (`POST /api/activity/events`). Sự kiện chỉ là nhật ký, **không được dùng để cộng XP hay công nhận kết quả thi chính thức**.
- 528 trang game gửi sự kiện trả lời/bỏ qua/hoàn thành qua cùng một helper. Khi mất mạng, helper cố gắng gửi lại một số sự kiện được lưu tạm, có chống gửi trùng bằng `event_id`.
- Admin > Tài khoản: thêm bảng sự kiện học tập và lịch sử Battle backend theo từng người, phân biệt sự kiện trình duyệt với kết quả chấm từ backend.
- Admin > Tổng quan: báo trạng thái cấu hình nơi lưu dữ liệu (`/api/admin/storage-status`). Trạng thái `configured_not_verified` **không** chứng minh có Render Disk.
- Backend: bắt lỗi không lường trước thành JSON 500 bên trong middleware CORS, để lỗi ứng dụng không bị báo nhầm như CORS nếu API vẫn hoạt động.

## VẤN ĐỀ ĐÃ XÁC ĐỊNH
`backend/database/database.py` dùng SQLite và `MATHWEB_DB_PATH`. Trên Render Free, ổ đĩa mặc định là tạm, nên có nguy cơ mất dữ liệu sau deploy; CORS không phải nguyên nhân xóa dữ liệu. **ZIP này không tự khôi phục 20 tài khoản đã mất.** Muốn khôi phục phải có database/bản backup thật.

## TRIỂN KHAI AN TOÀN, CẦN LÀM TRƯỚC
1. Vào Render > Environment: giữ **không đổi** `MATH_WEB_SECRET_KEY` (ít nhất 32 ký tự), và không xóa các biến hiện có.
2. Dịch vụ pilot cần **persistent disk thực sự** (thường gói trả phí hỗ trợ), mount tại `/var/data`. Trong Environment: `MATHWEB_DATA_DIR=/var/data`, `MATHWEB_DB_PATH=/var/data/mathweb.db`, `MATHWEB_AI_HISTORY_DB_PATH=/var/data/mathweb_ai_history.sqlite3`.
3. **Không** tải database rỗng từ ZIP lên vị trí đang chứa database đang hoạt động. Dùng bản sao lưu `.mwbackup` trước mọi thao tác di chuyển dữ liệu, giữ mật khẩu backup.
4. Muốn xác định 20 tài khoản cũ còn hay mất: kiểm tra database hiện ở Render, bản backup `.mwbackup`, dữ liệu ở instance/disk trước. Không bấm nút Khôi phục khi chưa đối chiếu.
5. Cập nhật **backend và frontend cùng phiên bản V74**, theo đúng cấu trúc thư mục, sau đó xem Admin > Tổng quan > cảnh báo lưu trữ; xác nhận `GET /health` trả 200 và API Admin trả dữ liệu.
6. Phải có sao lưu ngoài Render có kiểm thử khôi phục. Persistent disk không thay thế backup.

## CHƯA ĐẠT QUY MÔ TRIỆU NGƯỜI
Hệ thống hiện vẫn dùng SQLite và một backend FastAPI. Đây là mô hình pilot, **không phải** hệ thống đã được chứng minh chịu hàng triệu tài khoản đồng thời. Quy mô lớn cần PostgreSQL quản lý tập trung, connection pooling, API stateless, cache/queue và kiểm thử tải thực tế trước công bố. V74 không tuyên bố đã chuyển database sang PostgreSQL.

## RANH GIỚI KIỂM CHỨNG
- Đã kiểm tra 13 bài test hồi quy; API CORS có phản hồi từ origin GitHub Pages; event ghi, chống trùng và Admin đọc lại trong DB độc lập.
- Cú pháp inline JS trên 528 trang game đã được kiểm tra.
- Chromium trên localhost trong môi trường kiểm thử bị chặn kết nối, nên chưa xác minh luồng click bằng trình duyệt thật.
- Chưa kiểm thử trên dịch vụ Render production, chưa đo throughput/hàng triệu kết nối, chưa kiểm chứng độc lập toàn bộ câu toán trong ngân hàng.

## Lưu ý về ZIP triển khai
Để tránh ghi đè tài khoản thật hoặc vô tình đưa bí mật lên GitHub, ZIP V74 **không chứa** database tài khoản mẫu `backend/database/mathweb.db`, các cơ sở dữ liệu học tập phát sinh tại runtime trong `backend/database/`, hoặc khóa ký `.mathweb_hmac_secret`. Bản gốc trong ZIP V73 mà bạn đã cung cấp vẫn được giữ nguyên tại nguồn của bạn; không có thao tác khôi phục/xóa dữ liệu Render nào được thực hiện.
