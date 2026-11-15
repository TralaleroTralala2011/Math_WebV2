# MATH_WEB V61 – sửa tên Word và liên kết câu hỏi/chủ đề

**Nền:** ZIP V60 do người dùng tải lên ngày 15/11/2026. Đây là bản sửa tập trung vào provenance và định tuyến chủ đề của 150 Word; không viết lại nội dung đề toán, không thay đổi giao diện hay luồng Battle.

## Nguyên nhân và phạm vi
- Tên Word không dấu cũ làm rơi chữ **đ/Đ** khi chuyển tên tệp; chẳng hạn `..._uong_tron.docx`, `..._Menh_e.docx`, `..._Toa_o.docx`.
- Trong V60, backend đã đọc câu hỏi từ SQLite bằng **mã chủ đề**, chứ **không dùng tên file Word để tìm từng câu lúc chơi**. Vì vậy sai tên file là lỗi đáng sửa, nhưng không thể khẳng định đó là nguyên nhân duy nhất khiến game không lấy được câu.
- Hai cặp Word lớp 11 có chung tên hiển thị nhưng mã khác: `day_so` / `day_so_tong_quat`, và `phuong_trinh_luong_giac` / `phuong_trinh_luong_giac_day_du`. Hệ thống mới ưu tiên **mã ID hoặc tên file kèm số thứ tự**, không đoán khi chỉ nhận tên trùng nhau.

## Nội dung sửa
1. Thêm `question_bank_v254_source/150_CHU_DE_WORD_CORRECTED_V61.zip`, bao gồm 150 Word với tên **không dấu chuẩn hóa**, có chữ `d` đại diện `đ`; **nội dung từng Word nguyên byte**.
2. Giữ nguyên `question_bank_v254_source/150_CHU_DE_WORD_SOURCE_V60.zip`, làm bản gốc để đối chứng và khôi phục.
3. Sửa bảng `backend/app/ai/storage/v254_b56_topic_map.json` để mỗi `source_word` dùng tên mới và `source_word_legacy` lưu tên cũ.
4. Đồng bộ **95.544** trường `source_word` trong 150 JSONL và **16.274** bản ghi ứng viên trong SQLite. Đề bài, đáp án, lời giải và mã chủ đề **không đổi**.
5. Cập nhật seed SQLite nén và checksum trong manifest để Render có thể phục hồi lớp ngân hàng này.
6. Thêm bảng alias `word_topic_aliases_v61.json` nhận dạng tên chủ đề, tên file cũ/mới có kèm số thứ tự, có kiểm tra theo khối lớp. Tên hiển thị trùng nhau phải dùng ID riêng, tránh chuyển nhầm chủ đề.
7. Bổ sung khả năng importer chấp nhận **cả tệp Word gốc và tệp Word đã chuẩn hóa**.

## Kiểm chứng
- Số Word: 150/150; thay tên: **52**; Word bị mất: **0**.
- Word mới/bản gốc: SHA256 của **từng tệp DOCX** trùng nhau tuyệt đối.
- JSONL: 150 tệp, 95.544 bản ghi, **0 lỗi ghép grade/topic/source_word**.
- Dữ liệu chứa đề/đáp án/lời giải trong SQLite, đối chiếu theo ID trước và sau sửa: **16.274/16.274 giữ nguyên** (digest bằng nhau).
- Seed/SQLite: checksum hợp lệ, SQLite `integrity_check: ok`.
- Pytest: **10/10 đạt** (V61 + kiểm thử ngân hàng V59).
- API nạp câu từ nguồn V60/V59/V254: các mã chủ đề mẫu lớp 10, 11, 12 trả về câu hỏi.

## Giới hạn
- **Chưa kiểm định ý nghĩa toán học của toàn bộ 95.544 mục Word**, gồm mức độ khó, tính đúng của đáp án và khả năng có câu sai chủ đề bên trong các nguồn V254/V59/Word.
- **Chưa kiểm thử website GitHub Pages/Render thực tế**. Mã backend và dữ liệu liên kết được kiểm tra tại chỗ.
- Việc đổi tên nguồn **không làm tăng số câu hợp lệ** và **không tự giải quyết mọi nguyên nhân game không có câu**. Tiếp tục giữ cơ chế chặn trùng trong lượt chơi từ V60.

Báo cáo chi tiết 150 tên file cũ/mới: `WORD_TOPIC_FILENAME_AUDIT_V61.json`.
