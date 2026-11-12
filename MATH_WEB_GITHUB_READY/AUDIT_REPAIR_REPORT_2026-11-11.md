# MATH_WEB · Rà soát bổ sung và sửa lỗi lần 2 (11/11/2026)

## Nguồn và nguyên tắc

- Cơ sở: `MATH_WEB_GITHUB_READY_AUDIT_FIXED_2026-11-10.zip`, đã được chỉnh từ `Math_WebV2-main(1).zip` của người dùng. Không ghép ngược bản ZIP cũ.
- Giữ nguyên tên thư mục chính `MATH_WEB_GITHUB_READY`, các trang, bộ câu hỏi, game, API và chức năng hiện có. Thay đổi tập trung vào lỗi xác định được.
- Các thư mục `MATH_WEB/` và `mathweb_work/` là bản sao tham chiếu cũ được giữ để không làm mất dữ liệu. **Chỉ chạy dự án chính tại thư mục `MATH_WEB_GITHUB_READY`**.

## Lỗi tìm thêm và sửa trong lượt này

1. **45 trang game lỗi JavaScript khi mở:** mã dùng `document.querySelector('<button ...>')` thay vì bộ chọn `#nextQuestion`, gây `SyntaxError` ngay trong quá trình khởi tạo và chặn chơi. Đã thay đúng ở cả 45 trang.
2. **529 trang game có thể được mở trực tiếp không qua chặn đăng nhập:** thêm `protected-pages.js` với đường dẫn tương đối đúng ở các thư mục game 2 hoặc 3 tầng; cập nhật logic xác định trang game và điều hướng tới login. Không thay engine của game.
3. **Điện thoại cùng Wi-Fi trỏ sai API backend:** `js/api-config.js` trước đó nhận IP LAN (`192.168.x.x`, `10.x.x.x`, `172.16–31.x.x`) là deployment công khai, khiến backend chạy tại máy trong mạng LAN không được gọi. Đã tự chọn `http://<IP-LAN-frontend>:8000` cho địa chỉ LAN; giữ `127.0.0.1:8000` cho localhost và Render cho website công khai.
4. **Battle xử lý tiêu chí thời gian không chính xác:** hàm tổng kết trước đó tính lại thời gian cho cả hai tại cùng thời điểm và làm mất chênh lệch thời gian. Đã sử dụng thời gian đã ghi nhận riêng khi từng người hoàn thành, đo chính xác tới mili giây và so sánh dạng số thực.
5. **Battle cho phép gửi câu trả lời/bỏ qua ngoài thứ tự:** đã chặn `question_index` không đúng câu tiếp theo, hạn chế gửi trước/nhảy câu. Bổ sung `BEGIN IMMEDIATE` khi ghi đáp án và bỏ qua, ngăn hai request đồng thời ghi đè cùng trạng thái trong SQLite.
6. **Ba nút truy cập nhanh che nội dung trên màn hình nhỏ:** trên thiết bị rộng tối đa 600 px, thay bằng một nút “Công cụ học” có thể mở/thu gọn đủ 3 lối tắt, giữ nguyên 3 nút hiện ra trên desktop. Bổ sung ARIA cho hỗ trợ tiếp cận.
7. **Trang MathGeo Studio gần như mất toàn bộ bố cục nếu CDN Tailwind không tải được:** thêm tệp CSS dự phòng cục bộ, bảo toàn vùng danh mục, công cụ và canvas cả desktop/mobile; sửa viewport meta bị lặp.
8. **Bảng đo đạc che canvas trên điện thoại:** thêm nút thu gọn/mở bảng đo; các phép đo vẫn được giữ, bảng luôn hiển thị đầy đủ trên desktop.

## Kết quả kiểm thử sau sửa

- `pytest -q`: **129 đạt / 129**, không có bài thất bại (có 4 cảnh báo thư viện/khởi tạo cần theo dõi).
- Quét cú pháp: **549 trang HTML**, **1.067 khối JavaScript nhúng**, **32 tệp JavaScript riêng**: 0 lỗi cú pháp phát hiện được.
- Kiểm tra liên kết/tài nguyên nội bộ theo bộ test website: đạt.
- Kiểm tra khởi tạo bằng Chromium ở môi trường mô phỏng (token và phản hồi API giả): **19 trang chính + 529 trang game**, 0 lỗi JavaScript sau khi sửa `querySelector`. Sau khi bổ sung bảo vệ đăng nhập game, kiểm tra tĩnh tất cả 529 đường dẫn và chạy lại mẫu 129 trang game ở đầu/cuối danh mục: không có lỗi.
- Tương tác Chromium: kiểm tra mở/đóng lối tắt trên điện thoại, mở/đóng bảng đo MathGeo trên điện thoại; kích thước canvas và sidebar trên desktop: đều đạt.
- Có 8 kiểm thử hồi quy mới về đăng nhập trang game, Wi-Fi API/CORS, thứ tự Battle, chọn người thắng theo thời gian, và giao diện mobile.

## Giới hạn kiểm chứng và rủi ro còn lại

- Môi trường Chromium chặn điều hướng tới website chạy thật (`ERR_BLOCKED_BY_ADMINISTRATOR`). Kiểm thử DOM dùng HTML/CSS/JS thực tế nhưng cung cấp token và phản hồi API mô phỏng. Kiểm thử backend dùng TestClient trên SQLite thử, không phải server online và không phải thiết bị vật lý.
- Không thể chứng nhận 100% không có lỗi, bao gồm lỗi do mạng chập chờn, race condition dưới tải cao, dữ liệu lịch sử, sự khác biệt Android/iOS, canvas đa cảm ứng, hoặc lỗi ẩn trong hàng triệu câu hỏi AI.
- Kiểm định đáp án và sự độc lập toán học của hàng triệu câu hỏi **không nằm trong phạm vi bản sửa lỗi chức năng này**. Không tăng số lượng dạng/câu hỏi và không tuyên bố đã kiểm chứng toàn bộ ngân hàng.
- Việc chặn truy cập HTML ở phía trình duyệt là lớp điều hướng bổ sung, không thay thế xác thực ở API backend.
- Sau thay đổi token của bản trước, người dùng có thể cần đăng nhập lại. Trên thiết bị khác trong cùng mạng, backend phải chạy với `--host 0.0.0.0 --port 8000` và máy chủ phải cho phép kết nối cổng 8000 trong mạng nội bộ.

## Cách chạy và kiểm thử

1. Giải nén ZIP, vào thư mục chính `MATH_WEB_GITHUB_READY` (không mở thư mục lưu bản cũ bên trong).
2. Windows chạy `START_MATH_WEB.bat` (hoặc `CHAY_MATH_WEB.bat`). Truy cập `http://127.0.0.1:5500` và `http://127.0.0.1:8000/health`.
3. Chạy kiểm thử: `python -m pytest -q` khi đã cài `pytest`, `httpx` và thư viện backend.
4. Tạo 2 tài khoản thử để kiểm tra tìm Player ID, kết bạn, chat, lời mời Battle, câu hỏi và kết quả trong 2 tab trình duyệt. Thử trên điện thoại cùng Wi-Fi, xác nhận đúng địa chỉ IP máy chủ.
5. Với Admin, xác nhận tài khoản Admin và các quyền import, câu hỏi, học tập trước khi thay đổi database sản xuất. Luôn sao lưu database thật trước khi triển khai ZIP mới.

**Không đóng gói** SQLite sinh ra lúc chạy kiểm thử, khóa ký token, cache Python và file cấu hình bí mật. Mã khởi tạo tạo riêng database và khóa mới khi chạy lần đầu, hoặc sử dụng dữ liệu được khôi phục/sao lưu từ máy người dùng.
