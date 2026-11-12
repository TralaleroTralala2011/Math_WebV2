# MATH_WEB NEON V22 | Báo cáo kiểm toán và sửa lỗi

**Ngày:** 12/11/2026  
**Nguồn:** `MATH_WEB_GITHUB_READY_NEON_V21_MATHGEO_AI_TUTOR_2026-11-12.zip`.  
**Giới hạn phạm vi:** Không phá các chức năng đang vận hành; tập trung tính toàn vẹn AI gia sư, đề đầu vào và MathGeo Studio Pro trên điện thoại.

## Thay đổi có thật

1. **Không học lặp từ cùng mã câu hỏi:** Khi học sinh làm lại một câu đã chấm, hệ thống vẫn lưu sự kiện và điểm từng lượt, nhưng không cộng thêm vào số quan sát của Bayesian Knowledge Tracing. Một câu trước đó chỉ bỏ qua vẫn có thể đóng góp bằng chứng mới khi được trả lời ở lần sau. API chấm trả thêm `unique_new_answers`, `repeated_answers_excluded`.
2. **Câu bỏ qua là thiếu bằng chứng:** Phân tích đề cố định trả thêm `answered`, `answer_rate_percent`, `accuracy_among_answered`, `evidence_sufficient`; khoảng Wilson tính từ câu đã trả lời, không tính câu bỏ qua như sai. Điểm toàn bài theo đúng/sai/bỏ qua vẫn được giữ.
3. **Xếp lộ trình có căn cứ:** Chủ đề có đủ câu đã trả lời được ưu tiên theo sai/đúng; chủ đề chỉ bỏ qua được gắn nhãn chưa đủ bằng chứng, không bị xem là yếu chắc chắn. Giữ thứ tự chương trình khi thiếu dữ liệu.
4. **Lưu bản nháp không bị đảo thứ tự:** Frontend gửi các bản nháp tuần tự, gộp các chỉnh sửa phát sinh trong lúc đang lưu để giảm nguy cơ bản nháp cũ ghi đè bản mới.
5. **MathGeo di động:** Thu gọn bảng đo thành một nút, hỗ trợ thao tác bàn phím và giảm chuyển động; hướng dẫn tức thời theo công cụ Chọn/Điểm/Đoạn/Tròn/Kéo, không che phần lớn canvas. Giao diện máy tính giữ lại bộ công cụ đầy đủ.
6. **Giao diện kết quả:** Phân biệt rõ điểm trên toàn đề với độ chính xác của những câu đã trả lời; không diễn giải Wilson thành chứng nhận năng lực chuẩn hóa.

## Kiểm thử đã thực hiện

- Toàn bộ backend: **207 passed trong 33,11 giây** (`pytest -vv`, xem log kiểm thử phiên này). Kiểm thử lượng giác gồm 13 trường hợp đều đạt.
- 03 kiểm thử V22 mới: phân tích câu bỏ qua, chống học lặp, thứ tự ưu tiên chủ đề không nhầm bỏ qua với sai.
- Cú pháp JavaScript của các file sửa: `node --check` đạt.
- MathGeo với Chromium headless, HTML/CSS/JS được nạp nội tuyến vì môi trường chặn localhost: 390×844 và 1366×768, bảng công cụ mở/đóng, chọn Điểm, nội dung hướng dẫn đúng, không thấy lỗi JavaScript. Ảnh mô phỏng ở `V22_PREVIEW/`.
- ZIP được kiểm tra CRC sau khi đóng gói.

## Phần CHƯA được công nhận 100%

- Ba bộ đề cố định lớp 10–12 chưa đủ **1.350 câu đã được kiểm duyệt độc lập**: ma trận 441/459/450 chỉ là yêu cầu về số lượng và độ phủ, không phải câu đã được chứng nhận.
- Chưa có thử nghiệm tâm trắc trên mẫu học sinh đủ đại diện để xác nhận độ khó, độ phân biệt, độ tin cậy và công bằng.
- Mô hình BKT cập nhật xác suất cá nhân nhưng các tham số chưa được hiệu chuẩn thực tế; đây không phải mô hình ngôn ngữ tự huấn luyện.
- MathGeo chưa được kiểm thử trên thiết bị vật lý; Battle/Chat chưa được kiểm thử lại hai thiết bị thật trong phiên này.
- Giao diện toàn website chưa được kiểm tra so khớp từng trang với 5 ảnh mẫu.

## Dữ liệu & cập nhật

Sao lưu dữ liệu trước khi cập nhật. ZIP chỉ chứa mã nguồn, không đóng gói database người dùng và khóa HMAC. Các bảng SQLite bổ sung sẽ được tạo tự động khi backend khởi động. Không sao chép đè tệp cơ sở dữ liệu đang chạy.
