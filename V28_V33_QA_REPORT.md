# MATH_WEB V33 · GitHub/Render + MathGeo Mobile

## Những phần thực hiện

- Thêm `/health.features` để frontend chỉ gửi API thống kê phụ khi backend đã hỗ trợ, tránh đợt 404 `/api/roadmap-v2/tutor/10`, `/api/roadmap-v2/status/10..12`, `/api/games/activity-heatmap` trên backend cũ. Một lệnh `/health` dùng chung cho trang. Khi endpoint chưa được triển khai, hiển thị trạng thái chưa có dữ liệu, không tạo thống kê giả.
- Đồng bộ `render.yaml`: service `math-webv2`, build từ repository root (`backend/requirements.txt`), dùng `uvicorn --app-dir backend` để máy chủ vẫn đọc được `learn-assets` và `placement-exams`. **Không thể tự triển khai Render từ môi trường này.**
- Bổ sung `.github/workflows/pages.yml` triển khai frontend bằng GitHub Actions, loại trừ `backend`, SQLite và bí mật khỏi GitHub Pages.
- Sửa `geometry-studio.html` để kích thước bitmap khớp kích thước thực tế của canvas, không tràn vùng vẽ/toolbar; giảm redraw trùng bằng `requestAnimationFrame` và giới hạn DPR=2 trên điện thoại.
- Bổ sung CSS/JS thanh hướng dẫn cảm ứng cho MathGeo, giữ tính năng dựng điểm/đoạn/tròn, kéo, pinch zoom, hoàn tác.
- Giữ màu giao diện V28, hiệu ứng SortLab, Battle/Chat/Auth/Practice và dữ liệu ngân hàng B54 không sửa.

## Kết quả kiểm thử

- **Kiểm tra contract API:** 4 bài kiểm thử backend được chọn đạt; `health` có feature flags và ba routes tồn tại trong backend đóng gói.
- **Kiểm thử API gate bằng Node:** backend cũ chỉ bị gọi `/health` một lần (không gọi ba endpoint 404); backend mới có 1 `/health` và 3 API request.
- **Kiểm thử Chromium set_content:** viewport điện thoại 390×844, nút công cụ hiển thị, chạm thêm điểm thành công, hai ngón thu/phóng thành công; viewport desktop 1365×768, bitmap khớp CSS canvas; không lỗi JavaScript trong hai trường hợp mô phỏng.
- **Tài nguyên cục bộ:** 20 trang HTML ở root, **0 link thiếu**.
- **Ngân hàng B54:** SQLite quick_check=`ok`, `83298` câu ứng viên và `95514` nhãn B54, SHA-256 file SQLite không đổi so với V32. Đây không phải chứng nhận toán học độc lập.
- **Giữ nguyên mã:** 1969 file gốc V32 giữ nguyên từng byte; danh sách 9 file gốc chỉnh sửa ghi trong JSON.

## Cần làm trên GitHub/Render

1. Đưa các file con của thư mục `MATH_WEB_GITHUB_READY` vào repo root; đừng chỉ tải tệp ZIP lên GitHub.
2. Settings → Pages → Source = GitHub Actions.
3. Redeploy **CHÍNH backend** tại `https://math-webv2.onrender.com` với root repo và lệnh từ `render.yaml`, cập nhật `MATH_WEB_SECRET_KEY` giữ bền vững, lưu DB tài khoản trên storage bền vững.
4. Kiểm tra `/health` có `features` và ba endpoint trong `/openapi.json`.
5. Sau khi deploy hai bên, dùng trình duyệt thật để thử đăng nhập, hai tài khoản Battle/Chat, luyện tập, thiết bị iOS/Android.

**Giới hạn:** Chưa thể xác nhận 100% không lỗi trên máy chủ GitHub/Render thật vì không có quyền deploy vào tài khoản người dùng, cũng chưa có thử nghiệm end-to-end trên URL production. Cảnh báo forced reflow 59/67ms không phải lỗi 404, có thể vẫn xuất hiện tùy thiết bị.
