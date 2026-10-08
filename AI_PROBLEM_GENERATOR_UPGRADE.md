# MATH WEB AI Problem Generator

Đây là lớp mở rộng **chỉ thêm** lên Question Generator cũ.

## Không thay thế hệ thống cũ
- `/api/ai/questions` vẫn tạo câu hỏi như trước khi `problem_mode=false`.
- `/api/ai/practice/session` vẫn giữ hành vi cũ khi không bật problem mode.
- Toàn bộ `game_bank.py`, `template_bank.json`, composer, validator, distractor engine và QuestionGenerator cũ được giữ nguyên.

## Chế độ mới
Có thể bật `problem_mode=true` trong request:

```json
{
  "grade": 10,
  "topics": ["xac_suat"],
  "count": 3,
  "difficulty": "medium",
  "problem_mode": true,
  "problem_parts": 4
}
```

Mỗi bài có thể gồm 2–6 phần. Các phần được lưu riêng trong QuestionStore để hệ thống chấm điểm cũ vẫn dùng được.

## Các họ dạng bài
Kho archetype hiện có các cấu trúc như:
- dữ liệu bị thiếu
- bài toán ngược
- tình huống thực tế nhiều bước
- thí nghiệm → mô hình toán
- bảng dữ liệu → phân tích
- so sánh phương án
- điều kiện ẩn
- phát hiện lỗi
- thay đổi tham số
- tối ưu hóa
- lịch trình
- sản xuất/năng suất
- đo đạc hình học
- bản đồ tọa độ
- thí nghiệm xác suất
- thiết kế lựa chọn/tổ hợp
- tăng trưởng theo dãy
- mô hình hàm số
- khảo sát thống kê
- bài liên kết nhiều kiến thức

Các archetype là **khung sinh đề**, không phải văn bản sao chép từ SGK/SBT.

## Hình học
`geometry_diagrams.py` tạo mô tả hình học có tọa độ/kích thước. `practise.js` render mô tả đó thành SVG, nên hình được dựng từ chính dữ kiện của bài thay vì một hình minh họa cố định.

## Xen kẽ tự luận
Problem Generator chủ động trộn `short_answer` và `multiple_choice` giữa các phần. Vì vậy một bài có thể là:

`a) trắc nghiệm → b) tự luận → c) tự luận → d) trắc nghiệm`

và vẫn dùng cơ chế chấm đáp án/XP/feedback hiện tại.
