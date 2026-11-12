# MATH_WEB V34 · Trước khi thử nghiệm học sinh

## 1. Bản chất triển khai

- **GitHub Pages** phục vụ HTML, CSS, JS và tài liệu tĩnh. GitHub Pages KHÔNG chạy FastAPI, SQLite hay WebSocket.
- **Render** phục vụ `/api/...`, đăng nhập, Admin, Battle WebSocket, Chat và dữ liệu lưu bền vững.
- Cần triển khai **cả hai bên từ cùng phiên bản V34**. Chỉ đẩy frontend lên GitHub chưa đủ.

## 2. Thay đổi cụ thể V34

1. Sửa `curriculum-studio.html`, `study-suite.html`, `final-features.html`, `geometry-lab.html`, `geometry-learning.html` để dùng cấu hình API thống nhất; sửa các tệp JS tương ứng; trên GitHub Pages không gọi nhầm localhost hoặc origin GitHub nữa.
2. `js/api-config.js`: trên tên miền công cộng bỏ qua địa chỉ API được ghi tùy ý trong localStorage, tránh gửi bearer token sang máy chủ lạ.
3. Đóng gói bản nén `backend/app/ai/storage/v254_candidates.seed.zip` (12 MiB) được Git theo dõi. `scripts/restore_v254_bank.py` giải nén thành SQLite **ở thời điểm build Render**, tự kiểm tra SHA-256, `PRAGMA quick_check`, đúng 83.298 câu ứng viên và 95.514 nhãn B54.
4. Định tuyến dữ liệu học tập ghi được (`mathweb.db`, `*_history.sqlite3`, `study_suite.sqlite3`, `final_features.sqlite3`, `learning_progress.sqlite3`) tới thư mục bền vững qua `MATHWEB_DATA_DIR` và `MATHWEB_DB_PATH`.
5. Blueprint `render.yaml` cấu hình đĩa `/var/data`, gói trả phí Render `starter`, mật khẩu khởi tạo Admin từ biến bí mật; không đưa mật khẩu vào file mã nguồn hoặc log Render.
6. `.github/workflows/pages.yml`: khi push chạy kiểm tra ngân hàng, tài nguyên, API route và toàn bộ pytest trước khi xuất bản Pages; chỉ xuất frontend, không xuất `backend`, SQLite, dữ liệu tài khoản hay khóa.

## 3. Đưa lên GitHub

- Giải nén ZIP V34. Tại thư mục chứa file `index.html` và `.github` của ZIP, chuyển **toàn bộ nội dung** vào **gốc** repository `TralaleroTralala2011/Math_WebV2`. Đừng chuyển nguyên thư mục con `MATH_WEB_GITHUB_READY` lên gốc, nếu repo đang dùng bố cục gốc này.
- Khi dùng Git: `git add .`, `git commit -m "MATH_WEB V34 pilot deployment QA"`, `git push origin main`. Git **không commit** `v254_candidates.sqlite` do `.gitignore`; tệp `v254_candidates.seed.zip` cùng manifest và `scripts/restore_v254_bank.py` PHẢI được commit. Kiểm tra bằng `git status` trước và sau commit.
- Tại GitHub > Settings > Pages > Build and deployment > **GitHub Actions**. Xem `.github/workflows/pages.yml` đã xanh. Mục tiêu: `https://tralalerotralala2011.github.io/Math_WebV2/`.

## 4. Render: PHẢI xử lý lưu dữ liệu trước thu thập thật

> **Cảnh báo về chi phí**: Render persistent disk dùng cho dịch vụ web trả phí. File `render.yaml` đề xuất `plan: starter` và disk 1 GB; không có gì trong ZIP tự thanh toán hay tự bật dịch vụ. Xem giá và xác nhận trước khi áp dụng. Nếu chưa có persistent disk/DB bền vững, **không thu thập dữ liệu nghiên cứu thật** trên Render filesystem tạm.

1. Sao lưu SQLite người dùng **hiện có** trên backend trước mọi thay đổi cấu hình. Việc chuyển sang `/var/data` không tự động chuyển database cũ từ một đường dẫn khác. Tuyệt đối không tạo dịch vụ mới rồi bỏ mặc database cũ nếu cần giữ tài khoản hiện có.
2. Với Render web service trỏ tới **đúng repository và nhánh `main`**, Root Directory để trống (gốc repo). **Lưu ý**: Chỉnh file `render.yaml` trên GitHub không nhất thiết đổi cấu hình của service Render đã tạo bằng tay; kiểm tra cả Dashboard.
3. Build: `pip install -r backend/requirements.txt && python scripts/restore_v254_bank.py`.
4. Start: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`.
5. Thêm **persistent disk** mount `/var/data`, 1 GB hoặc hơn; cấu hình biến:
   - `MATHWEB_DATA_DIR=/var/data`
   - `MATHWEB_DB_PATH=/var/data/mathweb.db`
   - `MATHWEB_AI_HISTORY_DB_PATH=/var/data/mathweb_ai_history.sqlite3`
   - `MATH_WEB_SECRET_KEY`: khóa ngẫu nhiên >=32 ký tự, phải duy trì ổn định qua redeploy
   - `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD`: mật khẩu mạnh (>=8 ký tự) chỉ cho lần tạo Admin mới; lưu trong Render Environment, **không commit vào GitHub**.
6. Dùng đúng backend URL đã đặt trong `js/api-config.js`: `https://math-webv2.onrender.com` (nếu service của bạn dùng tên khác, chỉ sửa hằng `productionApi`).
7. Render > Logs: xác nhận build khôi phục B54 thành công. Mở `/health`, phải có `features` tương ứng. Sau đó kiểm tra API qua CORS từ GitHub Pages.

## 5. Chạy smoke test sau triển khai

Trên máy có Internet và Python:

```bash
python scripts/check_live_deploy.py
```

Bài này chỉ kiểm tra **khả năng kết nối, route và CORS**, không thao tác tài khoản thật. Cần tự thực hiện test tích hợp hai người học trên hai thiết bị/trình duyệt:

- A và B đăng ký tài khoản thử. Đăng xuất/đăng nhập lại, chuyển trang, reload, đảm bảo token hợp lệ và dữ liệu không mất.
- A và B kết bạn, nhắn tin realtime, kiểm tra thông báo và đóng một cửa sổ rồi kết nối lại.
- Battle: gửi mời, đồng ý, bắt đầu, đếm giờ, làm đủ câu, kiểm tra hai bên cùng một điểm và kết quả, thử ngắt/khôi phục Wi-Fi.
- Luyện tập: mỗi khối 10/11/12, nhiều chủ đề, thử đáp án đúng/sai, kiểm tra lời giải. Những câu B54 chưa kiểm định độc lập không được xem là chứng nhận chất lượng.
- Vẽ hình: Android và iPhone (nếu có), chạm tạo điểm, kéo điểm, zoom 2 ngón, xoay ngang/dọc.
- **Quan trọng nhất:** tạo bài làm có mã giả (không dùng thông tin cá nhân thật), ghi ID; redeploy/restart backend, kiểm tra bài làm/tài khoản/đánh giá vẫn còn. Sao lưu dữ liệu từ đĩa thường xuyên và hạn chế quyền truy cập.

## 6. Giới hạn xác minh lần này

- Kiểm tra **240/240** test backend trong môi trường tạm, đủ đường dẫn tĩnh 20 trang, 536 tham chiếu, 40 lượt render HTML/CSS tĩnh trên desktop/mobile không tràn ngang, script Node JS không có lỗi cú pháp trong các file JS root.
- Chưa làm một lượt **live E2E trên hai trình duyệt truy cập GitHub Pages+Render thực tế** vì không có quyền cập nhật/kiểm thử dịch vụ của bạn từ môi trường này.
- 95.514 là nhãn câu B54, không phải 95.514 câu được thẩm định sư phạm. Ngân hàng ứng viên B54 vẫn cần kiểm tra lỗi toán học và trùng phương án.
- Bài render tĩnh không bật API/JS nên không chứng minh tất cả màn hình động và hiệu ứng đều đẹp.

**Kết luận:** V34 là bản sửa triển khai và kiểm thử trước pilot. Chỉ khởi động thử nghiệm với người thật khi cả GitHub Pages, Render và lưu trữ bền vững đã vượt qua các bài smoke test thực tế trên thiết bị của bạn.
