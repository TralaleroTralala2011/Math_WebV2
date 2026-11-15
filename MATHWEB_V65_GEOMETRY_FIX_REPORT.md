# MATH_WEB V65 · Geometry Studio repair report

## Nền tảng
- Tạo từ ZIP MATH_WEB V64; đối chiếu CRC các tệp để bảo toàn toàn bộ ngân hàng, backend, tài khoản, Battle và game.
- Người dùng đính kèm V60; không dùng V60 làm nền để tránh mất các bản vá V61–V64.

## Sửa và bổ sung trong geometry-studio.html
- Công cụ chỉnh 3D: thêm/sửa/xóa điểm có tọa độ x,y,z; nối/xóa cạnh; tính độ dài 3D bằng tọa độ.
- Xoay khối bằng kéo, Shift+kéo điểm để chỉnh, cảm ứng chọn/kéo điểm, zoom bằng bánh xe và hai ngón.
- Trục Ox/Oy/Oz, căn vừa mô hình, reset góc nhìn; hỗ trợ đường tròn 3D dạng lưới khung (cylinder, cone, sphere) bên cạnh khối chóp/lăng trụ.
- Undo/Redo bao gồm dữ liệu 3D (bên cạnh 2D).
- Trình sinh hình theo mô tả hỗ trợ một tập mẫu cụ thể và điểm tọa độ A(x;y;z), điểm+vectơ chỉ phương; báo lỗi với mô tả không hỗ trợ thay vì xóa hình cũ.
- Hình chóp có đáy hình thoi/hình bình hành dựng tương ứng; sửa lăng trụ lục giác phải có hai đáy bằng nhau.
- Khi mở geometry-studio.html?mode=3d, chuyển thẳng sang bảng khối 3D.
- Ẩn bảng đo 2D khi đang vẽ 3D; vẫn giữ chức năng đo 2D khi quay lại chế độ 2D.

## Kiểm thử đã thực hiện
- 52/52 unit tests backend hình học đạt (`test_geometry_diagrams.py`, `test_additional_solid_diagrams.py`, `test_geometry_curriculum.py`, `test_neon_v21_geometry_personalization.py`, `test_v63_quadrilateral_relevance.py`).
- Chromium mô phỏng offline tại viewport 1260x850 và 390x800: chọn khối, dựng đường qua M(3;-3;4) theo vector u=(-3;3;-3), thêm điểm P, nối cạnh, undo/redo, đo MP, dựng chóp đáy hình thoi; không có JS runtime errors trong lượt thử.
- Kiểm tra cú pháp JavaScript của ba script inline trong Geometry Studio: đạt.
- 48/49 bài kiểm thử hồi quy về ngân hàng, chủ đề, bạn bè và Battle đạt. Bài thất bại thuộc V50, mong đợi Battle bắt đầu ngay ở `PLAYING`; backend hiện bắt đầu tại `SELECTING` đúng luồng hai người chọn chủ đề ở bản mới. Không sửa ngược hành vi Battle.

## Giới hạn kiểm chứng
- Chưa thử trên GitHub Pages + Render thật hoặc các thiết bị vật lý.
- Trình phân tích mô tả là hệ thống nhận diện mẫu và tọa độ trong HTML, không phải AI đa năng có thể suy ra mọi điều kiện hình học. Cần kiểm tra thủ công các giả thiết chưa được hỗ trợ.
- Chưa thể xác nhận toàn bộ chức năng của hàng nghìn trang game và toàn bộ câu hỏi đã hết lỗi; đây là bản sửa tập trung MathGeo Studio và bảo toàn các phần còn lại.
- Để dùng tại máy chủ cần cập nhật frontend và backend nhất quán, kiểm tra Render sau deploy.
