# MATH_WEB V141 | Báo cáo phát triển và checkpoint

- Mã nguồn gốc: `MATH_WEB_GITHUB_READY_V140_GRADING_V122_SAFE.zip` (mở ZIP và kiểm chứng có thật trong lượt này).
- Thời điểm checkpoint UTC: `2026-11-08T16:42:26.230453+00:00`.
- **Trạng thái: CHƯA HOÀN THÀNH mục tiêu cuối**.

## Sửa lỗi đo tiến độ và bảo toàn API

1. Backend trước đây lấy số **archetype được duyệt để sinh đề** thay cho số dạng thực sự **được thẩm định tính độc lập** khi tính thiếu hụt. Đã tách `approved_archetypes` và `certified_independent_types` bằng bảng `independence_certifications`. Bảng mới rỗng mặc định, không chứng nhận tự động; không xóa dữ liệu cũ.
2. Thêm `certified_method_verified_questions`, `target_ready_questions`, `target_questions_remaining_qualified`, các cột tương ứng theo chủ đề. Chỉ câu đã xác minh thuộc dạng có hồ sơ chứng nhận mới được tính vào chỉ tiêu 3 triệu.
3. Thiếu hụt dạng/câu tính **theo từng chủ đề**, nên thừa ở chủ đề A không bù vào thiếu ở chủ đề B. `/api/factory/catalog` vẫn hỗ trợ cấu trúc cũ và trả thêm số lượng chứng nhận.
4. Chứng nhận trong bảng dữ liệu là một hồ sơ lưu trữ, không tự nó chứng minh toán học. Hiện không đưa ra chứng nhận mới từ lô V141, và cần quy trình thẩm định nội dung có bằng chứng thật trước khi sử dụng trong sản xuất.

## Ngân hàng ứng viên V141

- **11** nhóm phương pháp ứng viên thuộc **11 chủ đề** Toán 10–12; **110** câu (10 câu/nhóm).
- Định dạng: **77 trắc nghiệm / 22 trả lời ngắn / 11 đúng-sai**, đúng tỷ lệ 7:2:1.
- **110/110** phép đối chiếu đáp án bằng phép tính/suy luận thứ hai đạt. 77 câu trắc nghiệm có 4 phương án khác nhau với đúng 1 đáp án đúng theo phép kiểm toán biểu thức.
- Rà trùng câu nguyên văn qua **649,483** bản ghi thuộc **44** tệp JSONL lịch sử: **0 trùng nguyên văn** phát hiện. Phép so tên phương pháp cùng chủ đề có 0 cảnh báo vượt ngưỡng; không phải phép chứng nhận khác biệt ngữ nghĩa.
- Dữ liệu vẫn có `review_status=pending-expert-review`, `published=false`, `independence_certified=false`; KHÔNG đưa vào nguồn câu hỏi sản xuất.
- Phạm vi toán học được kiểm tra là đáp án và cấu trúc câu, chưa thẩm định thủ công đầy đủ nội dung bài giảng và tính độc lập so với mọi phương pháp cũ.

## Kiểm thử

- Hồi quy backend diện rộng: **208/208 đạt**, **đã loại riêng test_question_factory_v120.py** vì tác vụ chạy lâu; 6 cảnh báo deprecation FastAPI. Log: `V141_RELEASE/BROAD_REGRESSION.log`.
- Kiểm thử nghiên cứu V141: **9/9 đạt**.
- Hồi quy API/tích hợp đã chọn: **33/33 đạt** (trong quá trình phát triển).
- Smoke cuối trên sửa đổi mới nhất: **11/11 đạt** (`V141_RELEASE/V141_FINAL_SMOKE.log`).
- **Không** xác nhận 100% chức năng frontend, Battle đa trình duyệt, Admin trong thực tế đã hết lỗi. Bản sửa không thay đổi mã frontend/Battle.
- Bản ZIP mới được ghép từ dữ liệu ZIP V140 GỐC, chỉ thay đúng các file liệt kê và thêm nghiên cứu/kiểm thử/báo cáo; dữ liệu SQLite không bị đưa biến động từ test vào bản giao.

## Mục tiêu, lũy kế và giới hạn

- Mục tiêu cuối: 150 × 2.000 dạng thực sự độc lập = 300.000 dạng; 10 câu/dạng = 3.000.000 câu.
- Mục tiêu lặp do người dùng nêu: tối thiểu 1.000 dạng độc lập/chùm. Lượt này mới có **11 ứng viên chờ thẩm định**, **0 dạng mới được chứng nhận** và **110 câu chờ duyệt**; không hề tuyên bố đạt chỉ tiêu.
- Không có quá trình ChatGPT chạy mã liên tục trong 60 phút được bảo đảm. Automation giữ lịch mỗi giờ với yêu cầu tận dụng tối đa thời lượng thực tế; mỗi lượt là một tác vụ riêng.

## Hướng tiếp theo

1. Thẩm định bằng chứng về phương pháp độc lập cho từng ứng viên, sàng lọc trùng **bản chất**, không chỉ tên/ID/số.
2. Bổ sung dạng toán thật sự mới theo từng chủ đề và ngân hàng 10 câu có lời giải, không nhân bản cách làm.
3. Chạy riêng test V120 thời gian dài và kiểm thử E2E hai trình duyệt cho Battle/tài khoản/Admin.
4. Giữ nguyên dữ liệu SQLite và hồi quy khi tích hợp ứng viên đã vượt kiểm toán, không công bố tự động.
