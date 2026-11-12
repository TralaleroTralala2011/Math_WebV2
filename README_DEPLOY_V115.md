# MATH_WEB V115: triển khai cục bộ, không cần GitHub

**Đây là bản triển khai phần mềm dạng thử nghiệm trên một máy, không phải máy chủ Internet đã được đưa vào hoạt động.** Không có cam kết hoàn thành 300.000 dạng độc lập hay 3 triệu câu. Các dạng V113/V114 vẫn chờ thẩm định.

## Chạy trên Windows (Docker Desktop)

1. Cài Docker Desktop và bật ứng dụng, bảo đảm lệnh `docker info` hoạt động.
2. Giải nén ZIP, mở PowerShell trong thư mục `MATH_WEB_GITHUB_READY`.
3. Chạy `powershell -ExecutionPolicy Bypass -File .\BAT_DAU_MATH_WEB_V115.ps1`.
4. Truy cập `http://127.0.0.1:8080/index.html` (frontend) hoặc `http://127.0.0.1:8000/health` (backend).
5. Xem log: `docker compose -f docker-compose.mathweb.yml logs -f factory-operator factory-worker`.
6. Dừng: `powershell -ExecutionPolicy Bypass -File .\DUNG_MATH_WEB_V115.ps1`.

Script tạo `.env` ngẫu nhiên nếu chưa có; **đừng chia sẻ .env**, đừng chụp màn hình mật khẩu, và đừng ghi đè nếu bạn đã thiết lập .env riêng. Nếu `.env` sẵn có thì phải chứa `QF_ADMIN_TOKEN` và `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` là chuỗi ngẫu nhiên mạnh. Dịch vụ frontend chỉ được bind ở loopback `127.0.0.1:8080`, chưa mở truy cập Internet.

## Các tiến trình

- `mathweb-web`: Nginx phục vụ các tệp HTML/CSS/JS và proxy `/api/`, `/health` về backend.
- `mathweb-api`: FastAPI, giữ các route hiện có, chạy health check.
- `factory-worker`: hàng đợi công việc đa luồng cho **những dạng đã duyệt**.
- `factory-operator`: sau khi bật, tự đăng ký 165 dạng ứng viên của V113/V114, cập nhật jobs đã duyệt, xuất trạng thái định kỳ 5 phút và sao lưu SQLite một lần mỗi 24 giờ.

**Không tự duyệt dạng toán.** Theo thiết kế, trên bản khởi chạy mới sẽ có 165 ứng viên `pending`, 0 dạng được duyệt và 0 việc tự enqueue. Muốn tạo câu thực tế phải có quá trình duyệt độc lập về chất lượng, phương pháp và mức độ phù hợp với từng chủ đề.

## Đường dẫn dữ liệu và báo cáo

- Docker volume `mathweb-data`: `/data/question_factory.sqlite3`, `/data/mathweb.db`, `/data/mathweb_ai_history.sqlite3`.
- Tình trạng: `/data/operations/progress-latest.json`.
- Sao lưu: `/data/backups/YYYYMMDDTHHMMSSZ/*.sqlite3` (SQLite online backup có kiểm tra integrity).
- Xem số liệu: `docker compose -f docker-compose.mathweb.yml exec factory-operator cat /data/operations/progress-latest.json`.
- Sao lưu ngay: `docker compose -f docker-compose.mathweb.yml exec factory-operator python -m question_factory.operations --mode backup --data-dir /data`.
- **Quan trọng:** Docker volume không phải bản sao lưu ngoài máy. Cần sao lưu ngoại vi và kiểm thử khôi phục trước khi sử dụng thật.

## Kiểm thử không cần Docker

Trong thư mục `backend`:

```bash
python -m pip install -r requirements-question-factory.txt
python -m pytest -q tests/test_question_factory_operations_v115.py
python -m question_factory.operations --mode once --data-dir ./database
```

Các lệnh `--mode once` không mở cổng Internet. Nếu muốn tránh chạm vào DB hiện có, sử dụng thư mục dữ liệu riêng, chẳng hạn `--data-dir ./test-data`.

## Những giới hạn quan trọng

1. Đã cung cấp **cấu hình** chạy lâu dài, không chứng minh máy chủ nào đang chạy 24/7.
2. SQLite + Docker volume phù hợp máy đơn/pilot, không phải cụm máy chủ HA. Để chạy đa máy và nhiều yêu cầu đồng thời cần PostgreSQL/hàng đợi phân tán, TLS, giám sát, rate limit và kiểm tra an toàn thông tin.
3. V115 chưa biến các ứng viên thành 300.000 phương pháp khác nhau, chưa triển khai AI agent tự sửa code liên tục, chưa kiểm thử Battle/chat trên thiết bị thực hoặc tải production.
4. Cấu hình `api-config.js` giữ đường dẫn Render của GitHub Pages và localhost:5500 như trước; khi dùng Nginx self-host, mặc định dùng API cùng origin. Nếu đã lưu API URL tùy chỉnh trong trình duyệt, nó sẽ được ưu tiên hơn cấu hình mặc định.
5. Trước khi công khai trên Internet cần kiểm toán bảo mật, quyền truy cập dữ liệu và triển khai HTTPS. **Không mở cổng quản trị ra Internet trực tiếp.**
