# MATH_WEB V123 | Ngân hàng dạng toán nghiên cứu

## Kết quả của đợt mở rộng

- 150 chủ đề (danh mục `catalog_150.json`).
- 1.050 **cấu trúc ứng viên tổng hợp**: 7 mục tiêu xử lý trên đáp án từ một bài toán nguồn ở mỗi chủ đề, gồm biến thiên, tổng, cực đại, trung vị, sai phân bậc hai, đếm vượt ngưỡng và phương sai (riêng logarit dùng độ rộng khoảng biến thiên thay phương sai để tránh phép rút gọn tốn kém).
- 10.500 câu hỏi và lời giải, 10 câu trên mỗi cấu trúc ứng viên. Dạng hiển thị: trả lời ngắn, trắc nghiệm, đúng/sai, tự luận ngắn, vận dụng.
- 0 câu hỏi trùng nguyên văn trong lô; 0 câu trùng nguyên văn với các tập cũ đã quét (không phải đánh giá trùng phương pháp).
- Kiểm tra lại phép tính toán học/nhất quán dữ liệu với kiểm tra toán tử: 10.500/10.500. Kết quả số học của bài nguồn thừa hưởng từ V121, không có xác minh sư phạm độc lập cho từng bài nguồn.

## Lưu ý bắt buộc về tính độc lập

**1.050 KHÔNG phải 1.050 phương pháp toán học độc lập**: các cấu trúc tổng hợp này tái sử dụng đúng 150 phương pháp nguồn V121 và 7 phép xử lý bổ sung. Tất cả đang bị gắn cờ `shared_core_method=true`, `independence_certified=false`, `concept_reuse_risk=high`.

Các bài có thể hợp lệ về số học nhưng chưa phù hợp hoàn toàn với mục tiêu kiến thức từng chuyên đề. Đặc biệt phép tổng hợp/so sánh số liệu có thể mang yếu tố liên chủ đề. Phải duyệt chuyên môn và đối chiếu ngữ nghĩa trước khi công nhận là dạng toán mới hoặc công bố cho học sinh.

**Số dạng toán độc lập được chứng nhận mới: 0.** Không cộng 1.050 vào tiến độ 300.000 dạng độc lập.

## Tích hợp và bảo toàn

- Giữ nguyên bản V122 ở các phần Battle, tài khoản, chat, kết bạn, MathGeo, Học tập và giao diện.
- Bổ sung `question_factory/v123_research.py`, routing engine và `seed_v123`.
- Đăng ký ứng viên theo cơ chế opt-in: đặt `QF_ENABLE_V123_CANDIDATES=1`. Đăng ký chỉ thêm bản ghi ở trạng thái `pending`, không tự phê duyệt, không tự đăng hàng loạt.
- Thêm kiểm thử `backend/tests/test_v123_research.py` cho số lượng, định dạng, kiểm định phép tính, chống sửa dữ liệu, và chặn tự xuất bản.

## Kiểm thử đã thực hiện

- 10.500 phép kiểm tra tại lúc xuất câu hỏi.
- Bộ kiểm thử V123 + operations: `11 passed`.
- Bộ thử tích hợp rộng với V121/V122 đã chạm giới hạn thời gian, không được xem như vượt qua.
- Chưa kiểm thử Docker chạy thật, UI thiết bị thật hoặc chạy production.

## Lệnh kiểm tra

```bash
cd MATH_WEB_GITHUB_READY/backend
python -m pytest -q tests/test_v123_research.py tests/test_question_factory_operations_v115.py
```

Các bộ dạng đã tạo đều ở trạng thái chờ duyệt. Mục tiêu cuối 150×2.000×10 vẫn chưa đạt.
