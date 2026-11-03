# MATH_WEB: phân tách dùng thử và tài khoản thật + giao/nộp bài

## Chế độ dùng thử
- Mở `trial-practise.html?trial=1` mà không cần đăng nhập hay gọi API demo.
- Dùng một hồ sơ khách cục bộ; không có tài khoản, bạn bè, chat, Battle hoặc bài tập được giao.
- Phiên thật (nếu có) được tạm cất riêng khi vào dùng thử và khôi phục khi thoát; token thật không hiện diện trong phiên dùng thử.
- Lựa chọn độ khó dùng thử lưu cục bộ dưới khóa khách.

## Chế độ tài khoản thật
- `practise.html` vẫn yêu cầu token hợp lệ.
- Thêm hộp “Bài tập của bạn”, đọc `/api/admin/learning/assignments/mine`, bắt đầu bài, hiển thị câu hỏi và gửi đáp án qua endpoint submit hiện có.
- Backend giao bài, lưu kết quả và lộ trình học đã có trong bản gốc, giữ nguyên các endpoint.

## Giới hạn kiểm thử
- Kiểm tra cú pháp JS và chạy bộ test backend hiện có.
- Cần xác nhận thủ công bằng một tài khoản giáo viên/admin và một tài khoản học sinh trên máy chủ để kiểm tra giao bài thật, hạn nộp và nhận xét.
