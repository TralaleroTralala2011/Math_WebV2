# MATH_WEB V33: GitHub Pages + Render (hướng dẫn triển khai)

**Lưu ý:** GitHub Pages CHỈ hiển thị giao diện. Đăng nhập, Chat, Battle, ngân hàng SQLite, lộ trình, AI đều cần **backend Render được cập nhật cùng bản**. Không thể sửa 404 chỉ bằng upload HTML lên GitHub.

1. Giải nén và đưa nội dung `MATH_WEB_GITHUB_READY` lên **thư mục gốc của repository** `TralaleroTralala2011/Math_WebV2` (đừng tải mỗi tệp ZIP lên repo). Đảm bảo `index.html`, `backend/`, `js/`, `css/` và `.github/workflows/pages.yml` nằm đúng vị trí.
2. GitHub → Settings → Pages → Source: **GitHub Actions**. Push lên nhánh `main`; workflow `Deploy MATH_WEB static frontend` tự xuất frontend, cố ý không public SQLite, backend hoặc khóa mật.
3. Trên Render, kiểm tra service thực sự phục vụ `https://math-webv2.onrender.com`. Chọn đúng repository và branch mới nhất, root directory **để trống** (repo root), build `pip install -r backend/requirements.txt`, start `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`; cập nhật biến `MATH_WEB_SECRET_KEY` bằng khóa bền vững (không lưu vào repo). Nếu dùng render.yaml làm Blueprint mới, bảo đảm tên và URL trỏ tới CHÍNH service frontend gọi.
4. Triển khai backend trước, sau đó mở `https://math-webv2.onrender.com/health` và xác nhận JSON chứa `features.roadmap_v2`, `features.activity_heatmap`, `features.tutor_recommendations` là `true`. Sau đó kiểm tra `/openapi.json` liệt kê các route.
5. Triển khai GitHub Pages; mở web và dùng **Ctrl+Shift+R**. Xóa API URL cũ trong localStorage chỉ khi đang bị lưu sai, không xóa tài khoản hoặc dữ liệu cá nhân.
6. Nếu Render trả 404 ở `/api/roadmap-v2/...` nhưng ZIP mới đã có router: phần backend trên Render vẫn chưa chạy cùng phiên bản, hoặc đang trỏ nhầm service. Xác minh logs/deploy SHA trên Render.

**Bảo toàn dữ liệu:** Render mặc định có thể dùng hệ tệp tạm thời và SQLite sẽ mất dữ liệu khi redeploy/restart nếu không cấu hình lưu trữ bền vững. Phải sao lưu tài khoản và ngân hàng trước deploy và cấu hình database/disk bền vững trước khi dùng thật. ZIP nguồn không gồm mật khẩu, database tài khoản hoặc secret key.

**Chế độ degrade an toàn:** Dashboard kiểm tra `/health` một lần. Nếu một backend cũ thiếu thông tin feature, phần thống kê phụ sẽ hiện trạng thái chưa có dữ liệu thay vì gửi liên tiếp các route 404. Battle, Chat và Lộ trình học vẫn yêu cầu backend đầy đủ.

**MathGeo trên điện thoại:** nút công cụ nằm ở thanh dưới, chạm để dựng điểm/đoạn/tròn; 2 ngón để thu phóng; ngón tay kéo điểm trong chế độ chọn. Không cần đăng nhập để thao tác trực tiếp trên một trang mẫu HTML nhưng website có bảo vệ truy cập theo trạng thái tài khoản hiện hành.

**Giới hạn kiểm thử:** test backend và kiểm thử cấu trúc không chứng minh toàn bộ luồng tài khoản/Battle/Chat vận hành trên GitHub+Render thật. Cần chạy kiểm thử end-to-end trên URL sau khi triển khai.

Lý do cần deploy từ repo root: backend Roadmap và thư viện Toán sử dụng `learn-assets/` và `placement-exams/` ở gốc dự án; nếu Render chỉ tải mỗi `backend/` sẽ thiếu dữ liệu khi khởi động.
