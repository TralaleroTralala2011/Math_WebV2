# MATH_WEB: Báo cáo quét toàn site và khắc phục lỗi

**Nguồn:** ZIP `Math_WebV2-main(1).zip` do người dùng gửi ngày 10/11/2026. Mọi chỉnh sửa áp dụng trên bản nguồn đó, không ghép ngược các ZIP cũ.

## Kết quả và phương pháp

- Quét **549 tệp HTML ở website gốc và danh mục game**.
- Kiểm tra cú pháp **1.067 khối JavaScript nhúng** bằng Node.js: không phát hiện lỗi cú pháp trong kiểm tra cuối.
- Kiểm tra **2.338 đường dẫn tài nguyên và liên kết nội bộ**: không còn liên kết tới tệp thiếu trong kiểm tra cuối.
- Kiểm tra cú pháp các tệp JS riêng biệt và biên dịch Python: đạt.
- Chạy kiểm thử API FastAPI + SQLite ở database thử riêng, bao gồm đăng ký/đăng nhập, tìm Player ID, kết bạn, chat, lời mời Battle, ghép ngẫu nhiên, chấm đáp án, quyền Admin, import câu hỏi, học tập, hình học, phân loại chủ đề, chống trùng và kiểm định ngân hàng.

## Những lỗi đã sửa

1. **121 trang game hình học/kiến thức bị hỏng cấu trúc HTML/JavaScript** sau thao tác chèn metadata, có trang mất thẻ `script`, có trang nhét JSON vào `src`, có trang làm hỏng phần đầu của engine. Đã phục hồi đúng footer, script nạp cấu hình API, metadata `window.MATH_GAME`, và phần đầu engine. Giữ nguyên nội dung đề và mã xử lý câu hỏi phía sau. Gồm 31 trang dạng lỗi thứ nhất và 90 trang dạng lỗi khác.
2. Liên kết `games.html` không có thật trong `learn.html` đổi sang trang luyện tập hiện có.
3. **Bài kiểm thử quality gate** dùng dữ liệu mẫu thiếu `skill_id` và xác nhận bám chủ đề, làm báo sai 31 lỗi thay vì 1 lỗi. Đã cập nhật fixture đúng quy tắc mới, không hạ tiêu chuẩn audit.
4. **Khóa ký token cố định công khai** thay bằng khóa riêng cho từng bản cài đặt, lưu cục bộ ngoài Git, hoặc khóa mạnh do quản trị cấu hình qua môi trường.
5. **Mật khẩu Admin mới khởi tạo cố định** đã bị loại bỏ. DB đã có tài khoản Admin giữ nguyên mật khẩu cũ để tránh mất quyền truy cập; với DB mới, dùng mật khẩu do quản trị cấu hình hoặc mật khẩu mạnh ngẫu nhiên được in một lần ở terminal backend.
6. **Khởi tạo database cũ có thể tái tạo và đặt lại mật khẩu Admin mặc định ở mỗi lần chạy**. Đã bỏ logic tạo/reset Admin trong `database.database`; quyền quản trị chỉ do `admin_routes` quản lý, tài khoản cũ được di chuyển một lần mà không đổi mật khẩu. Kiểm thử riêng xác nhận mật khẩu sau khi thay đổi không bị reset khi khởi tạo database lại.
7. **WebSocket Battle không đi cùng cơ sở dữ liệu trận đang chơi**, đồng thời thiếu kiểm tra quyền người tham gia. Đã bổ sung token, đối chiếu user và thành viên trận từ DB, trả trạng thái/trận từ server, không tin số liệu chấm điểm từ client; hỗ trợ fallback polling HTTP cũ.
8. **Đăng xuất server không thu hồi token**. Đã tăng `auth_version` khi đăng xuất thường và Admin; sửa các nút đăng xuất chính để gửi yêu cầu thu hồi phiên bằng `keepalive` trước khi chuyển trang.
9. Chặn việc thay đổi API đích bằng `?api=` qua URL ở website công khai, giảm rủi ro rò rỉ token; giữ lựa chọn API local cho phát triển.
10. Đồng bộ chặn truy cập chưa đăng nhập cho các trang học tập, vẽ hình, công cụ học tập mà trước đó có thể mở qua URL; giữ `trial-practise.html` cho chế độ thử nghiệm riêng.
11. Thêm hồi quy tự động cho cấu trúc trang game, liên kết tài nguyên, quyền trang, token đăng xuất, WebSocket Battle và quyền Admin, giúp tránh tái xuất hiện lỗi.

## Giới hạn kiểm chứng

- **Không thể khẳng định website không còn 100% lỗi.** Các kiểm thử API được chạy trong môi trường mô phỏng độc lập; không thay thế cho kiểm thử tải thật và dữ liệu người dùng ở máy chủ triển khai.
- Trình duyệt Chromium tại môi trường kiểm thử trả `ERR_BLOCKED_BY_ADMINISTRATOR` cho điều hướng, kể cả trang nội bộ và `data:`. Do đó không thể thực hiện/quan sát trực tiếp từng click, pixel layout, thao tác cảm ứng, canvas SVG và WebSocket chạy bằng trình duyệt thật; giao diện desktop/mobile được rà soát tĩnh, chưa chứng nhận hiển thị chính xác bằng ảnh chụp.
- Kết quả test không chứng nhận đáp án của toàn bộ câu hỏi do AI sinh; việc kiểm định hàng triệu câu và dạng toán độc lập cần quy trình toán học riêng.
- Các thư mục lưu phiên bản cũ `MATH_WEB/` và `mathweb_work/` được giữ nguyên như ZIP nguồn để bảo toàn dữ liệu. **Trang hoạt động chính là tại thư mục gốc `MATH_WEB_GITHUB_READY`**, không chạy bản sao cũ bên trong.
- Sau nâng cấp hệ thống ký token, phiên đăng nhập cũ cần đăng nhập lại. Với database cũ đang dùng mật khẩu Admin không an toàn, chủ hệ thống cần đổi mật khẩu Admin ngay.

## Hướng dẫn chạy

1. Giải nén ZIP, mở **thư mục gốc** `MATH_WEB_GITHUB_READY`.
2. Windows chạy `START_MATH_WEB.bat` hoặc `CHAY_MATH_WEB.bat`. Để kiểm thử thủ công, mở `http://127.0.0.1:5500/` và `http://127.0.0.1:8000/health`.
3. Tạo hai tài khoản test để kiểm tra tìm Player ID, kết bạn, chat, gửi/nhận lời mời, Battle ở hai cửa sổ/thiết bị; đăng nhập Admin và kiểm tra dữ liệu học tập, ngân hàng, đổi mật khẩu; trên điện thoại thử thao tác chạm, vẽ, cuộn và chuyển màn hình.
4. Kiểm thử hồi quy bằng `python -m pytest -q` tại thư mục gốc.

**Nguyên tắc:** Báo cáo chỉ công nhận lỗi đã sửa khi mã đã thay đổi và kiểm thử xác nhận. Không tuyên bố hoàn thành tuyệt đối hay bổ sung ngân hàng câu hỏi nếu chưa làm.
