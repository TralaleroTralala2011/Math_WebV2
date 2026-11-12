# MATH_WEB V80 | Nâng hiệu suất sinh và kiểm tra dạng toán

**Mục tiêu mới:** 150 chủ đề × 2.000 dạng độc lập × 10 câu = 3.000.000 câu.

Bản này giữ nguyên toàn bộ dự án V79, bổ sung `tools/type_pipeline.py` để xử lý hàng loạt đặc tả dạng toán. Mỗi đặc tả được kiểm tra cấu trúc, 10 câu khác nhau, đáp án và lời giải không rỗng, phát hiện trùng chữ ký kiến thức/phương pháp/yêu cầu, rồi mới tạo mã ổn định.

Chạy từ thư mục gốc dự án:

```
python tools/type_pipeline.py audit backend/app/ai/verified_seed/verified_seed_bank.jsonl
python tools/type_pipeline.py build path/to/reviewed_specs.jsonl path/to/new_questions.jsonl
```

Dạng đầu vào JSONL cần các trường `grade`, `topic`, `type_key`, `mathematical_task`, `method`, `knowledge`, `reasoning_steps`, `questions` (đúng 10 phần tử, mỗi phần tử có `question`, `answer`, `solution`).

**Quan trọng:** kiểm tra chữ ký chỉ loại các trường hợp trùng hiển nhiên, không đủ chứng minh độc lập toán học. Mọi mã mới được đánh dấu `needs_independent_math_and_pedagogy_review`. Bản V80 chưa thêm 10.000 mã, chưa đạt 100% và chưa kiểm thử hồi quy giao diện, Battle hoặc Admin.
