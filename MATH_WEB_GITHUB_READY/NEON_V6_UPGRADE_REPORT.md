# MATH_WEB GITHUB READY · NEON V6 | Báo cáo nâng cấp 11/11/2026

## Nguồn và nguyên tắc

- Đã đọc ZIP người dùng gửi `Math_WebV2-main(2).zip` và đối chiếu với checkpoint **NEON V5** mới nhất đang có. ZIP người dùng là nền trước V5; các đường dẫn tệp có trong ZIP đều được giữ lại ở checkpoint V5. Vì vậy V6 phát triển trên **V5**, không quay lại mã cũ và không xóa các chức năng hiện hữu.
- Giao diện được thiết kế lại theo 5 ảnh tham chiếu người dùng cung cấp: nền navy rất tối, viền cyan phát sáng, dashboard thẻ bo góc, biểu đồ parabol, bảng quản trị nền sáng + sidebar xanh đậm. Không dùng ảnh chụp màn hình để giả lập giao diện hoạt động.
- Tên thư mục dự án trong ZIP: `MATH_WEB_GITHUB_READY`.

## Đã triển khai trong V6

1. **Bộ giao diện chung**: `css/neon-v6.css` và `js/neon-v6-experience.js`, áp dụng trên **19 trang học sinh/chức năng chính**; trang quản trị dùng cùng bảng màu nhưng bộ JS riêng. Thanh điều hướng desktop, menu gấp trên tablet, dock điện thoại; các trang vẫn giữ JavaScript nghiệp vụ cũ.
2. **Trang chủ**: thiết kế lại khu vực chào mừng, XP/cấp độ, lịch hoạt động (không tạo ngày học giả), đồ thị parabol, 5 chức năng nhanh, 3 thẻ tiến độ/gia sư/gợi ý. Vòng XP tính theo công thức XP cần để lên cấp `100 + level × 50` của backend, thay vì phần trăm giả.
3. **Học tập**: thiết kế lại theo mẫu ảnh thứ nhất với hero parabol, tiến độ, sáu nút Lý thuyết / Ví dụ / Video / FAQ / Bài tập / Kiểm tra, ba bảng kiểm tra 30 câu / kết quả / gia sư. Các nút chuyển đến tab và chức năng hiện có; bộ chọn lớp/chủ đề và nội dung gốc vẫn được giữ.
4. **Lộ trình học**: thiết kế lại màn hình chọn lớp 10–12, bảng mô tả đề, phân tích AI, banner khóa đầu vào; sau bài đầu vào hiển thị nhóm ba chủ đề đang mở, điểm cao nhất, đường tiến trình và liên kết bài học. Logic khóa vẫn do backend quyết định, không chỉ khóa nút trên trình duyệt.
5. **Admin**: giao diện xanh đậm + nền sáng, bổ sung lối vào Question Factory 2.0, bảng thống kê trạng thái ứng viên từ API thật. Chỉ trang Admin nạp `admin-neon-v6.js`; người học không có mục Admin trên menu chung. Backend tiếp tục kiểm tra token theo vai trò.
6. **Battle/Chat**: đồng bộ màu sắc, thẻ, nút, tiêu đề và bố cục theo phong cách mới, giữ nguyên các luồng WebSocket, ghép trận, kết bạn và lưu tin nhắn đã có từ V5. Không tự tuyên bố đã thử nghiệm trên hai thiết bị thật.
7. **Question Factory 2.0**: sửa một lỗi quan trọng: 10 câu của **cùng một dạng** có thể khác nhau về số liệu, nhưng trước đây bị từ chối vì bộ so trùng xóa hết số. Nay so trùng **câu hỏi** theo nội dung đầy đủ, trong khi so trùng **dạng toán** vẫn xét concept/phương pháp. Bổ sung kiểm tra đáp án Đúng/Sai.
8. **Bộ sinh có kiểm chứng đại số (phạm vi hẹp)**: nút Admin **“Sinh mẫu 1 dạng parabol · 10 câu”**, tạo đúng **một dạng ứng viên** “Tìm tọa độ đỉnh của parabol” với 10 câu trắc nghiệm có bốn phương án khác nhau, đáp án và lời giải chi tiết; kiểm tra lại kết quả bằng công thức tọa độ đỉnh. Không đếm thay số thành dạng mới, không tự duyệt, không tự đưa vào ngân hàng chính thức.
9. **Sửa HTML**: chuẩn hóa lại cấu trúc `learning-progress.html` và đưa vào bộ giao diện chung.

## Kết quả kiểm thử

- **156/156 bài pytest đạt** (150 bài cũ và 6 bài mới), bao gồm quyền Admin/học sinh, API kiểm tra đầu vào, khóa đề 30 câu, WebSocket, quy trình QF2, bộ sinh 10 câu và hợp đồng gắn CSS/JS cho các trang.
- `node --check` cho các tệp JavaScript mới/chỉnh sửa đạt.
- Dựng mockup DOM bằng Chromium/Playwright ở **1440 × 1000** và **390 × 844** cho Trang chủ, Học tập và Lộ trình: không có lỗi JavaScript và không có tràn ngang trong phép thử. Do môi trường chặn điều hướng localhost/file, đây **không phải** kiểm thử end-to-end đầy đủ trên trang thật.
- Không có chứng cứ để cam kết **100% không còn lỗi**. Battle/Chat trên hai thiết bị thật, tải đồng thời và toàn bộ trò chơi vẫn cần kiểm thử thực tế.

## Các giới hạn cần nói rõ

- Ngân hàng học liệu hiện có 150 chủ đề, nhưng chưa đủ **3–4 câu ở cả ba mức độ cho từng chủ đề**. Các đề đầu vào dùng câu hiện có và hiển thị cảnh báo độ phủ, chưa đạt tiêu chí đánh giá năng lực toàn diện như yêu cầu.
- Phần lớn chủ đề chưa có đủ **30 câu khác nhau được kiểm chứng** để mở bài thi chủ đề. API sẽ từ chối và báo số lượng thiếu, không sinh câu giả hoặc dùng câu chưa duyệt để lấp đủ.
- Gia sư hiện dùng cập nhật trạng thái thành thạo dựa trên câu trả lời đã chấm, **không phải** một mô hình ngôn ngữ được huấn luyện lại liên tục.
- Bộ sinh tự động mới hỗ trợ **một dạng parabol cụ thể**, không phải hệ thống sinh/kiểm chứng tổng quát cho 150 chủ đề. Việc phê duyệt vẫn yêu cầu Admin đối chiếu toán học độc lập.
- **529 trang game** vẫn giữ UI riêng ở lõi để không làm hỏng gameplay; V6 đồng bộ chủ yếu các trang chính và thành phần dùng chung, chưa tái thiết kế từng trò chơi theo pixel của ảnh.
- Các ảnh mẫu là ảnh tham chiếu thiết kế. Số người dùng, điểm số và thống kê trong ảnh mẫu **không được đưa vào website làm số liệu thật**.

## Cách chạy

1. Giải nén ZIP, mở `MATH_WEB_GITHUB_READY`.
2. Windows: chạy `START_MATH_WEB.bat` (yêu cầu Python và các thư viện trong `backend/requirements.txt`).
3. Hoặc chạy backend từ `backend`: `uvicorn app.main:app --host 127.0.0.1 --port 8000`; chạy frontend từ thư mục gốc: `python -m http.server 5500`.
4. Mở `http://localhost:5500/index.html`. Đăng nhập tài khoản học sinh để dùng Học tập/Lộ trình/Battle; Admin đăng nhập bằng tài khoản quản trị và mở `admin.html`.
5. Sao lưu cơ sở dữ liệu trước khi nâng cấp một website đang có dữ liệu thực. Không đóng gói database thử nghiệm hay mật khẩu.

**Kết luận:** V6 là bản nâng cấp giao diện và bổ sung một phần nghiệp vụ có kiểm thử, giữ các chức năng cũ; chưa đạt toàn bộ tiêu chí ngân hàng câu hỏi và kiểm thử thiết bị thật nên không được coi là bản hoàn thành 100%.
