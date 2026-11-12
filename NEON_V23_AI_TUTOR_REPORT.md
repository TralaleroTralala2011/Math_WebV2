# MATH_WEB NEON V23 | AI gia sư học thích ứng theo bài làm

**Ngày:** 12/11/2026  
**Nguồn:** `MATH_WEB_GITHUB_READY_NEON_V22_EVIDENCE_MATHGEO_2026-11-12.zip`  
**Phạm vi:** Cá nhân hóa dựa trên bài làm được chấm và đã kiểm chứng. Giữ nguyên giao diện, MathGeo Studio Pro, Battle/Chat, Admin và các bộ sinh cũ.

## Thay đổi thực tế

1. **Chống thiên lệch do làm lại câu cũ ở khuyến nghị:** mô hình V22 không cập nhật xác suất hai lần, nhưng phần thống kê gợi ý còn tính trùng kết quả những lần làm lại. V23 tính hiệu quả **một bằng chứng trả lời đầu tiên cho mỗi mã câu**, kể cả nếu lần trước chỉ bỏ qua. Lịch sử bài làm giữ nguyên.
2. **API lộ trình thích ứng `GET /api/roadmap-v2/tutor-plan/{grade}`:** sau bài đầu vào cố định được duyệt, trả tối đa **3 chủ đề của chặng đang mở**, xếp chủ đề cần củng cố theo câu sai thực và mức bằng chứng. Không đưa chủ đề của chặng khóa vào đề xuất. Có `reason`, `focus_tier`, số câu đã đánh giá, độ tự tin giới hạn, và các bước học: lý thuyết, video, luyện tập, xem lại lời giải, kiểm tra 30 câu. Điều kiện mở chặng tiếp là **cả 3 chủ đề đạt tối thiểu 25/30**.
3. **Bảo vệ đề và dữ liệu:** yêu cầu đăng nhập học sinh, không công bố đáp án/giải thích của đề đầu vào cố định, không tin điểm do client tự gửi, không mở khóa bằng bài đầu vào thử, khóa kế hoạch nếu đề chính thức bị thu hồi. Thống kê và export chỉ trả dữ liệu của chính chủ tài khoản.
4. **Theo dõi hiệu quả học mô hình:** tách số lần nộp/ghi lịch sử (`training_events`) khỏi số câu thực sự đóng góp vào trạng thái BKT (`trained_answers`) và số mã câu có lịch sử (`unique_question_evidence`). Câu bỏ qua chỉ được ghi nhận, không tự hạ năng lực.
5. **Xuất hồ sơ riêng tư:** `GET /api/roadmap-v2/tutor-data/{grade}` có lịch sử đúng/sai/bỏ qua và trạng thái BKT theo chủ đề, độ khó của **chính học sinh**, không chứa nội dung đề, đáp án hay ID người dùng.
6. **Giao diện thích ứng trên máy tính và điện thoại:** nâng cấp `js/roadmap-v5.js`, tạo `css/neon-v23-ai-tutor.css`, hiển thị các bước luyện tập cá nhân và cập nhật sau khi nộp bài.

## Mô hình và giới hạn đo lường

- Phương pháp: **Bayesian Knowledge Tracing (BKT)** cập nhật online theo câu đã chấm trên máy chủ và được Admin duyệt. Không phải huấn luyện lại mô hình ngôn ngữ.
- Các xác suất slip/guess/learning vẫn là **tham số giả định**, chưa được hiệu chuẩn trên dữ liệu học sinh đại diện. Ước lượng mức thành thạo chỉ có giá trị hỗ trợ, **không phải chứng nhận năng lực khách quan toàn diện**.
- Khả năng xây dựng lộ trình chính thức phụ thuộc vào **đề đầu vào cố định** đã được giáo viên duyệt. Nếu đề chưa sẵn sàng, không mở lộ trình chính thức hoặc chế tạo số liệu học lực.
- Chỉ các bài kiểm tra thuộc `roadmap-v2` với câu đã duyệt được dùng học online. Dữ liệu Luyện tập/Battle chưa đủ thông tin kiểm chứng và **chưa được tự động đưa vào mô hình**.
- Chưa có cơ sở xác nhận đủ 1.350 câu đầu vào được duyệt, độ khó chuẩn hóa, tính công bằng tâm trắc hoặc kiểm thử trên người học thực tế.

## Kết quả kiểm thử thực hiện

- `python -m pytest -q -k 'not trig_generation'`: **198 passed, 13 deselected**.
- `python -m pytest -q tests/test_trig_generation.py`: **13 passed**.
- **Tổng 211/211 kiểm thử đã chạy đạt** (hai nhóm chạy riêng, không phải một lần chạy chung).
- Bổ sung 4 bài kiểm thử V23: lịch sử câu trùng/bỏ qua, cách ly tài khoản và khóa ba chủ đề, giao diện di động/cơ chế API, trường hợp nộp bài đầu vào thật cập nhật mô hình và lộ trình.
- `node --check js/roadmap-v5.js`: đạt.
- ZIP: kiểm tra CRC sau khi đóng gói.
- **Chưa** kiểm thử thiết bị vật lý hoặc đo độ chính xác dự đoán bằng dữ liệu học sinh thật.

## Cách sử dụng sau cập nhật

1. Sao lưu dữ liệu SQLite và cấu hình bí mật của bản đang chạy, **không ghi đè** chúng bằng tệp trong ZIP.
2. Giải nén bản V23 thay mã nguồn bản V22, giữ nguyên database người học.
3. Khởi động lại backend FastAPI và frontend; hệ thống tạo các bảng lộ trình nếu chưa tồn tại.
4. Đăng nhập bằng tài khoản học sinh, chọn khối 10/11/12 trên `learning-path.html`.
5. Khi Admin đã kiểm duyệt và công bố đề đầu vào chuẩn, nộp bài. Từ đó mô hình tự cập nhật sau mỗi bài kiểm tra được chấm, hiển thị ba chủ đề cần học và có nút xuất hồ sơ JSON.

**Không tuyên bố đã hoàn thành 100% các bộ đề hoặc độ chuẩn xác mô hình** khi chưa có đủ dữ liệu hiệu chuẩn và phê duyệt độc lập.
