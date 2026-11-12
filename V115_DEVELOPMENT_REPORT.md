# MATH_WEB V115: Báo cáo triển khai cục bộ (08/11/2026)

## Mục tiêu và hiện trạng

Dự án lấy trực tiếp từ ZIP V114 đã được người dùng cung cấp trong hội thoại trước. Phiên này tập trung **khả năng vận hành liên tục trên một máy**, lưu tiến độ, sao lưu, phục vụ giao diện và điều phối công việc của Question Factory. Không chỉnh sửa giao diện Battle, tài khoản, học tập, lộ trình, chat hoặc cơ sở dữ liệu nguồn.

## Đã làm

- Cấu hình Docker Compose cho bốn dịch vụ: `mathweb-web` (Nginx), `mathweb-api` (FastAPI), `factory-worker` (Question Factory), `factory-operator` (điều phối).
- Thêm `question_factory.operations`: đăng ký 165 dạng ứng viên từ V113/V114, đưa vào hàng đợi **chỉ những dạng đã có trạng thái approved**, xuất `/data/operations/progress-latest.json`, tạo backup SQLite trực tuyến hằng ngày, ghi manifest, kiểm tra `PRAGMA integrity_check`, không ghi đè backup nếu cùng giây, tự thử lại khi lỗi.
- Thêm script Windows `.ps1` tạo secret mạnh cho môi trường Docker cục bộ nếu thiếu `.env`, không yêu cầu kết nối GitHub; script dừng chỉ `stop` dịch vụ, không xóa volume.
- Chạy API theo mô hình Nginx reverse proxy để frontend cùng origin trên port 8080; giữ đường dẫn API cũ cho GitHub Pages và localhost:5500.
- Giữ API hành vi cũ, hạn chế Docker web image chỉ chứa các file frontend công khai, không nhúng source Python hoặc CSDL lên web image; `.env` được loại khỏi build context.

## Kiểm thử

- Các bài test backend thông thường: **151 đạt**, chạy thành hai lần: 150 test trước khi bổ sung test backup trùng giây, 1 test mới sau đó (nhóm vận hành 6/6 đạt).
- Các bài test API và chất lượng verified bank lớn: **7 đạt**. Tổng **158 test** đạt trong các lần chạy tách nhóm.
- Kiểm tra cú pháp JavaScript `node --check js/api-config.js`: đạt.
- Cấu trúc compose YAML, service dependency, restart policy và bind loopback: kiểm tra được bằng PyYAML.
- **Chưa** chạy được `docker compose up` hoặc `nginx -t`: môi trường kiểm thử không có Docker/nginx. **Chưa** kiểm thử tải cao, TLS, thiết bị thật hoặc VPS.

## Mục tiêu 300.000 dạng, 3.000.000 câu

150 chủ đề đã có tên trong danh mục; 165 blueprint mới V113/V114 vẫn ở trạng thái ứng viên. Chưa có chứng nhận độc lập giữa các dạng, nên không thể tuyên bố hoàn thành 2.000 dạng/chủ đề. Worker hiện **không tự nghiên cứu dạng mới**; chỉ thực thi những bộ tạo đã có và đã được duyệt. Số câu ngân hàng cũ 344.280 là số bản ghi, không phải số câu chứng nhận sư phạm đầy đủ. Việc tạo đủ 3 triệu câu và nâng cấp toàn diện các phân hệ vẫn chưa hoàn thành.

## Để đưa lên VPS thật

1. Chuẩn bị VPS (Docker Compose, ổ lưu trữ bền vững, tên miền, HTTPS, backup off-host). Không chia sẻ mật khẩu qua chat.
2. Sao lưu CSDL trước khi đổi phiên bản; kiểm tra các secrets ở `.env`.
3. Chạy thử `docker compose -f docker-compose.mathweb.yml up -d --build` trong mạng riêng, xác minh API, giao diện, login, Battle, WebSocket.
4. Chỉ sau khi kiểm toán bảo mật, TLS, cấu hình reverse proxy, backup/restore và giám sát mới cho truy cập công khai.
5. Để đạt khối lượng lớn nhiều máy, phải chuyển SQLite sang PostgreSQL + hàng đợi phân tán và triển khai bộ thẩm định dạng độc lập.

**Tình trạng cuối:** đã thêm cấu hình + mã chạy lâu dài và các test trong dự án; chưa có hệ thống nào được triển khai Internet, chưa hoàn thành 100% các yêu cầu học tập, Battle, chat và 3 triệu câu.
