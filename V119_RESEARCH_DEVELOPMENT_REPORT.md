# MATH_WEB V119 – Research batch: 10 problem types per topic

**Trạng thái:** Chưa hoàn thành mục tiêu 150 chủ đề × 10 dạng mới × 10 câu.

## Mục tiêu và kết quả đã thực hiện

| Chỉ tiêu | Mục tiêu đợt | Kết quả V119 |
|---|---:|---:|
| Chủ đề trong danh mục | 150 | 150 |
| Chủ đề được bổ sung đủ 10 dạng ứng viên V119 | 150 | 3 |
| Dạng toán ứng viên mới | 1.500 | 30 |
| Câu hỏi mới có đáp án, lời giải và kiểm định tính toán | 15.000 | 300 |
| Dạng được chứng nhận độc lập so với mọi dạng cũ | 1.500 | 0 |
| Dạng mới được phê duyệt công bố | 1.500 | 0 |

**Chủ đề đã được bổ sung 10 dạng ứng viên V119:**
1. Toán 10: Tập hợp và các phép toán (`tap_hop`).
2. Toán 11: Biến cố độc lập và xác suất có điều kiện (`bien_co_doc_lap_11`).
3. Toán 12: Số phức (`so_phuc`).

**Còn thiếu:** 1.470 dạng ứng viên cần viết và kiểm định cho 147 chủ đề chưa được bổ sung; chất lượng tính độc lập của cả 30 dạng đã tạo cũng cần chuyên gia so sánh với kho cũ.

## Các tính năng tích hợp

- Thêm module `backend/question_factory/v119_research.py` (30 bộ sinh, 10 đề/bộ), `v119_oracle.py` (bộ tính độc lập từ tham số) và `v119_audit.py`.
- Worker/engine nhận diện các dạng V119 qua ID, không sửa thiết kế Battle/tài khoản.
- CLI bổ sung `seed-v119`. Bộ điều phối đăng ký các dạng V119 theo cơ chế idempotent, giữ nguyên trạng thái `pending-expert-review`.
- Mỗi bộ có 2 câu trả lời ngắn, 2 trắc nghiệm, 2 đúng/sai, 2 tự luận ngắn và 2 câu vận dụng/thực tế.
- Có CSV theo dõi 150 chủ đề và 1.500 vị trí cần biên soạn, vị trí chưa có không được ghi thành câu hỏi đã tạo.

## Kiểm toán

- 300/300 bản ghi V119 được dựng lại xác định và kiểm tra đáp án bằng oracle riêng.
- Trong các tập dữ liệu nguồn 344.280 + 1.650 + 310 + 560 + 380 câu, **0 câu V119 trùng nguyên văn sau chuẩn hóa văn bản**.
- 0 chữ ký phương pháp trùng nguyên văn theo bộ so khớp, nhưng **14/30 dạng có cảnh báo gần giống dạng cũ trong cùng chủ đề**.
- 0 dòng JSON nguồn lỗi ở các tệp được kiểm tra.
- Không thể kết luận 300 câu không trùng về bản chất chỉ dựa trên câu chữ; chưa kiểm duyệt hoàn chỉnh về nội dung sư phạm.

## Kiểm thử

- 16/16 test mục tiêu đạt, gồm ca mới V119 và các test của V118/operations chạy lại.
- Một lần chạy hồi quy phạm vi rộng đã bị giới hạn thời gian trước khi hoàn tất, do đó **không khẳng định toàn bộ backend đã qua regression** tại V119.
- Đối chiếu file nguồn V118: không mất file nào, chỉ thay engine, storage, CLI, operations, một số bài test kỳ vọng số lượng phương pháp và cache chạy test. Đối chiếu trực tiếp 3.181 tệp gốc từ ZIP V118: không thiếu tệp nào, 3.175 tệp có checksum trùng khớp; chỉ có đúng 6 tệp mã nguồn và bài kiểm thử thay đổi có chủ đích. Cơ sở dữ liệu `mathweb.db`, ngân hàng câu hỏi 344.280 dòng, Battle, chat, tài khoản và giao diện không thay đổi.

## Cách chạy thử trên Windows (không cần GitHub)

Giải nén ZIP, mở PowerShell trong thư mục `MATH_WEB_GITHUB_READY\backend`:

```powershell
python -m question_factory.cli seed-v119
python -m question_factory.cli status
python -m pytest -q tests/test_question_factory_v119.py
```

Sử dụng `V119_RESEARCH/V119_NEW_QUESTIONS.jsonl` để xem 300 câu mẫu trước khi duyệt. **Không tự động duyệt các dạng ứng viên vào ngân hàng chính**. Các câu hỏi theo phương thức này có giá trị hỗ trợ nghiên cứu, không phải số dạng đã chứng nhận độc lập.

## Các tệp chính

- `V119_RESEARCH/V119_NEW_CANDIDATE_FORMS.jsonl`: danh sách 30 dạng.
- `V119_RESEARCH/V119_NEW_QUESTIONS.jsonl`: 300 câu có đáp án, lời giải.
- `V119_RESEARCH/V119_TOPIC_PROGRESS_150.csv`: tiến độ 150 chủ đề.
- `V119_RESEARCH/V119_REQUEST_1500_SLOTS.csv`: 1.500 vị trí yêu cầu, không điền giả vào chỗ trống.
- `V119_RESEARCH/V119_AUDIT_SUMMARY.json`, `V119_NEAR_METHOD_REVIEW.json`: báo cáo và cảnh báo.

**Kết luận:** V119 có 30 dạng toán ứng viên và 300 câu mới đã qua kiểm định đáp án. Chưa hoàn thành 1.500 dạng/15.000 câu. Không sử dụng đổi hệ số, đổi ID hoặc đổi hình thức làm bằng chứng tính độc lập.
