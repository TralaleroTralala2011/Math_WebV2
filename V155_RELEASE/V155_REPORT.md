# MATH_WEB V155 | Hoàn tất checkpoint an toàn từ V154

**Nguồn mới nhất được xác minh:** `MATH_WEB_GITHUB_READY_V154_PRIVATE_CHECKPOINT.zip`. Hai gói V154 đã tồn tại nên lượt này **không ghi đè**, chuyển các cập nhật báo cáo/kiểm tra đóng gói sang bản V155. Các tệp SQLite nguồn đồng nhất byte với cả V153 và V154, và cả hai ZIP nguồn vượt `testzip`.

## Nội dung tích lũy trong lượt hiện tại

- V154: kiểm toán các bản SQLite khác nhau, đếm hàng `users` an toàn mà không xuất username; phát hiện ba DB `mathweb.db` có số tài khoản **11, 5, 18**. Không gộp tài khoản khi chưa chứng minh bản nào đang dùng.
- Backup/migration: từ chối symlink, không cho phép tệp trùng tên ghi đè; migration hỗ trợ `--include-file database/study_suite.sqlite3` để chuyển DB học tập ở nhánh khác khi có xác nhận, và xác minh mẫu bốn DB bằng `integrity_check` cùng so sánh số tài khoản.
- Restore: kiểm tra định danh tệp theo cả cú pháp Windows/Linux, từ chối manifest sai. File SQLite gốc lấy từ ZIP, không giữ dữ liệu thử tình cờ được tạo khi chạy test trực tiếp.
- Question Factory: khôi phục logic kiểm toán V128 trên mã nguồn khi ZIP lịch sử không còn, dùng file nghiên cứu sẵn có, 27 bài kiểm toán QF đạt.
- Nghiên cứu Toán: 2 phương pháp ứng viên V154 và 20 câu có lời giải, 20 đáp án vượt phép kiểm độc lập; 4 phương pháp V153 và 40 câu từng nằm trong workspace nhưng chưa được đóng gói nay được bảo toàn và đã kiểm tra oracle.
- Kiểm tra trùng V154: 54 file JSONL, **665.293 dòng**, 0 trùng câu nguyên văn sau chuẩn hóa và 0 trùng nhãn `(topic, method)` nguyên văn sau chuẩn hóa, **không chứng minh mới về ngữ nghĩa**. 1.615 bản ghi ứng viên có định danh, trong đó 1.050 dùng chung phương pháp lõi; chưa được chứng nhận độc lập.
- Đóng gói: công cụ mới từ chối đóng gói nếu SQLite gốc bị thay đổi hoặc phát sinh SQLite lạ, dùng chế độ tạo ZIP độc quyền tránh ghi đè cùng tên. Tạo riêng bản checkpoint **private** chứa dữ liệu cũ và mã nguồn **source-only** không chứa SQLite hoặc .venv. Cả hai vẫn cần kiểm tra bí mật thủ công trước khi chia sẻ.

## Bằng chứng kiểm thử

- Hồi quy backend + kiểm toán QF cuối cùng: **279 passed, 6 warnings, 7 subtests passed**, log `V154_RELEASE/FINAL_COMBINED_REGRESSION.log`.
- Test tập trung lưu trữ V151–V154: **24/24 passed**. Thêm **2/2** test công cụ đóng gói đạt; các test nghiên cứu V153 và V154 đều đạt.
- Cả **6 SQLite** trong private source kiểm SHA-256 nguyên byte so với ZIP V154 (và trước đó V153). Sao lưu/khôi phục 4 SQLite thử trên bản sao qua integrity check; không chạy migration dữ liệu live.
- Không có kiểm thử trình duyệt E2E Battle/Admin/tài khoản, mobile, benchmark tải lớn, hay kiểm thử trên môi trường sản xuất. Không có so sánh hiệu năng trước/sau nên không tuyên bố cải thiện tốc độ.

## Chỉ tiêu ngân hàng đề

| Thước đo | Trong lượt V153→V155 |
|---|---:|
| Ứng viên mới thực sự được thiết kế | 2 |
| Câu hỏi ứng viên mới đã xác minh đáp án | 20 |
| Ứng viên cũ V153 được bảo toàn | 4 |
| Câu ứng viên V153 được bảo toàn | 40 |
| Dạng mới đã chứng nhận độc lập về bản chất Toán | **0** |
| Câu mới xuất bản vào ngân hàng chính | **0** |

SQLite Question Factory đi kèm mã có 150 chủ đề, 0 archetype, 0 câu QF và 0 chứng nhận. Không đồng nhất số liệu này với các bộ câu hỏi khác trên website. **Mục tiêu 300.000 dạng độc lập và 3.000.000 câu chưa đạt.**

## Các giới hạn và TODO

- Không có Git commit metadata đi kèm nguồn và không thực hiện push GitHub.
- Thời lượng làm việc 50–60 phút không được đo nên không tuyên bố đã làm đủ.
- Phải xác minh cơ sở dữ liệu tài khoản thực sự đang sử dụng, thực hiện staging restore với bản sao lưu thật và kiểm tra đăng nhập/XP/bạn bè/tin nhắn.
- Thẩm định độc lập 6 ứng viên phương pháp được giữ lại, đối chiếu phương pháp cũ bằng chuyên môn chứ không chỉ trùng văn bản.
- Kiểm thử Battle/Admin E2E, các trang mobile/tablet và benchmark API với dữ liệu lớn; mở rộng ngân hàng khi có bằng chứng đúng Toán và độc lập.

## Dữ liệu và an toàn chia sẻ

**Không upload `*_PRIVATE_CHECKPOINT.zip` lên GitHub công khai.** Dùng `*_GITHUB_SOURCE_ONLY.zip` cho mã nguồn, nhưng phải rà soát secrets bằng công cụ riêng và bảo đảm `MATHWEB_DATA_DIR` trên máy chủ trỏ vào ổ lưu trữ bền vững. Bản ZIP nguồn không tự bảo vệ tài khoản trên máy chủ nếu dữ liệu live vẫn để trong thư mục triển khai.
