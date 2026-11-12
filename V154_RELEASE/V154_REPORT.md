# MATH_WEB V154 | Báo cáo kỹ thuật

## Nguồn, phiên bản và phạm vi

- Input: `MATH_WEB_GITHUB_READY_V153_PERSISTENT_MIGRATION.zip` đã testzip đạt. Mã commit không có trong ZIP và không có thư mục `.git` để xác minh.
- Bổ sung các tệp nghiên cứu V153 còn dang dở từ checkpoint thư mục `/mnt/data/v153work` sau khi đối chiếu ZIP: **4 ứng viên, 40 câu** đã có oracle độc lập và chưa xuất bản. Bản ZIP V153 trước đó chưa chứa nhóm tệp này.
- V154 sửa bảo vệ symlink trong `backup_sqlite.py`, `migrate_persistent_data.py`, định danh tệp manifest trong `restore_sqlite.py`; bổ sung `--include-file` để di chuyển DB học tập ở thư mục khác **khi tên không xung đột**.
- Thêm công cụ read-only `audit_legacy_databases.py` đếm và phát hiện các bản tài khoản song song, không lộ username và không tự gộp tài khoản.
- Phục hồi hai file kiểm toán V128 đã được sửa trong workspace V153 nhưng còn thiếu trong ZIP nguồn.

## Ngân hàng toán

- V154 tạo 2 ứng viên phương pháp nghiên cứu mới và 20 câu (14 trắc nghiệm, 4 tự luận, 2 đúng/sai), có đáp án và lời giải.
- Oracle độc lập: hình chiếu trực giao tính khoảng cách; tích phân xác định kiểm bằng nguyên hàm ký hiệu và đạo hàm ngược (SymPy).
- Lô V154: 54 tệp JSONL lịch sử, 665.293 dòng đã quét, 0 trùng lời văn chuẩn hóa và 0 trùng nhãn (chủ đề, phương pháp) chuẩn hóa. **Không đủ để chứng nhận tính độc lập ngữ nghĩa.**
- 4 ứng viên V153, 40 câu từ checkpoint cũ được đóng gói lại nhưng không được tính thành ứng viên **mới V154**.
- 1.615 ứng viên lịch sử đã quét định danh (bao gồm lô V153 và V154), 1.050 ứng viên dùng chung phương pháp lõi cần rà soát.
- **Dạng độc lập mới được chứng nhận V154: 0. Câu hỏi mới được xuất bản vào ngân hàng chính: 0.** 20 câu V154 đã vượt phép kiểm đáp án độc lập, chỉ là dữ liệu nghiên cứu chờ duyệt.
- SQLite Question Factory đi kèm nguồn có 150 chủ đề, 0 archetype, 0 câu QF, 0 chứng nhận độc lập. Không suy diễn toàn website chỉ có 0 câu từ các hệ thống ngoài QF.
- Mục tiêu 300.000 dạng / 3.000.000 câu chưa đạt. Không tuyên bố hoàn thành.

## Dữ liệu và tính tương thích

- Đã nhận diện ba bản `mathweb.db` khác nhau tại `backend/database`, `MATH_WEB/backend/database`, `mathweb_work/backend/database`. Có 11, 5 và 18 hàng users tương ứng **trong ZIP V153**; khác biệt tài khoản không được tự giải quyết.
- Thử nghiệm migration trên bản sao **4 SQLite** (`mathweb.db`, QF, AI history, study suite) đã thành công. Tất cả qua `integrity_check`, số dòng users tương đương, byte các file DB nguồn không thay đổi. Có thể tạo WAL/SHM phụ trong lúc đọc bản sao.
- V154 PRIVATE checkpoint duy trì nguyên byte SQLite của ZIP nguồn; GITHUB_SOURCE_ONLY loại các SQLite. Nguồn tài khoản thực tế ở máy người dùng chưa được xác minh.
- Không thay đổi schema DB thật hoặc dữ liệu tài khoản trong lượt.

## Kiểm thử, đo hiệu năng và giới hạn

- Kiểm thử tập trung bảo vệ và phục hồi: 24/24 đạt. Oracle toán V154: 1 test parametrically kiểm 20 câu đạt. Oracle V153: 1 test kiểm 40 câu đạt.
- Bộ hồi quy cuối (`tests/` và năm bài kiểm toán QF): **279 bài đạt, 6 cảnh báo FastAPI deprecated event, 7 subtests đạt**. Đối chiếu SHA-256 của cả 6 SQLite sau kiểm thử với ZIP đầu vào cũng đạt. Bộ kiểm thử chạy trên thư mục dữ liệu tạm.
- Migration benchmark: một phép đo nhỏ trong `MIGRATION_DEMO.json`; **không có tối ưu runtime hay phép so sánh tốc độ trước/sau**. Không khẳng định API nhanh hơn.
- Chưa chạy browser E2E Battle/Admin, kiểm thử mobile, thử tải lớn và kiểm thử cập nhật ngay trên server thật.
- Chưa kiểm tra commit GitHub hoặc push; không hứa hệ thống tự chạy 50-60 phút khi công cụ không bảo đảm.

## TODO

1. Trên môi trường staging đã sao lưu, quyết định bản tài khoản nào thực sự đang sử dụng; không tự động trộn ba DB lịch sử.
2. Kiểm toán tính độc lập toán học của 6 ứng viên V153/V154 so với toàn bộ phương pháp cũ, không chỉ tên.
3. Thiết lập kho dữ liệu bền vững ngoài ZIP, xác nhận từng tính năng dùng đường dẫn thống nhất và kiểm thử khôi phục thực tế.
4. Battle/Admin E2E, hiệu năng ngân hàng lớn, giao diện mobile, benchmark trước/sau khi có thay đổi hiệu năng.
5. Tiếp tục mở rộng ngân hàng bài tập sau khi hoàn tất quy trình review.
