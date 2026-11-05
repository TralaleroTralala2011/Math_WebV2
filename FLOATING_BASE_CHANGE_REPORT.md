# MATH_WEB: nâng cấp có kiểm soát từ bản nền được chỉ định

**Bản nền DUY NHẤT:** `MATH_WEB_FLOATING_LEARNING_GEOMETRY_NAV_2026-11-05.zip`.

## Các tệp được chỉnh sửa (chỉ 3)
- `js/quick-navigation.js`: ẩn ba nút nếu chưa đăng nhập, trên trang Học bài/Lộ trình/Vẽ hình, trong trang game, và khi overlay luyện tập/game đang hiển thị. Theo dõi thay đổi overlay.
- `geometry-studio.html`: nâng cấp lưới và trục tọa độ theo vùng nhìn khi zoom, giữ các công cụ vẽ khác nguyên trạng.
- `learning-path.html`: nâng cấp màu sắc, thẻ, các chặng học uốn lượn, hiệu ứng nhẹ; không sửa logic lộ trình học.

**Không nhập các hiệu ứng toàn trang hoặc các sửa đổi game từ những ZIP phát sinh sau bản nền.**

## Giới hạn kiểm thử
Đã kiểm tra JavaScript riêng, HTML tồn tại, so sánh mọi tệp khác với ZIP nền và kiểm tra CRC ZIP. Chưa chạy kiểm thử end-to-end trên trình duyệt hoặc đo hình học trong mọi trường hợp. Trạng thái đăng nhập trong quicknav dựa trên localStorage, không thay thế xác thực máy chủ.
