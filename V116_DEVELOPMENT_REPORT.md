# MATH_WEB V116 · Báo cáo phát triển trung thực

Ngày: 08/11/2026  
Nền: `MATH_WEB_GITHUB_READY_V115_LOCAL_AUTOMATION.zip`

## Phạm vi

Tập trung vào mục tiêu ngắn hạn 150 × 500 × 10 = **75.000 dạng độc lập / 750.000 câu**. Không thay đổi các tính năng Battle, bạn bè, chat, tài khoản, giao diện hoặc ngân hàng gốc. Vẫn bảo toàn mục tiêu dài hạn 300.000 dạng/3.000.000 câu trong dashboard cũ, bổ sung chỉ tiêu **75.000/750.000** vào API tiến độ.

## Đã hoàn thành trong phiên

1. Bổ sung `backend/question_factory/v116_research.py` với 31 bộ dạng ứng viên thuộc 31 chủ đề Toán 10–12, bài mẫu có 5 kiểu trình bày.
2. Mỗi bộ tạo 10 câu, đáp án và lời giải. Nội dung mới có tổng **310 câu** với dữ liệu và dấu vết phép tính.
3. Tạo `backend/question_factory/v116_audit.py` để thống kê 150 chủ đề, so trùng nguyên văn với V113/V114 và ngân hàng cũ, không thổi phồng số dạng.
4. Nối engine và CLI/worker/điều phối để *đăng ký* 31 dạng ở trạng thái `pending`. Đưa vào `main` không đồng nghĩa xuất bản hoặc chấp nhận tính độc lập.
5. Bổ sung tiến độ ngắn hạn 500 dạng/chủ đề vào API và cơ chế lưu trạng thái mà không xóa mục tiêu 2.000 dạng/chủ đề lâu dài.
6. Bổ sung kiểm thử hồi quy, kiểm tra chống sửa đổi câu hỏi và chặn tự công bố.

## Kiểm toán dữ liệu

| Chỉ số | Số liệu |
| --- | ---: |
| Chủ đề trong catalog | 150 |
| Bộ dạng ứng viên V113 + V114 | 165 |
| Bộ dạng ứng viên V116 mới | 31 |
| Tổng bộ dạng ứng viên | 196 |
| Câu mẫu theo bộ dạng V113/V114/V116 | 1.960 |
| Câu V116 mới tính lại đáp án | 310 |
| Dòng câu hỏi ngân hàng cũ đã so trùng | 344.280 |
| Trùng nguyên văn giữa 310 câu mới với 1.650 câu ứng viên cũ | 0 |
| Trùng nguyên văn giữa 310 câu mới với 344.280 câu nguồn | 0 |
| Chủ đề có ít nhất một bộ dạng ứng viên | 150 |
| Chủ đề có bổ sung V116 | 31 |
| Chủ đề đạt 500 bộ dạng ứng viên | 0 |
| Bộ dạng đã chứng nhận độc lập toàn cục | 0 |

Số 196 là **bộ dạng ứng viên**, không phải số phương pháp được chứng nhận; số 1.960 chỉ là câu mẫu của hệ Question Factory, không phải toàn bộ ngân hàng câu hỏi cũ.

## Kiểm thử

- Nhóm `test_question_factory_v112.py`, `v113.py`, `v114.py`, `v116.py`, `test_question_factory_operations_v115.py`: **41/41 đạt**.
- Nhóm `test_verified_bank_api.py` + `test_verified_bank_quality.py`: **7/7 đạt**.
- Nhóm backend còn lại: **114/114 đạt**.
- Tổng số bài khác nhau: **162/162 đạt** (chạy theo ba nhóm, không tuyên bố một lệnh đơn đã chạy hết).
- Kiểm tra `test_question_factory_v116.py`, vận hành và V112 sau chỉnh sửa cuối: **28 đạt** (trùng với các test nằm trong 162, không cộng thêm).
- **Chưa** có kiểm thử trình duyệt, thiết bị thật, Docker production hoặc đánh giá giáo viên trên 310 câu.

## Bảo toàn

Đã so sánh file nguồn trong ZIP V115 với bản V116. Ngân hàng `verified_seed_bank.jsonl`, giao diện tài khoản, Battle, JavaScript Battle, CSS mobile không bị thay đổi. Cơ sở dữ liệu `backend/database/mathweb.db` được khôi phục đúng byte từ V115 sau khi chạy test (vì một số test làm thay đổi dữ liệu thử nghiệm). Nội dung phát triển chỉ tập trung trong `question_factory`, test và báo cáo.

## Giới hạn

**Chưa hoàn thành 500 dạng/chủ đề hoặc 750.000 câu**. 31 bộ mới chưa có bằng chứng so sánh đầy đủ với tất cả các phương pháp trong ngân hàng cũ hoặc đánh giá chuyên gia. Những dạng thuộc các chủ đề hẹp có thể không đủ 500 phương pháp độc lập trong phạm vi chương trình; không tạo biến thể giả để đạt số lượng.

Các đáp án/định dạng được xuất đầy đủ ở JSONL; đường API giao bài cũ chưa bảo toàn tất cả thuộc tính MCQ và đúng/sai, nên chưa được phép duyệt công bố bộ V116. Không có máy chủ 24/7 mới được triển khai.
