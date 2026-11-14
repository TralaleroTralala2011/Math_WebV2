# MATH_WEB V51: Scoped Practice / Friends / Battle / Mobile patch

Nền: MATH_WEB V50. Không thay database, tài khoản, Admin, thiết kế Battle chính, nguồn câu hỏi hay backend ghép trận trong bản này.

## Cải tiến

1. `practice.html` và `practise.html` vẫn có nội dung giống hệt nhau; các liên kết chính được thống nhất về `practise.html`. `practice.html` vẫn hoạt động như đường dẫn tương thích.
2. Khi tìm bạn đang có lời mời **gửi đến mình**, hiển thị nút Chấp nhận (không báo nhầm "Đã gửi lời mời"). Dùng chính API `/api/friends/accept/{id}` có sẵn.
3. Nút Kết bạn có thể thử lại khi gửi thất bại do mất mạng/Render ngủ. Chặn bấm lặp trong lúc yêu cầu đang xử lý.
4. Mobile: navbar chính được cố định phía trên cùng, thanh 5 tính năng được cố định phía dưới, chừa khoảng an toàn nội dung để không bị che.
5. Battle: đồng hồ đếm 300 giây dựa trên `server_now`, `started_at` và `performance.now()` để không bị sai nếu thiết bị chỉnh giờ; chặn gửi lặp thao tác chấp nhận lời mời. Việc chấp nhận trận và bộ câu hỏi chung tiếp tục sử dụng backend V50.
6. Chọn chủ đề tự động từ ngân hàng V254 của Battle được giữ nguyên từ V50. Không tự thêm hoặc chứng nhận câu hỏi mới.

## Kiểm chứng

- 32/32 bài kiểm thử scoped đạt (V22, V23, V37, V47, V48, V50, V51).
- `node --check` đạt cho 5 tệp JS liên quan.
- Hai đường dẫn HTML Luyện tập có SHA-256 giống nhau.
- ZIP được kiểm tra CRC sau đóng gói.
- Chưa kiểm thử trực tiếp bằng hai thiết bị trên Render + GitHub Pages; cần triển khai và thử thực tế trước khi tuyên bố hoàn thành 100%.
- Các bài kiểm thử toán học ngoài phạm vi chưa sửa.

## Cách triển khai

Cập nhật phiên bản trong repo GitHub, giữ database đang dùng. GitHub Pages tải frontend; Render chạy backend. Xóa cache trang bằng Ctrl+F5 trên máy tính hoặc tải lại trang trên điện thoại.
