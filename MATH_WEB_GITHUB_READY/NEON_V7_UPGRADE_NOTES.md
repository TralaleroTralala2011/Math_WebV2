# MATH_WEB · NEON V7 (11/11/2026)

## Nguồn

Tiếp tục trực tiếp từ `MATH_WEB_GITHUB_READY_NEON_V6_UPGRADED_2026-11-11.zip`. Giữ toàn bộ tệp V6, bao gồm mã nguồn nghiệp vụ, dữ liệu và thư mục dự phòng; không sử dụng bản GitHub cũ thay thế V6. Nên sao lưu database trước khi thay thế trên máy đang sử dụng.

## Đã bổ sung trong V7

- **529 trang game đang hoạt động** (`games/**.html`) dùng lớp giao diện NEON V7: nền navy, cyan, viền sáng, thanh điều hướng chung, menu gọn cho điện thoại; giữ mã chơi game và sự kiện cũ. Thanh điều hướng mới dùng Shadow DOM để không xung đột CSS/JS trò chơi.
- **20 trang chính** có CSS V7 bổ sung khả năng truy cập, focus, bố cục mobile và giữ thiết kế V6 từ 5 hình tham chiếu. Trang Admin vẫn có JavaScript và điều hướng riêng, không xuất hiện trong menu học sinh.
- **Trang chủ** kết nối API thật cho tên/XP/cấp độ, chuỗi học tập, lịch sử hoạt động 84 ngày, tiến độ đạt ≥25/30 theo khối lớp, gợi ý từ lịch sử làm bài. Không hiển thị ngày học hoặc KPI giả; nếu chưa đăng nhập không hiện tên/XP lưu từ tài khoản trước.
- **Question Factory 2.0** có 9 bộ sinh công thức hữu hạn (3 khối lớp, 3 chủ đề, 9 dạng ứng viên, 90 bài): tọa độ đỉnh, giá trị hàm số bậc hai, số nghiệm bậc hai, số hạng/tổng/công sai của cấp số cộng, cộng/nhân/môđun số phức. Từng câu có đáp án, lời giải và mức độ đề xuất; 8 dạng mới dùng 7 trắc nghiệm, 2 tự luận, 1 đúng/sai trên 10 câu. Chỉ sinh **ứng viên**, không tự duyệt hay cộng vào số dạng đã kiểm chứng.
- **Admin kiểm định học liệu**: xem câu gốc, phương án, đáp án, lời giải; xác nhận kiểm tra độc lập, phân loại Nền tảng/Trung cấp/Nâng cao hoặc từ chối câu sai. Hệ thống gắn dấu vân tay nội dung để tự vô hiệu hóa nhãn cũ khi đề/đáp án/lời giải thay đổi. Câu bị từ chối không vào đề mới.
- **Lộ trình học**: bài đầu vào lưu bản nháp theo tài khoản trên backend và khôi phục khi tải lại; chỉ chấm khi nộp; cải thiện kiểm tra tương đương phân số, số phức dạng a+bi và đúng/sai. Giữ quy tắc chọn lớp, bắt buộc kiểm tra, nhóm 3 chủ đề, bài 30 câu, ≥25/30, xem lại thứ tự câu.
- **Chat**: bổ sung heartbeat ping/pong và tự mở lại WebSocket khi quay về tab; polling REST vẫn dự phòng. Battle giữ luồng đồng bộ/reconnect từ V6.
- **Hiệu năng**: giảm truy vấn SQLite lặp lại khi thống kê độ phủ ngân hàng 150 chủ đề bằng tải câu được duyệt và nhãn review theo khối lớp một lần.

## Kiểm thử

- `python -m pytest -q backend/tests`: **163/163 đạt**.
- `node --check`: các tệp JS mới và thay đổi đạt.
- `python -m compileall -q backend/app`: đạt.
- Mô phỏng tĩnh Chromium cho một trang game ở **1440×900** và **390×844**: không có lỗi JS, không tràn ngang; menu mobile mở được.
- Thử nghiệm E2E bằng Chromium với `localhost` bị môi trường chặn (`ERR_BLOCKED_BY_ADMINISTRATOR`), nên **chưa** chứng nhận tương tác thực tế hai thiết bị, tất cả game và Battle/Chat đa máy.

## Giới hạn thực tế còn tồn tại

- Chỉ **3/150 chủ đề** hiện có bộ sinh công thức bổ sung. 9 dạng × 10 câu đều đang là ứng viên và cần Admin phê duyệt, chưa tự động xuất bản.
- **0/150 chủ đề** đang đáp ứng đầy đủ yêu cầu tối thiểu 3 câu đã gắn nhãn xác nhận ở mỗi mức. Ngân hàng hiện có 150 chủ đề nhưng nhiều câu chưa được kiểm định và có chủ đề chỉ có 1 câu; không thể chứng nhận đề đầu vào 3–4 câu/mức cho tất cả chủ đề.
- **1/150 chủ đề** có ít nhất 30 câu trong kho học liệu hiện tại, nhưng số lượng không đồng nghĩa 30 câu đã được xác minh độc lập. Bộ đề 30 câu chỉ mở khi đủ số câu hợp lệ; thiếu thì báo rõ.
- Gia sư cá nhân dùng cập nhật Bayes từ câu đã chấm, **không** huấn luyện lại mô hình ngôn ngữ AI.
- Không cam kết website không còn lỗi hay đáp ứng 100% yêu cầu khi chưa có kiểm định đủ 150 chủ đề và kiểm thử trên thiết bị thật.

## Chạy

Giải nén ZIP, mở thư mục `MATH_WEB_GITHUB_READY`, chạy `START_MATH_WEB.bat`. Hoặc chạy backend trong `backend` với `uvicorn app.main:app --host 0.0.0.0 --port 8000`, frontend tại thư mục gốc với `python -m http.server 5500`, rồi mở `http://localhost:5500`.

**Lưu ý bảo mật:** Admin được xác thực theo vai trò trên API. Không nhập token/mật khẩu vào mã nguồn. Sao lưu database và kiểm tra phân quyền trước khi triển khai công khai.
