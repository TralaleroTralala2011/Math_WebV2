# Sửa HTTP 400 ở game Hệ phương trình (04/11/2026)

Nguyên nhân: frontend gửi `topics:["SYSTEM_EQUATION"]` nhưng backend chỉ có alias `system-equation` và ID chuẩn `phuong_trinh_he`. Bộ lọc trả về `No valid topics` (HTTP 400).

Đã sửa: 3 game gửi ID chuẩn `phuong_trinh_he`; backend chấp nhận ID cũ không phân biệt hoa/thường và chỉ nhận ID thuộc đúng khối lớp. Không thay giao diện.

Thông báo của các extension `contentScript.js`, `Smart Unit Converter` không phải lỗi MATH_WEB.

Lưu ý: bản vá này sửa lỗi HTTP 400 do ID chủ đề; không chứng minh toàn bộ hệ thống hay 1000 dạng/chủ đề đã hoàn thành.
