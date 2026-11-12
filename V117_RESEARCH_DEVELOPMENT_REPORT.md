# MATH_WEB V117 · Báo cáo mở rộng ngân hàng 500 dạng/chủ đề

Ngày: 08/11/2026. Nền dự án: `MATH_WEB_GITHUB_READY_V116_RESEARCH_500_TARGET.zip`.

## Mục tiêu người dùng

- 150 chủ đề × 500 dạng toán độc lập/chủ đề = **75.000 dạng toán độc lập**.
- Mỗi dạng có 10 câu hỏi khác nhau, tổng **750.000 câu**.
- Các hình thức: lý thuyết, tự luận ngắn, trắc nghiệm, đúng/sai, trả lời ngắn, bài vận dụng và bài toán thực tế phù hợp chủ đề.
- **Không** coi thay số, đổi tên, ID, hình thức câu hỏi là dạng toán độc lập.

## Đã thực hiện có bằng chứng

1. Nghiên cứu và lập trình **56 bộ dạng ứng viên mới** thuộc 56 hướng bài toán (15 lớp 10, 18 lớp 11, 23 lớp 12) từ các chủ đề trong danh mục chính xác. Bộ tạo mỗi dạng cho 10 bộ dữ kiện khác nhau, có đáp án và lời giải.
2. Xuất **560 câu mới** vào `V117_AUDIT/V117_NEW_QUESTIONS.jsonl`. Tổng Question Factory từ V113–V117: **252 bộ dạng ứng viên** và **2.520 câu mẫu**. Không nhập các câu mới vào ngân hàng đã xuất bản.
3. Viết một **bộ tính đáp án độc lập từ dữ kiện** (`v117_oracle.py`) cho 56 dạng. Kiểm tra số học chính xác bằng SymPy, kiểm tra chống sửa nội dung, 4 lựa chọn khác nhau và tính đúng/sai.
4. Xử lý một số rủi ro chất lượng: 10 dữ kiện gốc riêng cho một dạng, phương án nhiễu xác suất nằm trong [0,1], phương án nhiễu giá trị lượng giác trong [-1,1], ngăn lựa chọn số âm trong bài đếm.
5. Kết nối 56 dạng với engine, CLI, lưu trữ và vòng điều phối. **Đăng ký mặc định ở `pending`**, không tự duyệt xuất bản.
6. Tạo báo cáo cho **150/150 chủ đề**, và cảnh báo dạng gần trùng để so sánh phương pháp.

## Kết quả kiểm toán

| Kiểm tra | Kết quả |
|---|---:|
| Chủ đề trong danh mục | 150 |
| Bộ dạng ứng viên trước V117 | 196 |
| Bộ dạng ứng viên mới V117 | 56 |
| **Tổng bộ dạng ứng viên** | **252** |
| Câu mẫu Question Factory V113–V117 | 2.520 |
| Câu mẫu mới V117 được đối chiếu với bộ tính độc lập | 560 |
| Dòng dữ liệu ngân hàng cũ được duyệt JSON và so trùng nguyên văn | 344.280 |
| Dòng V113/V114/V116 được so trùng nguyên văn | 1.960 |
| Đề V117 trùng nguyên văn với hai tập nguồn trên | 0 |
| Nhóm chữ ký dạng trùng tuyệt đối trong danh sách ứng viên | 2 |
| Bộ V117 bị cảnh báo gần giống dạng khác theo từ khóa | 30 |
| Chủ đề có 500 bộ dạng ứng viên | 0 |
| **Dạng được chứng nhận độc lập toàn cục** | **0** |

**Cực kỳ quan trọng:** Không phát hiện trùng nguyên văn **không** đồng nghĩa dạng toán độc lập. Có thể cùng một phương pháp giải nhưng khác dữ kiện/cách diễn đạt. 252 là số bộ dạng có mã tạo câu đã thử; 0 là số bộ dạng đủ bằng chứng công nhận độc lập trên toàn bộ ngân hàng sau rà soát sư phạm. Không tuyên bố đã đạt mục tiêu 75.000 dạng/750.000 câu.

Mỗi chủ đề hiện có từ **1–4 bộ dạng ứng viên**, còn thiếu đáng kể so với 500 dạng/chủ đề. Một số chủ đề hẹp có thể không thực sự có 500 phương pháp độc lập trong giới hạn kiến thức SGK. Không được chế biến thêm biến thể giả để đạt KPI.

## Kiểm thử được thực hiện

- Nhóm Question Factory và vận hành: **46/46 đạt**.
- Nhóm ngân hàng/verified API: **7/7 đạt**.
- Nhóm backend còn lại: **114/114 đạt**.
- **Tổng 167/167 bài test đạt**, theo ba lệnh riêng. Đây là kiểm thử cục bộ, không phải kiểm thử sản xuất hay duyệt sư phạm.
- Chưa kiểm thử trực tiếp trên browser, thiết bị thật hoặc môi trường Docker/VPS.

## Bảo toàn và giới hạn

Giữ nguyên những file ứng dụng, giao diện, Battle, tài khoản, chat, học tập, CSS mobile và ngân hàng `verified_seed_bank.jsonl` từ V116. Chỉ chỉnh mã nguồn Question Factory, một bài kiểm thử vận hành cần cập nhật số lượng đăng ký và thêm tài liệu/test V117. Cơ sở dữ liệu tài khoản gốc `mathweb.db` được lấy lại đúng byte từ ZIP V116 sau khi chạy test.

Bộ oracle xác minh **đáp số được tính theo dữ kiện**, không chứng nhận bản thân đề bài đã đủ rõ với mọi học sinh, đáp án nhiễu có chất lượng tốt như giáo viên biên soạn, hay chứng minh một phương pháp mới độc lập toàn hệ thống. Mọi nội dung mới vẫn chờ rà soát và bị chặn khỏi ngân hàng công khai.

## Tài liệu đối chiếu lĩnh vực kiến thức

- OpenStax *Precalculus 2e*, các chương về hàm số, lượng giác, hệ phương trình, giải tích sơ bộ và xác suất: https://openstax.org/books/precalculus-2e/pages/preface
- OpenStax *Calculus Volume 1*, các chương về giới hạn, đạo hàm, tích phân và ứng dụng: https://openstax.org/books/calculus-volume-1/pages/preface

Các đề V117 được viết mới bằng mã nguồn, không sao chép bài tập có bản quyền.

## Chạy thử sau khi giải nén

Tại `MATH_WEB_GITHUB_READY/backend`:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q tests/test_question_factory_v117.py
python -m question_factory.cli --db .\v117_demo.sqlite3 init
python -m question_factory.cli --db .\v117_demo.sqlite3 seed-v117
python -m question_factory.cli --db .\v117_demo.sqlite3 status
```

Lưu ý: `seed-v117` chỉ đăng ký 56 dạng ứng viên và không tự đưa nội dung vào game. Đọc trực tiếp file JSONL ở `V117_AUDIT` nếu muốn xem bộ câu mẫu và đáp án.
