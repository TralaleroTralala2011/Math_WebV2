# MATH_WEB V67 — Sửa MathGeo Studio dựa trên V65

## Phạm vi
- Cơ sở: MATH_WEB V65, không lấy ZIP V59 làm nền; V59 chỉ được đối chiếu chức năng.
- Tệp nguồn sửa: `geometry-studio.html`. Các tệp và dữ liệu khác được bảo toàn.
- Xóa hoàn toàn thẻ và mã thực thi của bảng nổi **📏 Đo đạc và chú thích**. Giữ công cụ đo khoảng cách trong bảng dựng 3D riêng.
- Bổ sung sáu nút khối 3D để có 13 mẫu trực tiếp, trạng thái nút được chọn và thông báo phản hồi.
- Vẽ các mặt bán trong suốt trên những khối đa diện hỗ trợ, giữ các cạnh khuất nét đứt và trục Ox/Oy/Oz.
- AI dựng hình theo mô tả: nhấn ví dụ có thể dựng ngay; bổ sung ví dụ đường thẳng Oxyz và hình hộp; cải thiện nhận diện tên hình.
- Sửa cách giải mã tỉ lệ AB = 2CD của hình thang vuông: AB/CD = 2, không đảo ngược; dựng AD vuông góc với hai đáy.
- Mobile: chọn mẫu hoặc sinh hình thành công tự đóng bảng công cụ, trả `scrollTop` của vùng làm việc về 0 và căn vừa hình. Trước sửa, khi duyệt danh sách dài vùng làm việc bị cuộn ngầm, dẫn đến khung vẽ bị cắt.
- Làm gọn thông số tọa độ 3D (3 chữ số thập phân trong bảng), tối đa 18 dòng hiển thị; dữ liệu mô hình không bị làm tròn.

## Kiểm thử
- `node --check`: tất cả các khối JavaScript nội tuyến có mã đều đạt.
- Playwright/Chromium với nội dung HTML nhúng trong trang kiểm thử: 13/13 nút mẫu tạo hình 3D trên desktop và mobile, 3D tự thêm điểm, undo/redo; phân tích hình thang có AB=2CD; dựng đường thẳng đi qua M(3;-3;4) có vectơ chỉ phương (-3;3;-3); không ghi nhận lỗi JavaScript.
- Thử nghiệm giao diện dùng CSS fallback tại 1280 × 800 và 390 × 800: canvas có kích thước hợp lệ. Sau sửa, canvas mobile ở y = 116 thay vì y = -239 khi chọn mẫu từ ngăn kéo.

## Giới hạn
- Phần AI dựng hình hiện là **bộ nhận dạng mẫu theo mô tả**, không phải mô hình ngôn ngữ có khả năng hiểu/chứng minh mọi giả thiết hình học. Mỗi hình tạo từ đề vẫn cần đối chiếu dữ kiện trước khi dùng trong bài toán.
- Không kiểm tra được trực tiếp bản GitHub Pages/Render đang chạy. Cần triển khai frontend và kiểm tra tương tác thực tế sau khi cập nhật; nên tải lại mạnh để tránh cache cũ.
- Tham khảo MathDA (https://mathda.com/calculator/vi) về bố cục rõ ràng, nút dễ nhận biết. Đây là trang **máy tính khoa học**, không phải bộ dựng 3D; không lấy mã từ trang đó.
