# MATH_WEB V118: Báo cáo nâng cấp ngân hàng 500 dạng/chủ đề

Ngày 08/11/2026. Nền dự án: `MATH_WEB_GITHUB_READY_V117_RESEARCH_500_TARGET.zip`.

## Mục tiêu bắt buộc

- 150 chủ đề × 500 dạng toán độc lập = **75.000 dạng**.
- Mỗi dạng 10 câu riêng có đáp án và lời giải = **750.000 câu**.
- Không tính dạng mới khi chỉ thay số, cách diễn đạt, tên biến, kiểu câu hay `form_id`.

## Công việc hoàn thành V118

1. Nghiên cứu và triển khai **38 bộ dạng ứng viên mới**: lớp 10 có 12, lớp 11 có 12, lớp 12 có 14.
2. Tạo **380 câu** từ 38 bộ dạng, đủ 10 dữ kiện khác nhau mỗi dạng, phân bố các kiểu trả lời ngắn, trắc nghiệm, đúng/sai, tự luận ngắn, vận dụng, một số bài toán thực tế.
3. Bổ sung bộ kiểm tra đáp án tính **từ tham số độc lập** (`v118_oracle.py`), không chỉ lặp lại cùng công thức sinh đề; có 5 bài test mới cho Question Factory.
4. Tích hợp bộ tạo vào `engine.py`, `storage.py`, `operations.py`, CLI `seed-v118`; **mặc định toàn bộ ở trạng thái pending**, không tự duyệt hoặc nhập vào ngân hàng công khai.
5. Kiểm toán xuyên kho đã đọc **346.800 bản ghi** (344.280 từ ngân hàng cũ + 1.650 + 310 + 560). Không có dòng JSON lỗi và không phát hiện đề V118 trùng nguyên văn với dữ liệu đã rà soát.
6. Tạo bảng thiếu hụt của 150 chủ đề, cảnh báo gần phương pháp và danh mục 38 dạng ứng viên mới.
7. Giữ nguyên tất cả dữ liệu tài khoản, giao diện, Battle, học tập, chat và ngân hàng cũ.

## Kết quả kiểm toán

| Chỉ tiêu | Kết quả |
|---|---:|
| Số chủ đề trong danh mục | 150 |
| Bộ dạng ứng viên V113–V117 | 252 |
| Bộ dạng ứng viên mới V118 | **38** |
| Tổng bộ dạng ứng viên | **290** |
| Số câu mới được kiểm tra bằng oracle | **380** |
| Số câu mẫu thuộc 290 bộ (10 câu/bộ) | **2.900** |
| Dạng độc lập được chứng nhận toàn hệ thống | **0** |
| Chủ đề có 500 dạng độc lập được chứng nhận | **0** |
| Số bộ mới có cảnh báo giống phương pháp khác | **22** |
| Trùng nguyên văn sau chuẩn hóa với kho đã quét | **0** |
| Chủ đề có ít dạng ứng viên nhất | **1** |
| Chủ đề có nhiều dạng ứng viên nhất | **6** |

Đây là số bộ tạo **ứng viên**, không phải dạng đã được chứng nhận độc lập. Kiểm tra đáp số đúng và không trùng câu nguyên văn vẫn không chứng minh nội dung khác phương pháp sư phạm với hàng trăm nghìn câu cũ. 22 bộ mới có tín hiệu gần phương pháp khác cần duyệt riêng, chưa kết luận là trùng hoặc không trùng.

## Kiểm thử hồi quy

- **172/172 test backend đạt**, chạy theo nhiều nhóm, có hai ca lặp giữa các nhóm đã loại khỏi tổng.
- Nhóm Question Factory 51 ca; API/học tập/hình học 33 ca; Toán và kiểm định 43 ca; hồi quy khác 40 ca; Verified Bank API 4 ca; kiểm tra chất lượng ngân hàng 3 ca.
- Không chạy đồng loạt trong một tiến trình; chưa có kiểm thử production, Docker hoặc thiết bị thật.

## Bảo toàn ứng dụng

Chỉ thay đổi các thành phần Question Factory và cập nhật một test số lượng đăng ký. Không thay các thành phần Battle, bạn bè, chat, notification, đăng nhập, MathGeo, học tập, lộ trình, HTML/CSS/JS, cơ sở dữ liệu tài khoản hay ngân hàng verified cũ. Docker/VPS production không được thử trong phiên này.

## Tự động hóa sau phiên chat

Bản V118 là mã nguồn chạy được khi người dùng chạy nó. Không có tiến trình ChatGPT tự lập trình liên tục hay VPS đang hoạt động. Worker hiện tại chỉ sinh câu từ dạng đã được duyệt; chưa có hệ thống nghiên cứu 500 phương pháp độc lập mỗi chủ đề. Để triển khai 24/7 cần máy chủ thực tế, tài khoản API, ngân sách, giám sát, sao lưu và kiểm duyệt chuyên môn. Không được coi lịch nhắc lại là một worker chạy mã 24/7.

## Chạy lại kiểm toán

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

## Các tài liệu khảo cứu định hướng

Các quy tắc toán học được đối chiếu với nội dung chương trình Toán 10–12, các định lý cơ bản trong *OpenStax Precalculus 2e* và *OpenStax Calculus Vol. 1*. Bài toán, lời giải được biên soạn mới trong mã nguồn; không sao chép nguyên văn câu hỏi từ sách.
