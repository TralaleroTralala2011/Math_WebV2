# Hướng dẫn V118



Tại thư mục `MATH_WEB_GITHUB_READY/backend`:

```powershell
python -m pip install -r requirements-question-factory.txt
python -m pytest -q tests/test_question_factory_v118.py
python -m question_factory.cli --db .\v118_demo.sqlite3 init
python -m question_factory.cli --db .\v118_demo.sqlite3 seed-v118
python -m question_factory.cli --db .\v118_demo.sqlite3 status
python -m question_factory.v118_audit --root .. --output ..\V118_AUDIT
```

**Cảnh báo:** không chạy `approve-type` hàng loạt trước khi duyệt nội dung. Không nhập 380 câu vào Battle hay ngân hàng công khai nếu chưa qua review phương pháp và chất lượng câu hỏi.

