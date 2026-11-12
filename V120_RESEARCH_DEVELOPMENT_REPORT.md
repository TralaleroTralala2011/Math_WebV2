# MATH_WEB V120: Mỗi chủ đề một dạng ứng viên, mỗi dạng 10 câu

Ngày bàn giao: 08/11/2026. Nguồn: ZIP `MATH_WEB_GITHUB_READY_V119_10_TYPES_PER_TOPIC_PROGRESS.zip`.

## Những gì đã tạo thực sự

- **150/150** mã chủ đề trong `backend/question_factory/catalog_150.json` đều được gắn **một bộ dạng ứng viên mới của V120**.
- **150 bộ dạng × 10 câu = 1.500 câu mới** trong `V120_RESEARCH/V120_1500_NEW_QUESTIONS.jsonl`.
- Mỗi dạng có mục tiêu/toán cụ thể, mô tả kiến thức, biểu thức kiểm tra đáp số, lời giải giải thích và 10 bộ dữ kiện không trùng trong dạng.
- Các định dạng được xuất: **300 trả lời ngắn**, **300 trắc nghiệm**, **300 đúng/sai**, **300 tự luận ngắn**, **276 vận dụng**, **24 bài có ngữ cảnh thực tế**.
- Mỗi câu trắc nghiệm có 4 đáp án và đúng 1 đáp án khớp biểu thức đáp số; câu đúng/sai đối chiếu nội dung nhận định.
- Cơ chế đăng ký V120 vào bảng `archetypes` của Question Factory và tích hợp `engine.generate/independently_verify`. Không tự phê duyệt hoặc đưa các dạng vào ngân hàng chính.

## Kiểm toán dữ liệu

- Tính toán biểu thức đáp án với SymPy và so khớp toàn bản ghi: **1.500/1.500** qua kiểm tra số học/cấu trúc.
- Đối chiếu nguyên văn sau chuẩn hóa với **347.480 bản ghi** của V119 và các phiên trước: **0 câu trùng nguyên văn**, **0 câu trùng nguyên văn trong V120**.
- **58 bộ dạng** được gắn cờ tương đồng tên hoặc chữ ký giải với ứng viên cũ. Đây là cảnh báo rà soát, không phải 58 dạng đã chứng minh trùng.
- **0 dạng mới được chứng nhận độc lập toàn hệ thống**. Đáp án tính đúng từ biểu thức tham số không thay thế việc thẩm định độc lập đề bài, giả thiết và lời giải bởi chuyên gia. Chưa có phép kiểm chứng độc lập hoàn toàn đối với mọi phát biểu trong ngôn ngữ tự nhiên.
- Dữ liệu V120 nằm ở trạng thái `pending-expert-review` và **chưa xuất bản**.

## Tổng tiến độ sau V120

| Chỉ tiêu | Thực có | Chú giải |
|---|---:|---|
| Chủ đề trong danh mục | 150 | Đủ danh mục |
| Bộ dạng ứng viên V113–V119 | 320 | Chưa chứng nhận độc lập toàn hệ thống |
| Bộ dạng ứng viên V120 | 150 | Đúng 1 bộ/mỗi chủ đề |
| Tổng bộ dạng ứng viên | 470 | Chưa phải 470 dạng độc lập được công nhận |
| Câu mẫu V120 | 1.500 | Kiểm tra biểu thức số học, chờ duyệt nội dung |
| Tổng câu mẫu ứng viên nếu tính mỗi dạng 10 câu | 4.700 | Không gồm ngân hàng cũ, chưa phải câu công bố |
| Mục tiêu dài hạn | 75.000 dạng × 10 = 750.000 câu | Chưa đạt |

## Kiểm thử trong phiên

- V120: **5/5 bài test đạt**.
- Hệ vận hành + V119: **11/11 đạt**.
- V118: **5/5 đạt**.
- V112/V113/V114/V116/V117, ngoại trừ `test_v117_audit_150_topic_gap`: **39/39 đạt**.
- **Tổng 60 bài test hoàn tất và đều đạt**. Một ca kiểm toán ngân hàng lớn của V117 không hoàn tất trong thời gian chạy, **không ghi là đã qua kiểm thử**.
- Không có kiểm thử browser/điện thoại thật hay triển khai Docker thực tế trong lần nâng cấp V120 này.

## Thay đổi mã nguồn

- Thêm `backend/question_factory/v120_specs.txt`: 150 đặc tả có phương pháp và đáp số.
- Thêm `backend/question_factory/v120_research.py`: sinh 10 câu/dạng, kiểm tra, xuất JSONL.
- Thêm `backend/question_factory/v120_audit.py`: rà soát dữ liệu cũ, chữ ký gần giống, báo cáo 150 chủ đề.
- Sửa `backend/question_factory/engine.py`, `storage.py`, `operations.py`: đăng ký và sử dụng các bộ tạo.
- Thêm `backend/tests/test_question_factory_v120.py`, điều chỉnh 3 tệp test cũ chỉ ở số lượng tổng ứng viên do V120 bổ sung 150.
- Không sửa route Battle, tài khoản, bạn bè, chat, notification hoặc giao diện web.

## Tệp kiểm toán

- `V120_RESEARCH/V120_150_NEW_CANDIDATE_FORMS.jsonl`
- `V120_RESEARCH/V120_1500_NEW_QUESTIONS.jsonl`
- `V120_RESEARCH/V120_PROGRESS_150_TOPICS.csv`
- `V120_RESEARCH/V120_POSSIBLE_METHOD_OVERLAPS.json`
- `V120_RESEARCH/V120_AUDIT_SUMMARY.json`
- `V120_RESEARCH/V120_QUESTION_COLLISIONS.json`

## Cách dùng

Tại thư mục `MATH_WEB_GITHUB_READY/backend`:

```bash
python -m question_factory.v120_audit --root .. --out ../V120_RESEARCH
python -m question_factory.operations --mode once --data-dir ./data_v120
PYTHONPATH=. pytest -q tests/test_question_factory_v120.py
```

Trên Windows PowerShell, đặt biến môi trường cho `pytest`: `$env:PYTHONPATH='.'`.

**Chỉ người thẩm định có quyền mới phê duyệt bộ dạng.** Hệ thống chủ đích không tự công bố 150 dạng này vào ngân hàng công khai.
