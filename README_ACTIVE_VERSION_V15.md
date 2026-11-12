# MATH_WEB NEON V15 - Đúng thư mục cần chạy

Website chính: thư mục `MATH_WEB_GITHUB_READY` chứa `index.html`, `learning-path.html`, `admin.html`, `backend/`, `css/`, `js/` và `START_MATH_WEB.bat`.

Các thư mục `MATH_WEB/` và `mathweb_work/` là bản tham chiếu cũ, không phải bản NEON V15. Không chạy trang từ những thư mục đó.

## Chạy trên Windows

1. Sao lưu database và khóa đăng nhập của phiên bản cũ trước khi cập nhật.
2. Giải nén ZIP, mở thư mục `MATH_WEB_GITHUB_READY`.
3. Chạy `START_MATH_WEB.bat`, chờ backend và frontend khởi động.
4. Mở `index.html` thông qua địa chỉ máy chủ frontend được hiển thị, không mở trực tiếp bằng `file://`.
5. Admin dùng tài khoản Admin riêng; học sinh không có quyền gọi API Admin.

## Báo cáo và kiểm thử

- `NEON_V15_REPORT.md`: kết quả, độ phủ thực tế và giới hạn.
- `placement-audit/`: ba bản kiểm kê câu hỏi theo khối lớp, **không phải ba đề thi hoàn chỉnh**.
- `tools/export_placement_blueprint.py`: xuất độ phủ từ database hiện có.
- `tools/test_live_realtime_tcp.py`: thử Chat/Battle với hai kết nối TCP độc lập, không thay thế kiểm thử trên hai máy thật.
