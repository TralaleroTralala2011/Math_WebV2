# MATH_WEB V32 · SortLab visual-only integration

Nguồn: `MATH_WEB_V28_CLASSIC_V30_LOGIN_GRADING_UI_FIX(1).zip`
Tham chiếu hiệu ứng: `sorting_algorithms_cyber_presentation_EPIC (1).html`

- Đã gắn stylesheet và script hiệu ứng vào **20 trang HTML gốc**.
- **Không chỉnh sửa bất kỳ file ứng dụng JavaScript/Python, SQLite, dữ liệu tài khoản, API hoặc backend nào.**
- Không chép code thuật toán sắp xếp, slide HTML, Tailwind hoặc event handler gốc của SortLab.
- Các trang chỉ được thêm đúng 2 liên kết: CSS trong `head`, script `defer` trước `body` đóng.
- Hiệu ứng mới: ánh sáng nền nhẹ, hiệu ứng vào trang, ánh sáng con trỏ, gợn click, hover thẻ, hỗ trợ reduced motion.
- Node `--check` JavaScript: **PASS**.
- Trạng thái kiểm thử trình duyệt end-to-end: **CHƯA CHẠY**.

Thiết kế không chặn click hoặc thay nội dung trang. Các phần backend, câu hỏi, Battle, Chat, đăng nhập, Admin, chấm bài đều bảo toàn byte so với ZIP nguồn.
