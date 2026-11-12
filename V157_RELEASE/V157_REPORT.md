# MATH_WEB V157 | Sửa lỗi khởi tạo Admin và bảo toàn cơ sở dữ liệu

**Nguồn mới nhất:** `MATH_WEB_GITHUB_READY_V156_PRIVATE_CHECKPOINT.zip`, đã được xác minh. Không ghi đè V156. ZIP đầu vào được kiểm tra toàn vẹn; 6 cơ sở dữ liệu SQLite trong mã nguồn làm việc trùng byte với ZIP gốc.

## Lỗi thực tế được tìm và sửa

Trong một thư mục triển khai mới không có SQLite, module `database.database` khởi tạo Admin cũ trong bảng `users`, sau đó `app.admin_routes` chuyển Admin sang `admin_accounts` và đổi tên bản ghi cũ. Nếu gọi `init_database()` lần nữa, hệ thống cũ sẽ cố tạo lại bản ghi Admin trong `users`; thao tác thực tế từng gặp lỗi `UNIQUE constraint failed: users.player_id` khi cùng một giây.

**V157 sửa** bằng cách kiểm tra bảng `admin_accounts` và không tự khởi tạo lại Admin legacy khi tài khoản quản trị riêng đã tồn tại. Khi cần tạo Admin legacy trong môi trường cũ, ID mới sử dụng số ngẫu nhiên mật mã, không dùng timestamp theo giây. V157 thêm kiểm tra môi trường `MATHWEB_ENV=production` hoặc `prod`: yêu cầu đặt `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` khác mặc định và dài ít nhất 12 ký tự; môi trường phát triển không bị thay đổi quy tắc này.

**Hai kiểm thử hồi quy mới đạt:** khởi tạo lại ba lần không sinh tài khoản Admin bóng, và production từ chối mật khẩu bootstrap mặc định nhưng chấp nhận giá trị được cấu hình hợp lệ.

## Tiến độ từ đầu lượt V153→V157

- Hai phương pháp nghiên cứu ứng viên V154 với 20 câu có đáp án được kiểm tra bằng oracle toán độc lập; vẫn **chờ duyệt tính độc lập**, không được phát hành.
- Bốn phương pháp và 40 câu V153 từ workspace cũ được đóng gói bổ sung.
- Quét 665.293 dòng JSONL lịch sử; chưa thấy trùng nguyên văn chuẩn hóa, chưa kiểm chứng trùng ngữ nghĩa. 1.050 ứng viên lịch sử dùng chung phương pháp lõi.
- Thêm audit DB nhiều nhánh (11/5/18 tài khoản lịch sử) và backup/migrate có chặn symlink, không tự gộp tài khoản. Thử migration 4 DB trên bản sao.
- Hệ thống đóng gói đã phân tách ZIP private chứa 6 SQLite lịch sử và ZIP source-only không chứa DB. Tệp WAL/SHM tạm không được đóng gói. Có kiểm tra checksum/integrity DB và chặn file ZIP trùng tên.
- **Dạng toán độc lập mới được chứng nhận: 0. Câu hỏi mới được xuất bản: 0.**

## Kiểm thử

- Bộ hồi quy backend và Question Factory: **281 passed, 6 warnings, 7 subtests passed**.
- Kiểm thử Admin V157: **2/2 đạt**.
- Kiểm thử backup/migration trước đó: **24/24 đạt**; đóng gói: **4/4 đạt**; oracle V153/V154 đạt.
- Chưa kiểm thử đăng nhập/XP thực tế ở môi trường sản xuất, Battle/Admin E2E bằng trình duyệt, benchmark API triệu câu hay responsive trên nhiều thiết bị.
- Không có mã Git commit gốc trong ZIP; không thực hiện đẩy GitHub.

## Phân phối và an toàn

- `MATH_WEB_GITHUB_READY_V157_PRIVATE_CHECKPOINT.zip`: bản checkpoint đầy đủ, chứa 6 SQLite lịch sử. **Không đẩy lên GitHub công khai.**
- `MATH_WEB_GITHUB_READY_V157_GITHUB_SOURCE_ONLY.zip`: mã nguồn đã lọc SQLite và các tệp bí mật thông dụng, vẫn cần kiểm tra riêng trước khi công khai.
- Ở môi trường production, đặt `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` là bí mật mạnh ngay từ đầu; rà lại và thay đổi mật khẩu quản trị hiện có nếu trước đây dùng mặc định. Dùng `MATHWEB_DATA_DIR` cố định nằm ngoài thư mục giải nén.

## TODO

Ưu tiên kiểm tra luồng tạo tài khoản/đăng nhập/XP sau khi thay phiên bản bằng dữ liệu thử trên staging; kiểm tra Battle, bạn bè, chat, Admin E2E; xác định DB thực tế đang dùng; thẩm định dạng toán độc lập và tiếp tục mở rộng ngân hàng. Không thể gọi toàn bộ dự án hoàn thành 100% khi chưa có bằng chứng đủ 300.000 dạng và 3.000.000 câu.
