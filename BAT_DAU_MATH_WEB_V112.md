# MATH_WEB V112: chạy không cần GitHub

**Không cần GitHub và không cần nhập mã xác thực GitHub để dùng bản ZIP này.** Đây là bản nâng cấp trực tiếp trên ZIP V111 người dùng gửi, không phải bản rebuild dựa trên một repository khác.

## A. Chạy trên Windows

1. Giải nén ZIP. Mở Terminal tại thư mục `MATH_WEB_GITHUB_READY` (thư mục có `backend`, `index.html`, `CHAY_BACKEND.bat`).
2. Cài Python 3.11 hoặc 3.12. Cài thư viện:

   ```powershell
   python -m pip install -r backend/requirements-question-factory.txt
   python -m pip install pytest httpx
   ```

3. Cửa sổ thứ nhất, đặt mật khẩu bootstrap khi khởi tạo DB mới, và token nếu muốn điều khiển qua dashboard:

   ```powershell
   $env:MATHWEB_BOOTSTRAP_ADMIN_PASSWORD="YOUR_UNIQUE_STRONG_ADMIN_PASSWORD"
   $env:QF_ADMIN_TOKEN="YOUR_SEPARATE_LONG_RANDOM_FACTORY_TOKEN"
   ```

   **Không gửi các mật khẩu này vào chat hoặc GitHub.** Nếu dữ liệu Admin cũ đã tồn tại, mật khẩu phải được thay đổi qua quy trình quản trị an toàn, không chỉ thay biến môi trường.

   Sau đó khởi động **backend MATH_WEB**:

   ```powershell
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

4. Cửa sổ thứ hai, tại **thư mục gốc**:

   ```powershell
   python -m http.server 5500
   ```

   Truy cập `http://127.0.0.1:5500/index.html`. Xem bảng giám sát Question Factory tại `http://127.0.0.1:5500/factory-dashboard.html`.

5. Cửa sổ thứ ba, chạy `CHAY_QUESTION_FACTORY.bat`. Worker độc lập sẽ kiểm tra hàng đợi 5 giây/lần. **Nó không tự tạo 3 triệu câu**; chỉ tạo câu cho các dạng đã duyệt, có engine kiểm chứng và nằm trong hàng đợi.

## B. Thử 9 dạng ví dụ an toàn

Từ thư mục gốc, mở PowerShell:

```powershell
$env:PYTHONPATH="backend"
python -m question_factory.cli init
python -m question_factory.cli seed-demo
python -m question_factory.cli status
python -m question_factory.cli approve-type linear-equation --reviewer "Teacher"
python -m question_factory.cli enqueue --per-type 10
python -m question_factory.cli run --workers 4
python -m question_factory.cli status
```

Các dạng mẫu được đưa vào **danh mục đúng 150 chủ đề**, không tạo thêm 7 chủ đề giả. Ban đầu tất cả ở trạng thái `pending`, không xuất bản cho học sinh. **Chỉ duyệt dạng thực sự đã được thẩm định nội dung.** Các câu sau khi kiểm tra SymPy sẽ có thể lấy qua API `/api/factory/next?topic_id=phuong_trinh&surface=practice`; gửi đáp án qua `/api/factory/answer` bằng `session_id`.

## C. Chạy liên tục trên máy chủ của bạn

Cần một máy chủ có Docker, ổ cứng bền vững, mạng, HTTPS reverse proxy, backup và giám sát. Đây **không phải dịch vụ đã được triển khai online trong phiên chat**.

Tại máy chủ, trong thư mục gốc:

```bash
cp .env.mathweb.example .env
# Sửa .env: thay giá trị `QF_ADMIN_TOKEN` **và** `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` bằng **hai** bí mật dài, khác nhau
# KHÔNG commit .env hoặc chia sẻ token

docker compose -f docker-compose.mathweb.yml up -d --build
docker compose -f docker-compose.mathweb.yml ps
docker compose -f docker-compose.mathweb.yml logs -f factory-worker
```

- `mathweb-api`: FastAPI MATH_WEB, mặc định chỉ mở trên `127.0.0.1:8000` của máy chủ.
- `factory-worker`: 4 luồng worker, theo dõi hàng đợi và tự chạy lại khi container thoát.
- `mathweb-data`: volume dùng chung, lưu SQLite bền vững khi container được tạo lại.
- **Không chạy nhiều server API/worker trên nhiều host với SQLite**, không có bảo đảm high availability. Muốn 3 triệu câu cần PostgreSQL, hàng đợi task phân tán, giới hạn API và giám sát tài nguyên. Để phục hồi sau mất máy chủ phải có bản sao lưu tại nơi khác.
- Dữ liệu tài khoản hiện hữu trong `backend/database/mathweb.db` **không được tự động nhập vào Docker volume mới**. Phải backup và lập kế hoạch migration trước khi dùng dữ liệu người thật; không sao chép DB SQLite đang ghi mà không tạo bản sao nhất quán.
- Frontend HTML/CSS/JS cũ vẫn ở thư mục gốc, không được Docker Compose này tự công bố. Cần thêm hosting tĩnh và HTTPS cho frontend khi lên production.
- Cấu hình `QF_ADMIN_TOKEN` chỉ dành cho quản trị API; **không lưu token vào website công khai hoặc chia sẻ với học sinh**.

## D. Tự kiểm thử trước khi cập nhật

```powershell
$env:PYTHONPATH="backend"
python -m pytest -q backend/tests
node --check js/battle.js
node --check js/practise.js
node --check js/practice-mathgeo-bridge.js
node tools/v96_mathgeo_runtime_test.cjs geometry-studio.html
node tools/v97_triangle_sss_test.cjs geometry-studio.html
python tools/audit_v111_seed_stream.py
```

**Giữ nguyên giao diện đã khóa.** Kiểm thử thực tế trên hai trình duyệt, điện thoại, tablet và phục hồi sau restart vẫn cần thực hiện trước khi đưa vào production. Không được sử dụng trực tiếp bản này cho người dùng thật nếu chưa backup dữ liệu và kiểm thử hạ tầng.

## E. Kết nối GitHub không bắt buộc

ZIP chạy trên Windows không đòi liên kết GitHub với ChatGPT. Khi muốn đưa code lên repository, có thể đăng nhập GitHub từ máy tính của bạn và tự `git add`, `commit`, `push`; không cần gửi mật khẩu hay mã OTP cho ChatGPT. Nếu GitHub yêu cầu authenticator, nên dùng phương pháp khôi phục tài khoản chính thức, không tìm cách bỏ qua bảo mật.

**Cảnh báo bảo mật**: mã V111 có sẵn giá trị mật khẩu bootstrap admin dự phòng trong database.py. Cấu hình Docker V112 từ chối khởi động nếu chưa có biến môi trường `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD`. Trên Windows cũng nên đặt biến này trước lần chạy đầu nếu bạn tạo cơ sở dữ liệu mới. Các tài khoản admin hiện có không bị sửa mật khẩu chỉ vì thay biến môi trường.
