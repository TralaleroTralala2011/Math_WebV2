# MATH_WEB V62 — Kết nối ngân hàng trực tiếp từ 150 file Word

**Bản nền:** MATH_WEB V61 (`MATH_WEB_V61_WORD_TOPIC_MAPPING_FIXED_20261115.zip`).  
**Nguồn nhập:** đúng tệp `150_CHU_DE_WORD(1).zip` mà người dùng cung cấp.  
**SHA-256 của nguồn:** `1acfc64f91c51955a273dd2c01beb76784a13c7ab0667a24e0a30be6fe03aa9a`.  
File ZIP Word gốc đã có sẵn trong V61 có byte giống hệt file người dùng vừa tải lên. Không sửa nội dung Word gốc.

## Kết quả xuất dữ liệu

| Hạng mục | Số lượng |
|---|---:|
| File Word đầu vào | 150 |
| Chủ đề có dữ liệu (Toán 10/11/12) | 150/150 |
| Mục câu hỏi được nhận diện trong Word | 95.544 |
| Câu đưa vào SQLite có lọc cấu trúc và trùng nội dung | 91.026 |
| Câu trắc nghiệm 4 lựa chọn | 60.578 |
| Câu trả lời ngắn | 30.448 |
| Câu gắn nhãn `easy` | 13.797 |
| Câu gắn nhãn `medium` | 73.033 |
| Câu gắn nhãn `hard` | 4.196 |
| Bản ghi bị loại do phương án toán học tương đương | 2.439 |
| Bản ghi trùng nội dung trong 150 Word | 1.378 |
| Bản ghi trắc nghiệm không sử dụng được | 345 |
| Bản ghi thiếu trường/không hợp lệ về độ dài | 356 |

Lưu ý: `medium` là giá trị mặc định trong trường hợp Word không gắn nhãn mức độ theo khuôn mẫu được nhận diện. Các bản ghi là **ứng viên đã qua kiểm tra cấu trúc**, không được chứng nhận chính xác toán học độc lập toàn bộ. Không cộng 91.026 câu vào V254 như các câu độc lập mới, vì hai nguồn có nội dung giao nhau.

## Cấu trúc dữ liệu V62

- `question_bank_word_v62/`: **150 file JSONL**, một file ứng với một chủ đề, mỗi dòng có mã chủ đề thật, đề bài, đáp án, lời giải, loại câu, nguồn Word, số câu, trạng thái nhập và mã kiểm tra trùng. Có cả các dòng bị loại để kiểm toán, nhưng backend không phát các dòng này.
- `backend/app/ai/storage/v62_word_source.sqlite`: SQLite chỉ đọc, **91.026 câu có cấu trúc hợp lệ**, chỉ mục theo `(grade, topic, difficulty, question_type)`.
- `backend/app/ai/storage/v62_word_source.seed.zip`: bản khôi phục nén, kiểm tra SHA-256 trước khi sử dụng.
- `backend/app/ai/storage/v62_word_source_manifest.json`: số liệu, kiểm tra SHA-256, thống kê chủ đề.
- `scripts/build_word_source_bank_v62.py`: công cụ tái xuất dữ liệu từ file Word gốc theo **số thứ tự 001–150 và bảng ánh xạ V61**, không đoán mã chủ đề từ tên file không dấu.

## Luồng lấy câu hỏi

1. Trang web gọi backend `/api/ai/questions` hoặc `/api/ai/practice/session` với lớp, mã chủ đề, độ khó và hình thức trả lời.
2. Backend chuẩn hóa mã chủ đề, tìm ưu tiên trong `v62_word_source.sqlite` bằng đúng lớp/chủ đề/độ khó/loại câu. Nếu thiếu, giữ nguồn V59/V254 cũ làm dự phòng; không đổi sang chủ đề khác.
3. Câu được kiểm tra kiểu trả lời và trùng nội dung ở lớp backend trước khi đưa vào một lượt làm bài.
4. Battle sử dụng cùng hàm lấy ngân hàng, so trùng toàn bộ bộ đề trước khi gửi cho hai người chơi.
5. `/api/ai/bank/word/availability?grade=10&topic=ham_so` là điểm kiểm tra nguồn/công suất **không tiết lộ đáp án**.
6. Hệ thống nhiều phần `/api/ai/problems` có cấu trúc bài liên hoàn riêng: vẫn giữ hoạt động vốn có, không ép các câu Word đơn lẻ thành bài liên hoàn giả.

**Quan trọng:** Browser trên GitHub Pages không trực tiếp mở file Word/SQLite. Phần mềm backend (Render/FastAPI) mới là nơi đọc SQLite và trả về câu đúng chủ đề qua API.

## Kiểm thử đã thực hiện

- 150/150 file Word, 150/150 file JSONL, 150/150 mã chủ đề có bản ghi có thể sử dụng.
- Đối chiếu ID chủ đề/lớp với bản đồ V61; không phát sinh chủ đề thứ 151–153.
- So trùng theo nội dung chuẩn hóa: tất cả 91.026 bản ghi có `prompt_hash` không trùng trong ngân hàng Word V62.
- Cú pháp Python, CRC bản seed, hash của SQLite được kiểm tra.
- 20/20 bài kiểm thử hồi quy mới và cũ đã chọn đạt, gồm thử khôi phục ngân hàng từ seed khi SQLite gốc thiếu.
- Qua HTTP TestClient: `/api/ai/practice/session` và `/api/ai/questions` trả 10/10 câu khác nhau ở Hàm số lớp 10, Chia dư lớp 10, Dãy số lớp 11, Cực trị lớp 12. Battle trả 10 câu độc lập nội dung tại Dãy số lớp 11.

## Giới hạn và triển khai

- **Chưa** kiểm chứng toán học độc lập tất cả 91.026 câu. Một số câu Word có thể vẫn có đáp án/lời giải chưa chính xác, khác cách nhập hoặc phù hợp chấm tự luận ở mức hạn chế.
- **Chưa** thử hai tài khoản thật trên Render sau triển khai.
- Cần triển khai backend V62 lên Render (cả source và SQLite/seed đi kèm); frontend không cần cấu trúc mới và giữ nguyên từ V61.
- Không xóa/ghi đè database người dùng. Tập tin `backend/database/mathweb.db` trong bản V62 được khôi phục byte-for-byte từ V61 sau kiểm thử.
