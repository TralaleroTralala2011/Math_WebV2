# MATH WEB Universal Game Standard

Bản nâng cấp này chuẩn hóa hệ thống game của MATH WEB:

- 92 kiến thức Toán 10/11/12 được giữ nguyên danh sách và phân tầng.
- Mỗi kiến thức luôn có đúng 3 game: Đấu tốc độ, Đấu Boss, Giải mật mã.
- Cả 3 game đều mở `games/universal/index.html` để dùng cùng một giao diện game chuẩn.
- Các game HTML cũ trong `games/<topic>/` KHÔNG bị xóa. Chúng được giữ nguyên làm mốc tham khảo và nền để cải tiến sau này.
- Các ID kiến thức cũ được ánh xạ sang ID AI phù hợp để Universal Game không bị lỗi `No valid topics`.
- Đã sửa trùng `Hàm số logarit`, đưa danh sách từ 93 về đúng 92 kiến thức.

## Smoke test

- 92/92 kiến thức gọi `/api/ai/questions` thành công.
- Đúng phân tầng: Toán 10 = 11/10/11; Toán 11 = 10/10/10; Toán 12 = 10/10/10.
- `node --check js/practise.js` passed.
- `python -m compileall -q backend/app` passed.
