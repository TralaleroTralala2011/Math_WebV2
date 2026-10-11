# MATH WEB: bộ máy bài toán nhiều phần

Bản nâng cấp này bổ sung/sửa chế độ **Bài toán thực tế nhiều phần** mà không thay thế engine câu hỏi cũ hoặc thiết kế giao diện game cũ.

## Cách dùng trong website

1. Mở phần luyện tập AI trong trang `practise.html`.
2. Ở mục **Kiểu luyện tập**, chọn **🧩 Bài toán thực tế nhiều phần**.
3. Chọn số phần trong mỗi bài (3–6) và số bài toán muốn tạo.
4. Chọn lớp, chuyên đề và cấp kiến thức như trước rồi bắt đầu luyện tập.

Khi chọn chế độ này, trường số lượng đổi nhãn thành **Số bài toán** vì mỗi bài có nhiều phần a, b, c, d... Các phần cùng chia sẻ ngữ cảnh và dữ kiện; bài toán xác suất chọn học sinh có câu đếm số nhóm, xác suất cả nhóm thuộc một lớp, xác suất có đủ hai lớp và xác suất có điều kiện.

## API

- `POST /api/ai/problems`
- `POST /api/ai/questions` với `problem_mode: true`
- `POST /api/ai/practice/session` với `problem_mode: true`

Ví dụ phần thân yêu cầu:

```json
{
  "grade": 11,
  "topics": ["xac_suat_11"],
  "count": 2,
  "difficulty": "medium",
  "problem_mode": true,
  "problem_parts": 4
}
```

`count` trong chế độ bài toán là số **bài toán**, không phải số phần nhỏ. Kết quả có `problems` (các bài được nhóm) và `questions` (các phần phẳng để giao diện luyện tập cũ có thể tiếp tục chấm từng phần).

## Kiểm thử

Từ thư mục `backend`, chạy:

```bash
python -m unittest discover -s tests -v
```

Các bài test kiểm tra chuyên đề hiện có ở cả ba khối lớp, đủ trường dữ liệu cho từng phần, bốn lựa chọn trắc nghiệm không trùng nhau, và các phép đếm chính xác của bài toán xác suất có điều kiện.

## Phạm vi và giới hạn

Đây là bộ sinh theo cấu trúc và dữ kiện được tính toán bằng mã, không phải lời hứa rằng mọi đề sinh ra đã được thẩm định như đề thi chính thức. Cần tiếp tục mở rộng các mẫu theo từng chuyên đề và rà soát lời giải trước khi dùng làm ngân hàng đề chuẩn hóa. Các câu hỏi độc lập và các game cũ vẫn được giữ lại.
