# MATH_WEB: BÁO CÁO NÂNG CẤP GIAO DIỆN V5 + LỘ TRÌNH + QUESTION FACTORY 2.0

**Ngày kiểm tra:** 11/11/2026  
**Nền:** `MATH_WEB_GITHUB_READY_AUDIT_OPTIMIZED_ROUND4_2026-11-11.zip`  
**Phạm vi:** Các trang chính desktop/mobile, Admin tách biệt, API đánh giá năng lực, lộ trình, bài kiểm tra và chat thời gian thực.

## Những phần thực sự đã triển khai

1. **Giao diện dark navy / cyan đồng bộ:** bộ style `css/neon-v5.css`, thanh điều hướng dùng chung `js/neon-v5.js` cho 19 trang người học/tiện ích chính; trang Admin được thiết kế riêng với dashboard sáng và panel Question Factory. Trang chủ bổ sung XP, cấp độ, chuỗi học, các lối tắt, tiến độ lớp và gia sư. Responsive cho desktop/mobile. Giữ lại các đoạn nội dung và chức năng cũ thay vì xóa. Các trang trò chơi con giữ giao diện/logic gốc để tránh làm hỏng 529 game.
2. **Lộ trình học mới:** phải đăng nhập, chọn lớp 10/11/12, làm và nộp bài đầu vào để mở lộ trình. Server giữ khóa đáp án, chấm bài, lưu đáp án từng câu và trả kết quả theo đúng thứ tự câu. Xếp ba chủ đề đầu theo tỷ lệ cần ôn; các nhóm ba tiếp theo khóa ở cả frontend và backend cho tới khi ba chủ đề trước hoàn tất. Kiểm tra mỗi chủ đề đúng **30 câu khác nhau**, đạt **25/30** mới công nhận; hỗ trợ làm lại. Nếu thiếu 30 câu hợp lệ, API từ chối rõ ràng, không tạo câu giả.
3. **Gia sư thích ứng:** theo dõi đúng/sai/bỏ qua, khối lớp, chủ đề, nhãn độ khó, cập nhật xác suất thành thạo sau mỗi bài chấm và trả gợi ý ôn tập. Kết quả được lưu ở SQLite theo từng tài khoản, hỗ trợ xuất hồ sơ JSON qua giao diện. Đây **không phải mô hình ngôn ngữ được huấn luyện lại**.
4. **Question Factory 2.0:** API và UI chỉ cho Admin. Nhập ứng viên chứa tối thiểu 10 câu, mô tả phương pháp, điều kiện, điểm phân biệt; kiểm tra cấu trúc, trùng theo mẫu; xem chi tiết; duyệt hoặc từ chối bằng ghi chú và xác nhận thẩm định. Dạng được duyệt xuất bản 10+ câu vào `admin_question_bank`, sau đó có thể được dùng trong đề kiểm tra lộ trình. Không tự coi ứng viên, ID mới, câu AI thô là loại toán độc lập đã kiểm định. Quy trình **chưa có bộ sinh tự động tổng quát hay chứng minh toán học tự động**.
5. **Chat realtime:** thêm WebSocket có xác thực và kiểm tra quan hệ bạn bè, đẩy thông báo tin khi REST lưu xong; khôi phục kết nối theo cấp số nhân, nếu WS lỗi vẫn có thể dùng cơ chế tải tin cũ. Cần kiểm tra nhiều máy chủ/thiết bị thật trước khi triển khai quy mô lớn.
6. **Giữ tính năng cũ:** Battle, đăng nhập, bạn bè, quản trị, ngân hàng luyện tập, hình học, tài liệu và game không bị thay lõi logic trong lượt V5. Các bản sửa Round 4 vẫn được giữ nguyên.

## Độ phủ ngân hàng đề THỰC TẾ

| Lớp | Chủ đề | Có ≥1 câu | Đủ ≥3 câu ở mỗi 3 mức độ | Có ≥30 câu khác nhau |
|---|---:|---:|---:|---:|
| 10 | 49 | 49 | **0** | 1 |
| 11 | 51 | 51 | **0** | 0 |
| 12 | 50 | 50 | **0** | 0 |
| **Tổng** | **150** | **150** | **0** | **1** |

Các bài học hiện có tổng khoảng **1.009 câu ứng viên theo bộ lọc cú pháp**, nhiều câu không có nhãn độ khó. Số câu trên **không đồng nghĩa đã chứng minh đúng toán học**. Bài đầu vào có thể chạy với các câu hiện có ở đủ 150 chủ đề, nhưng **chưa đáp ứng 3–4 câu/mức × 3 mức cho tất cả các chủ đề**, nên chưa thể đánh giá năng lực toàn diện với chất lượng như yêu cầu. 149 trong 150 chủ đề hiện chưa có 30 câu hợp lệ để tổ chức bài thi 30 câu, cho tới khi bổ sung nội dung đã duyệt.

## Kiểm thử

- **150/150 bài kiểm thử pytest thành công** trên FastAPI TestClient, gồm bộ 144 bài cũ + 6 kiểm thử mới cho lộ trình, phân quyền, WebSocket chat và khâu duyệt/xuất bản QF2.
- Cú pháp của các JS sửa mới qua `node --check`; mô phỏng DOM và độ tràn ngang ở các trang trọng điểm tại chiều rộng **390 px và 1440 px** không phát hiện lỗi trong phép thử đó.
- **Chưa có** kiểm thử đầy đủ mọi thao tác trên trình duyệt thật, điện thoại thật hoặc Battle nhiều thiết bị thực; Chromium điều hướng localhost bị hạn chế trong môi trường kiểm tra. Vì vậy không thể cam kết 100% không còn lỗi.
- Không đóng gói database thử nghiệm, file secret, `__pycache__`, `.pytest_cache`, hay tệp môi trường phát sinh trong kiểm thử.

## Cách chạy

1. Giải nén ZIP, mở `MATH_WEB_GITHUB_READY`.
2. Chạy `START_MATH_WEB.bat` để khởi động backend + frontend (máy Windows), hoặc chạy từ thư mục `backend`: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` và từ thư mục gốc: `python -m http.server 5500`.
3. Mở `http://localhost:5500/index.html`.
4. Học sinh đăng nhập bằng tài khoản người học, chọn **Lộ trình học** và khối lớp. Admin đăng nhập riêng và mở `admin.html` để dùng Question Factory 2.0.
5. Khi tạo database mới, lấy thông tin Admin khởi tạo từ cửa sổ backend (đổi mật khẩu ngay). Với database hiện có, sao lưu trước khi thay bản.

## Việc cần làm để đạt đúng toàn bộ yêu cầu cuối

- Biên soạn và **kiểm chứng độc lập** tối thiểu 3–4 câu ở **mỗi mức × từng chủ đề** của từng lớp, cộng ngân hàng ít nhất 30 câu chất lượng cho **mỗi chủ đề**. Cơ chế kiểm tra mới chủ động chặn trường hợp thiếu dữ liệu.
- Xây dựng generator/solver toán học đáng tin, đối chiếu dạng độc lập bằng kiến thức chuyên môn, audit có bằng chứng. Nhãn QF2 approved hiện dựa trên xác nhận của quản trị viên, không phải bằng chứng toán học tự sinh.
- Bổ sung kiểm thử xuyên suốt trên thiết bị thật, bảo mật, tải đồng thời và WebSocket đa tiến trình (ví dụ qua Redis); nâng cấp học liệu video/FAQ của từng chủ đề và rà lại tính toán tương đương của đáp án tự luận phức tạp.
- Hoàn thiện giao diện phần **529 trang game** theo hệ thống theme mới sau khi có kiểm thử tương tác đầy đủ. Hiện giao diện phần trang chính được đồng bộ, game vẫn giữ theme gốc để tránh ảnh hưởng chức năng.

**Kết luận:** Đây là bản nâng cấp **một phần quan trọng và đã chạy kiểm thử**, không phải bản chứng nhận hoàn thành 100% các yêu cầu có độ phủ dữ liệu lớn. Mọi số liệu và tuyên bố về đã hoàn thành được ghi theo kiểm chứng thực tế.
