# MATH_WEB NEON V25: AI gia sư có kiểm định bằng chứng dự đoán

**Ngày:** 12/11/2026. **Nguồn nâng cấp:** `MATH_WEB_GITHUB_READY_NEON_V24_TRAINABLE_AI_TUTOR_2026-11-12.zip`.

## Các thay đổi thực sự

1. Nâng mô hình cá nhân từ `online_personal_logistic_v1` lên `online_personal_logistic_v2_evidence_guard` trong `backend/app/learner_online.py`.
2. Dữ liệu học chỉ gồm câu đã kiểm duyệt, lần trả lời đầu tiên đã chấm, không tính câu bỏ qua hoặc trả lời lại; quy tắc của V24 được giữ nguyên.
3. Thêm **đánh giá dự đoán tuần tự theo thời gian** (prequential): sau 10 quan sát khởi động, dự đoán của mô hình được so với xác suất đúng trung bình được tính từ dữ liệu trước đó (baseline Laplace), sử dụng Brier score. Thống kê dự đoán được ghi trước khi nhìn đáp án.
4. Không công bố xác suất làm đúng tiếp theo nếu thiếu một trong các điều kiện: ít nhất 30 câu đã duyệt, ba chủ đề mỗi chủ đề >=3 câu, hai mức độ mỗi mức >=4 câu, có ít nhất 5 đúng và 5 sai, ít nhất 15 dự đoán sau giai đoạn khởi động, Brier cải thiện baseline tối thiểu 0,005 và thấp hơn 0,25.
5. Đối với **mỗi chủ đề riêng**, dự đoán theo mức chỉ được công bố nếu chủ đề có >=6 câu và >=2 mức độ mỗi mức >=2 câu. Dữ liệu một mức không được coi là bằng chứng đánh giá toàn diện chủ đề.
6. Các lý do "chưa đủ dữ liệu" được trả về trong API `online_training.readiness_reasons` và hiển thị ở giao diện Lộ trình học qua bảng thông tin mở rộng gọn cho cả điện thoại.
7. Sửa chọn mức ôn: nếu có >=2 câu đã được duyệt ở một mức với lỗi thực tế, ưu tiên tỷ lệ sai quan sát được để xác định mức ôn, thay vì xác suất dự báo chưa hiệu chuẩn. API công bố `focus_basis` và `observed_by_tier`; giao diện hiện giải thích vì sao ưu tiên mức đó.
8. Có kiểm tra khả năng tải trạng thái AI bị hỏng (không hữu hạn/thiếu trường). Hồ sơ V24 sẽ tự tái huấn luyện từ sự kiện bài làm đã lưu khi đọc lần đầu. Không xóa bài làm hay điểm của học sinh.

## Kiểm thử

- `python -m pytest -q --ignore=tests/test_trig_generation.py`: **210 passed**.
- `python -m pytest -q tests/test_trig_generation.py`: **13 passed**.
- **Tổng 223/223 kiểm thử đã chạy đạt**, thực hiện hai nhóm.
- `node --check js/roadmap-v5.js`: đạt.
- Kiểm thử mới: không phán đoán từ 100 câu một mức, đánh giá tiến về sau, phân biệt bằng chứng mỗi mức, bỏ qua/ứng viên/lặp, khôi phục trạng thái hỏng, kiểm thử UI, sửa ưu tiên mức độ từ lỗi thực tế thông qua HTTP.

## Giới hạn chưa hoàn thành

- AI logistic là mô hình dự đoán hỗ trợ học tập, **chưa hiệu chuẩn hoặc đánh giá độ công bằng trên tập học sinh đại diện**. Kiểm thử chương trình và Brier nội bộ không thay thế thử nghiệm thực tế.
- Vẫn **chưa có đủ ba bộ đề cố định lớp 10–12 với 1.350 câu được duyệt độc lập**; hệ thống giữ cơ chế không mở lộ trình chính thức khi thiếu đề hợp lệ.
- Câu cùng bản chất nhưng mang ID khác vẫn có thể làm thiên lệch phân tích; cần bổ sung metadata dạng toán được duyệt độc lập và quy trình kiểm tra tính tương đồng ngữ nghĩa.
- Chưa thử nghiệm Battle/Chat trên hai thiết bị vật lý hoặc xác nhận toàn bộ UI giống năm ảnh mẫu trong đợt này.
- Bản ZIP **không chứa database người dùng** và **không chứa khóa xác thực**. Sao lưu `backend/database/mathweb.db` và `backend/database/.mathweb_hmac_secret` trước khi ghi đè mã nguồn. Đừng xóa các tệp đó khi cập nhật.

## Tóm tắt trạng thái

- **Đã triển khai và kiểm thử:** mô hình huấn luyện theo bài đã chấm, bộ lọc chứng cứ, chất lượng dự đoán, gợi ý ôn theo mức sai đã quan sát và giao diện giải thích.
- **Chưa đủ căn cứ tuyên bố 100%:** đề đầu vào chuẩn hóa, hiệu chuẩn thực nghiệm, độ tin cậy và tính công bằng với học sinh thực tế.
