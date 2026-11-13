# MATH_WEB V37 | Battle 5 phút, câu hỏi từ ngân hàng

## Đã thay đổi
- Thời gian trận đấu: 300 giây do backend quyết định; frontend hiển thị đếm ngược 05:00.
- Không gọi bộ sinh AI cho Battle. Lấy câu từ `admin_question_bank` và `v254_candidates.sqlite`, xác thực cấu trúc/đáp án trước khi đưa vào trận.
- Khởi tạo 10 câu; khi người chơi làm hết, API GET `/api/matchmaking/match/{id}` bổ sung một đợt câu từ ngân hàng vào bộ đề chung cho cả hai người, tránh trùng nội dung trong trận.
- Không tự kết thúc khi cả hai làm hết 10 câu; trận chỉ kết thúc khi hết 5 phút. Giữ nguyên API trả lời, bỏ qua, thống kê, websocket.
- Nếu ngân hàng không đủ câu phù hợp, hệ thống báo thiếu dữ liệu, **không tạo câu giả**. "Vô hạn" có nghĩa là không áp hạn mức số câu trong 5 phút, không có nghĩa ngân hàng dữ liệu vô hạn.

## Kiểm thử
- 16 bài test tập trung (V37, luồng 2 tài khoản và API integration): đạt.
- Bộ test hồi quy cũ có bài kiểm tra kết thúc trận sau đúng 10 câu; bài này không còn phù hợp với luật chơi mới và sẽ thất bại nếu chưa cập nhật kỳ vọng.
- Chưa kiểm thử E2E trên Render/GitHub thật hoặc Battle 2 thiết bị thật; không cam kết không lỗi sản xuất.

## Triển khai
Đẩy nội dung thư mục dự án lên GitHub, triển khai lại cả backend Render. Phải giữ dữ liệu ngân hàng V254 khi deploy. Kiểm tra 2 tài khoản cùng trận, vượt câu 10 và chờ đến phút 5 để xác nhận kết quả. Đảm bảo lưu trữ SQLite bền vững.
