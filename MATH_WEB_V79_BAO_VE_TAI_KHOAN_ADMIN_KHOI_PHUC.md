# MATH_WEB V79 · Cứu dữ liệu tài khoản, bảo vệ Admin và chống trùng câu

Ngày 16/11/2026. Nền: bản MATH_WEB V77 đầy đủ đã có gọi thoại, gọi video, hồ sơ người dùng và bản vá chống trùng dạng bài theo lượt chơi.

## Quan trọng: 30+ tài khoản đã mất

**Không có dữ liệu tài khoản cũ trong ZIP này. Không có thuật toán nào có thể khôi phục mật khẩu/tiến độ của các tài khoản đã mất nếu không còn database cũ hoặc bản sao lưu.** Trước khi triển khai phiên bản này, hãy thu thập và bảo vệ những bản đang còn.

1. Tạm dừng đăng ký/tác vụ ghi dữ liệu trong lúc kiểm tra. Nếu trang Admin còn đăng nhập được, tải bản sao lưu .mwbackup hiện tại về máy riêng trước tiên.
2. Render Dashboard → chọn đúng Web Service → Settings/Disk: xác định có Render Persistent Disk thực sự gắn vào `/var/data` hay không, không chỉ có biến môi trường.
3. Nếu đã có Disk: kiểm tra các disk snapshots còn khả dụng từ thời điểm trước khi mất tài khoản. LƯU Ý khôi phục snapshot toàn bộ ổ có thể ghi đè dữ liệu mới, chỉ thực hiện sau khi đã sao lưu trạng thái hiện tại và cân nhắc lịch sử thay đổi.
4. Nếu đã có tệp `.mwbackup` từ Admin: sử dụng mục **Thao tác cập nhật → Kiểm tra & khôi phục dữ liệu**, chỉ khi đã sao lưu dữ liệu hiện tại. V79 chặn phục hồi bản sao lưu chứa ít tài khoản hơn database đang sống.
5. Nếu trước đây chạy trên Render Free và SQLite lưu trong vùng filesystem mặc định, bản thân Render không giữ file sau sleep/redeploy; không thể tái tạo 30 tài khoản chỉ từ repository hoặc ZIP không chứa database.
6. Có thể dùng `scripts/audit_legacy_databases.py` để rà soát các bản database đã tải về trước đó trên máy cá nhân; không ghép chồng dữ liệu theo tên tài khoản nếu chưa kiểm chứng.

## Chặn mất dữ liệu lần sau

- Render phát hiện nhưng không có **ổ mount thực sự** + `MATHWEB_DATA_DIR` + `MATHWEB_DB_PATH` phù hợp → từ chối khởi động thay vì khởi tạo tài khoản mới trên ổ tạm.
- Lưu watermark về số tài khoản đã đăng ký sau mỗi lần tạo tài khoản; phát hiện số lượng giảm hoặc database biến mất khi ledger còn tồn tại → từ chối tiếp tục, yêu cầu kiểm tra backup.
- Snapshot SQLite theo phương pháp SQLite backup nhất quán (gồm các ghi WAL), tạo lúc khởi động với database cũ, định kỳ trong quá trình chạy và theo nút **Tạo điểm khôi phục SQLite** từ Admin.
- Tối đa 4 điểm khôi phục cùng ổ để hạn chế chiếm dung lượng, **không thay thế backup ngoài máy chủ**.
- Admin Dashboard hiển thị số tài khoản hiện tại, mốc cao nhất, số snapshot, mount status và tình trạng backup ngoài (chưa xác minh).
- Chức năng khôi phục .mwbackup từ chối khôi phục nếu số tài khoản trong backup ít hơn số tài khoản đang hoạt động.
- Trên Render Blueprint: gói **Starter có Persistent Disk `/var/data`**, biến môi trường đường dẫn SQLite đặt nhất quán. `MATHWEB_ENV=production`, `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` là secret cài trong Render, không đưa vào GitHub.

## Cập nhật V77 → V79

- Không xóa/sửa nội dung ngân hàng Word và ngân hàng câu hỏi SQLite đã đóng gói sẵn; giữ nguyên dữ liệu học tập đã có trong bản nền.
- Gửi cùng script chống trùng dạng theo 3 game một chủ đề, có định danh lượt chơi chung; làm mới phiên bản URL JS trên 526 trang game để tránh cache trang cũ.
- Giữ gọi thoại, gọi video, xem hồ sơ, Friends, Battle, luyện tập, hình học và các trang Admin cũ.
- Mở rộng hệ thống Admin với chẩn đoán lưu trữ, tạo snapshot theo quyền quản trị và hướng dẫn sao lưu mã hóa.

## Cách dùng trên Render

1. **Không đẩy bản ZIP lên dịch vụ có tài khoản thật trước khi sao lưu được database hiện có.**
2. Cài đặt Render service **paid** hỗ trợ Disk, gắn mount path `/var/data` trước khi chấp nhận đăng ký. Nếu dùng Render Free, cần chuyển kiến trúc dữ liệu sang dịch vụ DB bền vững, không dùng SQLite trên filesystem tạm.
3. Cài env `MATHWEB_DATA_DIR=/var/data`, `MATHWEB_DB_PATH=/var/data/mathweb.db`, `MATHWEB_AI_HISTORY_DB_PATH=/var/data/mathweb_ai_history.sqlite3`, `MATHWEB_ENV=production`.
4. Dùng giá trị secret riêng cho `MATH_WEB_SECRET_KEY` (ít nhất 32 ký tự), `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` đủ dài cho lần khởi tạo đầu tiên.
5. Chỉ chạy **1 backend worker** với một SQLite disk. Render Dashboard phải cho thấy Disk đang gắn, không chỉ biến môi trường.
6. Sau khi chạy: Admin → Tổng quan → Bảo vệ tài khoản & sao lưu, đối chiếu số lượng tài khoản. Tải bản sao lưu mã hóa `.mwbackup` và cất ngoài máy chủ.

## Kiểm thử trong phiên

- 43/43 kiểm thử chọn lọc đã đạt, gồm đăng ký/đăng nhập, bootstrap Admin, sao lưu mã hóa và khôi phục, chặn giảm số tài khoản, phòng khởi tạo DB tạm Render, kiểm tra snapshot, tín hiệu gọi điện, Battle theo chọn chủ đề, lượt hỏi không lặp ở tầng câu hỏi.
- Ba bài kiểm thử Battle cũ (`test_v22_two_account_flow`) yêu cầu bắt đầu trận khi chưa chọn chủ đề, không còn đúng luồng Battle mới. Chưa khẳng định toàn bộ bộ test legacy đạt.
- Chưa đăng nhập và kiểm thử thực tế trên dịch vụ Render của bạn; chưa xác nhận việc phục hồi những tài khoản đã mất.

## Giới hạn cần hiểu

Không thể cam kết “100% không mất dữ liệu” nếu mất cả Render Disk và không có bản sao lưu độc lập. Snapshot trên chính ổ dữ liệu chỉ giúp xử lý một số lỗi ghi đè và không thay thế backup từ một nơi độc lập. Bộ lọc câu trùng tránh thay số/ID, nhưng chưa chứng minh được mọi dạng toán khác nhau về bản chất trong kho lớn; nếu hết dạng đạt chuẩn, game thông báo hết câu thay vì thay số để tạo câu giả mới.
