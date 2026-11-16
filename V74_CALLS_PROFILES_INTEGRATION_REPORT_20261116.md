# MATH_WEB V74 + Gọi thoại, gọi video, hồ sơ người dùng và sửa tương phản câu hỏi

## Nguồn
- Dựng bản đầy đủ từ V70; tích hợp các bản vá V70-only, V72, V73, V74 theo thứ tự.
- Sau đó áp dụng tập thay đổi chức năng từ V76 (được phát triển dựa trên V74 và sửa tương phản V75).
- Không cố ý thay thế ngân hàng câu hỏi và dữ liệu người dùng bằng bản dữ liệu mới.

## Tính năng
- Gọi thoại 1-1 và gọi video 1-1 trên trang Chat bằng WebRTC.
- Cần đăng nhập, có quan hệ bạn bè được chấp nhận và đồng ý nhận cuộc gọi.
- Từ chối, kết thúc cuộc gọi, bật/tắt micro hoặc camera; không lưu nội dung âm thanh/video.
- Mở trang hồ sơ người dùng khác từ Chat, chỉ hiển thị thông tin công khai.
- Chỉnh CSS cho câu hỏi, đáp án và hộp thoại luyện tập để nội dung không bị chìm màu.
- Các chức năng và ngân hàng câu hỏi của bản nền được giữ lại khi tích hợp.

## Kiểm chứng trong phiên này
- `pytest -q backend/tests/test_calls_v76.py`: 2 bài đạt.
- `python scripts/v74_smoke.py`: đạt.
- `node --check js/chat.js js/chat-calls-v76.js js/user-profile-v76.js`: đạt.

## Giới hạn chưa kiểm chứng
- Chưa kiểm thử cuộc gọi âm thanh/video hai chiều trên 2 trình duyệt thật hoặc trên Render.
- STUN-only có thể không vượt được NAT: muốn ổn định trên mọi mạng cần TURN.
- Phần tín hiệu cuộc gọi lưu trạng thái trong một tiến trình: dùng 1 worker, hoặc mở rộng qua Redis nếu triển khai đa worker.
- Chat phải được mở để nhận cuộc gọi; HTTPS và quyền trình duyệt với micro/camera là bắt buộc trên môi trường công khai.
- Không có cơ sở khẳng định toàn hệ thống không còn bất kỳ lỗi nào chỉ từ các kiểm thử trên.
