# MATH_WEB V156 | Checkpoint cuối của lượt phát triển

**Nguồn vào:** `MATH_WEB_GITHUB_READY_V155_PRIVATE_CHECKPOINT.zip` đã kiểm tra toàn vẹn. Do bản V154 và V155 đã tồn tại trong cùng môi trường, các bản đó được giữ nguyên không ghi đè. V156 bổ sung rào chắn đóng gói dữ liệu sau khi xác minh thành phần mã nguồn được bảo toàn giữa các bản.

## Thay đổi kỹ thuật đã thực hiện trong toàn lượt

1. Sửa cơ chế backup/migration SQLite: chặn file và thư mục symlink, kiểm tra manifest chặt hơn cho Windows và POSIX, tránh ghi đè DB trùng tên; hỗ trợ `--include-file` để chuyển `study_suite.sqlite3` ngoài thư mục backend.
2. Thêm kiểm toán đọc-only các DB lịch sử. ZIP V153 có ba bản `mathweb.db` khác nhau với 11, 5 và 18 tài khoản (số hàng); phải xác định DB nào đang hoạt động trước khi di chuyển. Không tự gộp hoặc xóa.
3. Khôi phục các kiểm thử kiểm toán V128 và lô nghiên cứu V153 bị bỏ sót khỏi ZIP V153 nhưng vẫn còn ở checkpoint thư mục, không đụng vào SQLite người dùng.
4. Tạo **2 phương pháp ứng viên mới / 20 câu hỏi** V154 với lời giải và đáp án đã được kiểm chứng bằng oracle hình chiếu trực giao và tích phân ký hiệu. Chưa có bằng chứng độc lập so với ngân hàng lịch sử, giữ nguyên trạng thái chờ duyệt.
5. Kiểm toán JSONL: 665.293 dòng lịch sử, 0 trùng câu nguyên văn sau chuẩn hóa, 0 trùng phương pháp cùng chủ đề **theo nhãn văn bản**. Phát hiện 1.050 ứng viên dùng chung phương pháp lõi trong 1.615 ứng viên đã quét; không tự chứng nhận.
6. Bảo vệ phát hành: từ chối ZIP đầu vào có WAL SQLite chưa checkpoint, từ chối DB bị thay đổi hoặc DB lạ, chạy `PRAGMA integrity_check` không sửa dữ liệu, tạo ZIP với chế độ độc quyền để tránh đè bản khác. ZIP private giữ 6 SQLite gốc, **loại WAL/SHM tạm**; ZIP source-only loại toàn bộ SQLite và dữ liệu nhạy cảm phổ biến nhưng giữ file `.env.*.example` chứa placeholder.

## Kết quả kiểm thử có bằng chứng

- **279 passed, 6 warnings, 7 subtests passed** ở bộ backend + kiểm toán Question Factory. Cảnh báo thuộc FastAPI `on_event` deprecated.
- **24/24** bài test được chọn cho backup/migration/restore đạt, **4/4** kiểm thử đóng gói đạt; test oracle 20/20 câu V154 và 40/40 câu V153 đạt.
- 6 SQLite trong nguồn đã đối chiếu SHA-256 nguyên byte với cả ZIP V153/V154/V155; lô migration 4 DB trên bản sao kiểm tra tính toàn vẹn và giữ số dòng tài khoản. Không chạy migration trên server thật.
- Kiểm tra toàn vẹn cả hai ZIP đầu ra khi đóng gói.

## Tiến độ mục tiêu và giới hạn

| Chỉ tiêu | Kết quả tăng thêm trong lượt |
|---|---:|
| Ứng viên dạng toán mới | 2 |
| Câu hỏi mới có đáp án kiểm độc lập, vẫn chờ duyệt | 20 |
| Dạng **độc lập thật** được chứng nhận mới | **0** |
| Câu mới đưa vào ngân hàng đang phát hành | **0** |
| Dữ liệu ứng viên V153 được bảo toàn | 4 phương pháp, 40 câu |

SQLite Question Factory nguồn có 150 chủ đề nhưng chưa có archetype/câu QF/chứng nhận trong bảng tương ứng; điều này không thống kê các nguồn luyện tập khác. **300.000 dạng độc lập và 3.000.000 câu hỏi chưa đạt.**

**Chưa làm:** kiểm thử giao diện Battle/Admin/tài khoản bằng trình duyệt, kiểm tra responsive, benchmark API ở quy mô triệu câu, xác minh dữ liệu live cùng thông tin đăng nhập, phát hành GitHub, thẩm định ngữ nghĩa toàn bộ ứng viên. Không có chứng cứ đo đủ 50–60 phút làm việc nên không khẳng định đạt thời lượng.

**Lượt kế tiếp:** bắt đầu từ `MATH_WEB_GITHUB_READY_V156_PRIVATE_CHECKPOINT.zip`, xác minh SHA ZIP và backup dữ liệu thật; rà trùng phương pháp trước khi cấp chứng nhận; chạy E2E Battle/Admin và hiệu suất thực trước/sau mọi thay đổi hotpath.

**Lưu ý bảo mật:** `*_PRIVATE_CHECKPOINT.zip` **có bản sao SQLite với tài khoản**, không upload GitHub. `*_GITHUB_SOURCE_ONLY.zip` không chứa SQLite nhưng vẫn cần rà soát bí mật ngoài SQLite trước khi public. Đường dẫn `MATHWEB_DATA_DIR` phải ở ngoài thư mục triển khai để không mất tài khoản khi nâng cấp mã nguồn.
