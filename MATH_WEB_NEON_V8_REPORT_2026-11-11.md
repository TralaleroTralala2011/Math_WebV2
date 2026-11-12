# MATH_WEB · NEON V8 (11/11/2026)

## Nguồn và cách đóng gói

Tiếp nối trực tiếp `MATH_WEB_GITHUB_READY_NEON_V7_UPGRADED_2026-11-11.zip`, bảo toàn thư mục `MATH_WEB_GITHUB_READY`, các trang, module tài khoản, bạn bè, chat, Battle, video, bài học, hình học, game và ngân hàng cũ. Không xây lại từ `Math_WebV2-main(2).zip` hay phiên bản V5/V6. File đã sửa chủ yếu là backend lộ trình, QF2 Admin, stylesheet UI và máy chủ frontend. Không thay thế 529 file HTML trò chơi hoặc thay đổi thuật toán game cũ.

**Bảo vệ dữ liệu:** Gói V8 *cố ý không đính kèm* `backend/database/mathweb.db` hoặc `backend/database/.mathweb_hmac_secret` phát sinh từ bản cài đặt thử. Hãy đọc `HUONG_DAN_CAP_NHAT_NEON_V8.txt` để chuyển dữ liệu từ bản đang dùng. Không gửi DB và khóa ký lên GitHub hoặc chia sẻ công khai.

## Đã triển khai và kiểm thử trong V8

1. **Lộ trình / câu hỏi được kiểm định:** Chỉ những câu học liệu được Admin duyệt độc lập hoặc QF2 đã chính thức xuất bản mới được sử dụng trong bài kiểm tra chủ đề 30 câu và để mở khóa đạt `25/30`. Câu học liệu chưa duyệt tiếp tục tồn tại dạng ứng viên nhưng không được tính như câu đã xác nhận. Nếu thiếu câu, API trả `409` và số câu đã duyệt thực tế, không bù bằng đề giả.
2. **Bài kiểm tra đầu vào:** Vẫn bắt buộc chọn lớp 10/11/12, bảo toàn 3 bộ đề theo lớp và kết quả được lưu theo tài khoản. Bổ sung metadata độ phủ: số câu đã duyệt, chưa duyệt, số câu theo mức và mức độ đầy đủ. Khi chưa có đủ 3 câu/mức cho toàn bộ chủ đề, giao diện và kết quả ghi rõ chỉ là **đánh giá sơ bộ**.
3. **Admin Question Factory 2.0:** API mới `/api/admin/qf2/coverage-detail` thống kê chi tiết 150 chủ đề, mỗi lớp, số câu đã duyệt, ứng viên, số còn thiếu cho ngưỡng 30 và cho ba mức độ. Chỉ Admin có quyền sử dụng. UI Admin có nút **Xuất kiểm định 150 chủ đề (JSON)**. Không cộng số ứng viên vào số dạng độc lập đã được kiểm chứng.
4. **NEON UI và responsive:** Thêm lớp `css/neon-v8.css` cho 20 trang chính, làm rõ trạng thái đã hoàn thành, đáp án đúng/sai/bỏ qua, touch target, focus, tương phản và card điện thoại. Tiếp tục dùng NEON V7 ở 529 trang game qua lớp CSS chung, không can thiệp sự kiện JS trò chơi.
5. **Bảo mật frontend:** Sửa `scripts/serve_frontend.py` chặn truy cập tệp `.db`, `.sqlite`, `.py`, key, file ẩn và các thư mục `backend`, `scripts`, `mathweb_work`. Chặn cho GET, HEAD và đường dẫn đã URL-encode; tắt directory listing. Giữ gzip/ETag cho HTML/JS/CSS công khai. Mặc định máy chủ chỉ bind `127.0.0.1`; LAN cần chọn chế độ riêng. Hai launcher phụ được đổi sang máy chủ an toàn.
6. **Bảo toàn các tính năng cũ:** Chat realtime WebSocket, Battle, AI gia sư thích ứng, kết bạn, thông báo, hình học và các công cụ quản trị vẫn ở bản V7. V8 không tự nhận đã chạy đầy đủ thử nghiệm 2 thiết bị vật lý hay đã huấn luyện lại LLM.

## Kết quả kiểm thử

- `python -m pytest -q backend/tests` từ thư mục backend: **169/169 passed**, trong đó 6 bài V8 kiểm tra xác thực, kiểm định câu, độ phủ, đầu vào, bảo vệ tệp và HTML/CSS.
- Kiểm tra tĩnh riêng: **549 HTML**, **1.098 đoạn/tệp JavaScript** qua `node --check`, **0 lỗi cú pháp** và **0 đường dẫn nội bộ thiếu** thuộc nhóm HTML/JS/CSS/asset được quét.
- Compile toàn backend Python: đạt.
- ZIP phát hành: được kiểm tra toàn vẹn bằng `ZipFile.testzip()`.
- Giới hạn: chưa kiểm thử UI pixel-perfect trên thiết bị vật lý, chưa đo benchmark nhiều người dùng/độ trễ internet, chưa thực hiện giao tiếp Battle với hai điện thoại thật.

## Độ phủ ngân hàng thực tế, chưa đủ 100%

- **150 chủ đề:** lớp 10 = 49, lớp 11 = 51, lớp 12 = 50.
- **0/150 chủ đề** đang có 30 câu **được duyệt độc lập** trong ngân hàng sử dụng cho bài kiểm tra chủ đề. Trước V8 có 1 chủ đề chứa ít nhất 30 câu *ứng viên*, không thể coi là 30 câu chuẩn.
- **0/150 chủ đề** có đủ tối thiểu 3 câu đã gắn nhãn kiểm định cho cả ba mức Nền tảng, Trung cấp, Nâng cao.
- Gói V7 có **9 dạng ứng viên × 10 câu = 90 câu** ở 3 chủ đề thuộc 3 khối. Không mặc nhiên coi đó là 9 dạng được duyệt hoặc nguồn bao phủ 150 chủ đề.
- AI gia sư hiện dùng ước lượng kiến thức từ bài đã chấm, **không phải huấn luyện lại mô hình ngôn ngữ**.

Do đó **không thể công bố yêu cầu 100% hoàn thành**. Cần mở rộng học liệu đã kiểm chứng và chạy end-to-end trên thiết bị thật trước khi tuyên bố như vậy.

## Ưu tiên V9

1. Kiểm chứng và duyệt có bằng chứng tối thiểu 9–12 câu/chủ đề cho bài đầu vào (3–4 câu ở từng mức), đủ 150 chủ đề; thiết kế câu mới đúng bản chất Toán.
2. Bổ sung và xác minh 30 câu duy nhất cho từng bài kiểm tra chủ đề; thử quy tắc 25/30 và mở nhóm ba chủ đề qua các tài khoản riêng.
3. Kiểm tra browser E2E desktop/iOS/Android, Battle hai người qua Wi-Fi và Internet, reconnect Chat, sao lưu/khôi phục dữ liệu thật.
4. Có cơ chế kiểm định toán học độc lập kết hợp máy kiểm tra đại số với người duyệt; benchmark tải trang và API, giám sát lỗi và hiệu năng.

## Cách chạy

Giải nén ZIP, sao lưu/di chuyển DB và khóa ký riêng theo hướng dẫn nội bộ rồi dùng `START_MATH_WEB.bat`; không dùng `python -m http.server` để phục vụ nguyên thư mục dự án có backend và dữ liệu tài khoản.
