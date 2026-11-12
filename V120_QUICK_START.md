# V120 - BỔ SUNG 150 CHỦ ĐỀ × 1 DẠNG × 10 CÂU

**Gói này bảo toàn nguyên vẹn các tệp cũ của V119, chỉ thêm bộ tạo và bộ dữ liệu ứng viên V120.**

Mở thư mục `V120_RESEARCH` để xem:
1. `V120_1500_NEW_QUESTIONS.jsonl` (1.500 bài, đáp án, giải thích),
2. `V120_150_NEW_CANDIDATE_FORMS.jsonl` (150 mô tả dạng),
3. `V120_PROGRESS_150_TOPICS.csv` (bảng 150 chủ đề),
4. `V120_AUDIT_SUMMARY.json` (kiểm toán so trùng và thông tin xác minh).

Dạng ứng viên chưa được phê duyệt. Không được nhầm `150 mã dạng` với `150 phương pháp độc lập được thẩm định`.

Nếu muốn chạy kiểm thử trên máy tính:
```powershell
cd MATH_WEB_GITHUB_READY\backend
$env:PYTHONPATH = '.'
python -m pytest -q tests/test_question_factory_v120.py
```

Để cập nhật cơ sở dữ liệu Question Factory, chạy `python -m question_factory.operations --mode once --data-dir ./data_v120`; tác vụ này chỉ đăng ký ứng viên chưa duyệt, không chỉnh dữ liệu người dùng.
