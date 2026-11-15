# MATH_WEB V69 - Sửa lỗi không dựng được mô hình 3D

**Nền mã nguồn:** MATH_WEB V68, kế thừa các thay đổi của V67.
**Phạm vi:** 2 file mã nguồn, không sửa backend, ngân hàng câu hỏi, tài khoản hay dữ liệu.

## Nguyên nhân tái hiện
`js/unified-navbar-v55.js` dùng `shouldReplaceHeader()` kiểm tra chuỗi `MATH` trong toàn bộ header. Thanh công cụ MathGeo Studio chứa tên `MathGeo Studio Pro`, nên bị script thay bằng navbar chung. Kết quả: `#view-mode-2d`, `#view-mode-3d` và `#bar-fx-container` bị xóa khỏi DOM. `switchMode()` tiếp tục gọi `...style.display` trên `null`, dẫn tới lỗi `Cannot read properties of null (reading 'style')`.

## Sửa lỗi
1. Navbar chung không được thay header MathGeo có các điều khiển `view-mode-2d`, `view-mode-3d` hoặc `bar-fx-container`. Thay vào đó navbar được chèn riêng và vẫn giữ thanh công cụ 2D/3D.
2. Hàm `switchMode()` kiểm tra tồn tại của `bar-fx-container` trước khi thay đổi `style`, để không gây sập toàn bộ luồng dựng hình nếu thanh chức năng tùy chọn chưa sẵn sàng.

## Thử nghiệm
- Tái hiện lỗi V68 bằng Chromium: sau khi trang tải, chỉ còn một header, các nút 2D/3D bị mất; bấm cube phát sinh lỗi null.style.
- Bản V69 trên Chromium (HTML nội tuyến, JS tương đương): cả hai header có mặt; các nút 2D/3D được giữ; 13/13 mẫu 3D chuyển mode và nhận dạng hình; không phát sinh lỗi JS.
- Chuyển 3D → 2D → 3D: không lỗi.
- AI dựng hình chóp và đường thẳng theo dữ kiện Oxyz: không lỗi; cập nhật trạng thái.
- Chế độ điện thoại 393×852: bật bảng công cụ, chọn hình cầu và sinh hình Oxyz; không lỗi.
- Cú pháp Node.js (`node --check`) của navbar và hai khối JavaScript nội tuyến: đạt.

**Giới hạn:** Môi trường Chromium tại đây chặn việc mở localhost/file://; thử bằng `page.set_content` với JavaScript thực tế và CSS/JS nội tuyến, không phải kiểm thử deployment trên GitHub Pages/Render. Kết quả không chứng nhận mọi mô hình hình học hoặc chức năng web đúng 100%.
