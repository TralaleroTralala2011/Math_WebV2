# MATH_WEB V63 | Chặn câu hỏi sai chuyên đề trong game hình bình hành / hình thoi

## Nền tảng

Kế thừa trực tiếp `MATH_WEB_V62_WORD_DIRECT_150_TOPICS_INTEGRATED_20261115.zip`.
Không xóa/sửa file Word, ngân hàng SQLite gốc, dữ liệu tài khoản hay câu hỏi ở chủ đề khác.

## Lỗi đã chứng minh

Chủ đề lớp 10 `g10_geom_quadrilaterals_properties` bị lẫn câu hỏi về:
- Góc trong cùng phía của hai đường thẳng song song;
- Diện tích tam giác, định lý Pythagoras;
- Hai tam giác đồng dạng, tổng góc của tam giác.

Các hàng bị gắn sẵn mã chủ đề hình bình hành/hình thoi trong Word và V254.
Chỉ đối chiếu `topic_id` hay filename là **không đủ** để bảo đảm câu đúng nội dung.

| Nguồn | Số hàng gắn nhãn | Qua bộ lọc nội dung | Cách ly khỏi nguồn cấp đề của chủ đề này |
|---|---:|---:|---:|
| Word V62 | 634 | 93 | 541 |
| V254 dự phòng | 614 | 73 | 541 |

Các hàng ở hai nguồn có thể trùng nhau; **không** cộng hai nguồn thành số câu độc lập.
Các số trên chỉ cho biết tính phù hợp theo bộ quy tắc chủ đề có thể giải thích; **không** chứng nhận tính đúng toán học của đáp án.

## Bản vá

1. `backend/app/ai/engine/topic_relevance.py`: bộ kiểm tra nội dung theo kiến thức hình bình hành và hình thoi, loại tiêu chí hình học chung như `tam giác`, `góc`, `song song` khi không có quan hệ chủ đề.
2. `backend/app/ai/engine/word_source_v62.py`: lọc Word khi truy vấn, lấy thêm ứng viên để bù tỷ lệ câu sai nhãn, cập nhật số liệu khả dụng của chủ đề trong API.
3. `backend/app/ai/engine/service.py`: cùng bộ lọc áp dụng với Word, V59/V254, câu Admin, bộ sinh dự phòng và bài toán nhiều phần. Khi thiếu đề sẽ báo thiếu thay vì rút bài khác chủ đề.
4. `backend/app/ai/engine/geometry_curriculum.py`: mẫu bài toán riêng cho hình bình hành/hình thoi từ dễ tới khó: chu vi, diện tích, đường chéo, góc, tọa độ, định thức. Không đính kèm hình tam giác mặc định vào câu hình bình hành.
5. `js/game-question-bridge-v60.js`: lớp lọc bổ sung phía trình duyệt để đề sai chủ đề không lọt ra nếu backend Render còn đang chạy phiên bản cũ.
6. Ba trang game `games/knowledge/g10_geom_quadrilaterals_properties/*.html`: tăng phiên bản URL bộ nạp câu hỏi để tránh cache JS cũ.
7. `backend/tests/test_v63_quadrilateral_relevance.py`: kiểm thử tự động.

## Kiểm thử đã thực hiện

- `pytest` V63 và V62: **25/25 đạt**.
- `pytest` V59 và V61: **9/9 đạt**.
- Bộ cấp 10 câu không trùng, đúng chủ đề ở cả `easy`/`medium`/`hard`, với `multiple_choice`/`short_answer`/`mixed`: đạt lượt mô phỏng API.
- Kiểm thử JS giả lập kết quả trả về gồm hai câu sai chủ đề và một câu đúng chủ đề: loại đúng hai câu sai.
- Cú pháp JS/Python: đạt.
- Dữ liệu gốc: giữ nguyên byte từ V62.

## Giới hạn trung thực

Bản V63 **tập trung xử lý chuyên đề được báo lỗi**, không thể tự động bảo đảm toàn bộ 150 chuyên đề đã có phép kiểm định ngữ nghĩa đầy đủ. Các chuyên đề khác chưa thay đổi cách kiểm duyệt và có thể cũng tồn tại câu bị gắn nhầm. Quy tắc ngôn ngữ chỉ giúp phát hiện sự không khớp rõ ràng, không thay thế giáo viên kiểm chứng lời giải/đáp án và ngữ nghĩa.

Chưa thử hoạt động trực tiếp trên Render sau khi triển khai. Cần cập nhật backend V63 cùng với frontend V63. Nếu Render còn lỗi deploy, bản web đã cập nhật frontend sẽ chặn hai loại câu lạc đề này nhưng không thể nhận những câu sinh mới từ backend V63.
