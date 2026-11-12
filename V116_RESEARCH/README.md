# MATH_WEB V116 · Nghiên cứu dạng toán theo mục tiêu 500/chủ đề

**Tình trạng:** kết quả có thể kiểm thử nhưng **chưa đạt 500 dạng/chủ đề** và **chưa chứng nhận độc lập phương pháp**.

## Mục tiêu được yêu cầu

- 150 chủ đề lớp 10–12.
- 500 dạng toán **độc lập** trên mỗi chủ đề, tức **75.000 dạng**.
- 10 câu khác nhau cho mỗi dạng, tức **750.000 câu**.
- Có các hình thức: trả lời ngắn, trắc nghiệm, đúng/sai, tự luận ngắn, vận dụng và bài toán thực tế khi phù hợp.
- Không coi thay số, đổi ký hiệu hoặc đổi hình thức trình bày là dạng mới.

## Kết quả thực tế trong V116

- Xây dựng **31 bộ dạng ứng viên mới**, ở 31 chủ đề, có tên mục tiêu toán học, chữ ký phương pháp, mức độ và **10 câu/bộ**.
- Tạo **310 câu mới**. 10 câu/bộ có cách hỏi luân phiên; các kết quả được tính lại bằng SymPy/thuật toán xác định và đi kèm lời giải.
- So trùng *nguyên văn* 310 câu mới với 1.650 câu ứng viên của V113/V114 và **344.280** câu nguồn hiện có: **0 trường hợp trùng nguyên văn**. Điều này **không chứng minh không trùng về dạng**.
- Tổng cộng **196 bộ dạng ứng viên** từ V113/V114/V116, có **1.960 câu mẫu**. **0 bộ dạng** đã được chứng nhận toàn cục là phương pháp độc lập.
- Trong 150 chủ đề, số bộ dạng ứng viên mỗi chủ đề hiện từ 1 đến 3, **không chủ đề nào đạt 500**.
- Tất cả V116 vẫn để ở trạng thái `pending-expert-review`, không tự đưa vào đề luyện tập hoặc Battle.

## File

- `V116_NEW_METHODS_PENDING_REVIEW.jsonl`: 31 phương pháp ứng viên, chưa chứng nhận độc lập.
- `V116_NEW_QUESTIONS_10_EACH.jsonl`: 310 câu, bao gồm các trường `question_type`, `options`, `correct_index` (nếu trắc nghiệm), `answer`, `solution`, `verification`.
- `V116_150_TOPIC_PROGRESS.json`: hiện trạng từng chủ đề, mục tiêu 500 và thiếu hụt.
- `V116_AUDIT_SUMMARY.json`: bản tóm tắt đếm, kiểm định và so trùng.

## Lấy lại kết quả, không cần GitHub

Trong thư mục `backend` (đã cài `requirements.txt` và `requirements-question-factory.txt`):

```powershell
python -m question_factory.v116_audit --out ../V116_RESEARCH --legacy app/ai/verified_seed/verified_seed_bank.jsonl
python -m pytest -q tests/test_question_factory_v116.py
```

**Đăng ký dạng vào cơ sở dữ liệu thử nghiệm (không duyệt, không công bố):**

```powershell
python -m question_factory.cli --db database/question_factory.sqlite3 seed-v116
python -m question_factory.cli --db database/question_factory.sqlite3 status
```

Bộ điều phối V115 đã bổ sung bước `seed_v116()` khi chạy lần tiếp theo. Các phương thức vẫn khóa chờ duyệt, tuyệt đối không tự duyệt hàng loạt.

## Hạn chế cần kiểm soát

1. Xác minh toán học bằng chương trình **không** bằng kiểm duyệt sư phạm hoặc chứng nhận phương pháp độc lập.
2. Hình thức đáp án trắc nghiệm/đúng-sai đầy đủ được lưu trong **JSONL V116**. CSDL và API gameplay cũ chưa được chuyển sang lưu/hiển thị đầy đủ trường lựa chọn/đúng-sai cho các bộ dạng mới. Không nên duyệt công bố V116 khi chưa nâng cấp đường dữ liệu này.
3. V116 dùng bộ sinh xác định cho 10 ví dụ/bộ, **không** phải AI tự nghiên cứu ra 75.000 dạng.
4. 344.280 câu ngân hàng cũ không được coi là 344.280 câu đã chứng nhận toàn diện.
5. Không có triển khai VPS hoặc sản xuất online mới trong phiên này.

## Nguồn tham khảo về phạm vi và loại bài tập

- [Chương trình giáo dục phổ thông, Thông tư 32/2018/TT-BGDĐT](https://vbpl.moj.gov.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=146721)
- [OpenStax, Algebra and Trigonometry 2e](https://openstax.org/books/algebra-and-trigonometry-2e/pages/preface)
- [Khan Academy, Math](https://www.khanacademy.org/math)

Các nguồn được dùng làm khung tham chiếu về **nhóm kiến thức** và **loại nhiệm vụ**. Câu hỏi ví dụ V116 được viết lại riêng, không trích nguyên văn bài tập có bản quyền.
