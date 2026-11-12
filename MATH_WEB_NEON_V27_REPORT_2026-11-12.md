# MATH_WEB NEON V27 · sửa giao diện theo Math_WebV2 và phản hồi người dùng

Ngày: 12/11/2026. Nền: thư mục MATH_WEB_GITHUB_READY V26 đang được chỉnh từ V25, đối chiếu ZIP `Math_WebV2-main(4).zip`. Không thay thế cơ sở dữ liệu.

## Đã sửa trong mã

1. Thanh điều hướng chung: ở đầu trang, cuộn xuống khuất đi và chỉ hiện lại khi quay lên; bỏ sticky header. Không đổi quyền người dùng/Admin.
2. Notification: ở thanh V26 mới, biểu tượng chuông trước đó là liên kết sang Tài khoản, còn bộ điều khiển thật bị giữ trong header ẩn. V27 tạo nút chuông thực, chuyển panel thông báo ra ngoài header ẩn, dùng lại API `notification.js`, badge và nút đánh dấu đã đọc. Các trang không nhúng script tự tải controller.
3. Battle: áp dụng lớp bố cục gọn trên máy tính có chiều cao đủ, thanh điều hướng + màn hình đấu + footer trong một viewport, nội dung từng màn hình có thể cuộn bên trong nếu dài. Trên điện thoại và máy thấp vẫn cho cuộn để không cắt câu hỏi, bàn phím và nút nộp. Vẫn dùng battle.js và cơ chế WebSocket trước đó.
4. Lộ trình: bỏ che nội dung do xung đột header, tránh chữ bị ép từng ký tự, bảo toàn giao diện thẻ và đầu trang. Bộ đề chính thức vẫn bị khoá khi chưa đạt gate kiểm duyệt câu.
5. Hình trong câu hỏi lộ trình: bỏ nút chỉ bật popup MathGeo, hiển thị SVG inline khi dựng được từ dữ kiện. Có dựng tam giác từ ba cạnh hợp lệ, hình phác họa tam giác không ghi góc/cạnh suy diễn, điểm Oxy (tỷ lệ trục bằng nhau), điểm Oxyz (hình chiếu trục đo, không đo độ dài trên hình), hình tròn minh hoạ. Nếu không có dữ kiện đủ để dựng hình, không bịa hình. Giữ nguyên trang MathGeo Studio Pro dành cho vẽ tự do.
6. Đồng bộ stylesheet V27 cho 17 trang đã có V26. Những trang dùng bộ giao diện khác chưa được xác nhận tương thích hoàn toàn.

## Kiểm thử

- Backend: `pytest -q -k 'not test_trig_equation_topic_survives_multiple_sets'`: **226 passed, 1 deselected** (không tính ca đã bỏ qua là đạt).
- `node --check` trên JS V27, roadmap, notification script: đạt.
- Playwright cô lập: màn hình chọn mode Battle ở viewport 1366×768 không cuộn cả trang, 390×844 không tràn ngang; header position relative ở cả hai.
- Playwright cô lập: SVG từ tam giác ba cạnh, tọa độ Oxy, tam giác minh hoạ, và không sinh hình đối với phương trình đại số thường.
- Playwright cô lập: nút Notification mới chuyển panel sang BODY, một ID duy nhất, mở được bằng controller stub.
- Chromium trong môi trường hiện tại chặn mở địa chỉ localhost và file:// của dự án (`ERR_BLOCKED_BY_ADMINISTRATOR`). Vì thế **chưa có thử nghiệm end-to-end trên website chạy đầy đủ**, đăng nhập thật, quyền notification server, WebSocket hai máy hoặc thiết bị vật lý. Ảnh Playwright chỉ là kiểm thử giao diện cô lập.

## Chưa hoàn thành 100%

- Đề đầu vào cố định lớp 10–12 chưa có đủ câu được người duyệt độc lập chứng nhận (mỗi chủ đề 3 câu ở ba mức). Giữ gate, không tự mở đề hoặc huấn luyện AI từ câu chưa duyệt.
- Chưa thể bảo đảm mọi đề hình học đều có hình tự động chính xác nếu dữ kiện chưa đủ hoặc định dạng nằm ngoài hỗ trợ.
- Chưa kiểm thử Battle thật với hai tài khoản/thiết bị và notification với backend và dữ liệu thực.
- Chưa chứng minh toàn bộ 17+ trang trên mọi điện thoại đạt hoàn thiện tuyệt đối.

## Tệp sửa chính

- `css/neon-v27-usability.css`, `js/neon-v27-usability.js`, `js/geometry-inline-v27.js`, `js/roadmap-v5.js`.
- 17 trang HTML có liên kết stylesheet/script V27.
- `backend/tests/test_neon_v27_usability.py` và cập nhật kiểm thử cũ phù hợp tính năng vẽ hình nội tuyến.

## Chạy thử

Frontend từ thư mục gốc: `python -m http.server 5500`. Backend từ `backend`: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`. Cần chạy backend và dùng tài khoản thực để đánh giá các luồng có API. Trước khi cập nhật, sao lưu database/khóa hiện có.
