# MATH WEB

Nền tảng luyện Toán bằng HTML/CSS/JavaScript + FastAPI, có 45 game và AI sinh câu hỏi nội bộ.

## AI Question Engine + Unified Gameplay 6.2

MATH WEB không gọi ChatGPT hay API AI bên ngoài để sinh câu hỏi. AI nội bộ dùng **Template Bank** làm kho dữ liệu nền, sau đó Composer/Generator tự chọn kiến thức, dạng bài, dữ kiện, kiểu hỏi, ngữ cảnh và độ khó để xây câu hỏi.

Luồng sinh câu hỏi:

```text
Template Bank
    ↓
AI Composer / Generator
    ↓
Question + Answer + Solution
    ↓
Math Validator
    ↓
Duplicate / Structure Detector
    ↓
Game / Practice
```

Template Bank có dữ liệu riêng cho toàn bộ 45 game, gồm problem families, question styles, contexts và các quy tắc của từng game. Bộ sinh còn có các dạng lý thuyết, tính toán, suy luận, bài ngược, ứng dụng, tình huống thực tế và derived tasks.

Mỗi câu được kiểm tra đáp án ở backend trước khi trả cho người chơi. Các câu trong cùng bộ không được trùng nguyên văn; engine cũng lưu `structure_fingerprint` để theo dõi độ giống cấu trúc.

## Chạy local

### Backend

Mở PowerShell:

```powershell
cd "C:\duong-dan-den-MATH_WEB\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

Mở PowerShell thứ hai:

```powershell
cd "C:\duong-dan-den-MATH_WEB"
python -m http.server 5500
```

Mở:

```text
http://127.0.0.1:5500/
```

## Cấu trúc chính

- `index.html`: trang chủ.
- `practise.html`: khu luyện tập chính (`practice.html` được giữ để tương thích liên kết cũ).
- `battle.html`: PvP.
- `account.html`: tài khoản.
- `chat.html`: chat.
- `games/knowledge/`: 276 trang game độc lập, gồm 92 chủ đề × 3 game riêng; `games/` cũng giữ các trang game cũ.
- `backend/app/ai/knowledge/template_bank.json`: Template Bank của 45 game.
- `backend/app/ai/engine/composer.py`: bộ chọn template, kiểu hỏi, ngữ cảnh và derived task.
- `backend/app/ai/engine/game_bank.py`: bộ sinh toán theo game.
- `backend/app/ai/engine/generator.py`: AI Generator trung tâm.
- `backend/app/ai/engine/validator.py`: kiểm tra câu hỏi/đáp án.
- `backend/app/ai/engine/duplicate.py`: fingerprint chống trùng.
- `backend/app/ai/engine/service.py`: dịch vụ AI, lưu câu hỏi và adaptive difficulty.
- `backend/app/ai/routes.py`: API AI.
- `backend/app/matchmaking/`: matchmaking PvP.

## GitHub

Repository có thể đưa lên GitHub. Database local `mathweb.db`, cache Python và file môi trường riêng không được đóng gói vào bản source phát hành.

GitHub Pages chỉ phục vụ frontend tĩnh. Đăng nhập, AI, database, matchmaking và PvP cần FastAPI backend được deploy riêng.


## Gameplay thống nhất mới

- Trong trang chơi không còn nút chọn Dễ/Vừa/Khó; độ khó được xoay vòng nội bộ.
- Thanh tiến độ tính từ 0 đến 100: đúng +5, sai −1, không âm; đạt 100 thì hiện màn chúc mừng hoạt họa.
- Sau khi trả lời, trò chơi dừng để người học đọc đáp án và lời giải; phải bấm **Đọc xong, câu tiếp theo** mới tiếp tục.
- Bộ câu hỏi trộn trắc nghiệm, trả lời ngắn và nhận định đúng/sai khi API hỗ trợ.
- Câu hỏi hình học hiển thị nhiều loại hình SVG như tam giác, tứ giác, hình thang, hình thoi, đường tròn có dây/tiếp tuyến, hình chóp và mặt phẳng tọa độ. Hình minh họa được ghi chú khi không theo tỉ lệ.
- Ngân hàng hệ phương trình có bài giải hệ trực tiếp, tổng-hiệu, hệ hệ số khác nhau, hệ cần rút gọn, tìm biểu thức từ hệ, kiểm tra nghiệm và bài toán thực tế. Ba game hệ phương trình hiện có cũng dùng các cấu trúc khác nhau theo cấp độ.
- Chủ đề Hình học phẳng lớp 10 có 18 họ bài nguyên bản từ nền tảng đến nâng cao, trong đó mức nâng cao bổ sung định lý phân giác, tiếp tuyến-cát tuyến, tích hai dây và suy luận chứng minh.
- Thành tích từng trò chơi được lưu trong trình duyệt. Đây là lưu cục bộ, không tự đồng bộ giữa các thiết bị.

Xem `UNIFIED_FEATURES_2026-10.md` và `LOCAL_RUN.md` để biết chi tiết. Trên Windows, có thể chạy nhanh bằng `START_BACKEND.bat` và `START_FRONTEND.bat`.


## Kiểm thử và chẩn đoán

Sau khi cài backend, có thể cài thêm công cụ kiểm thử và chạy regression tests:

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Nếu trình duyệt báo CORS khi ghép trận, trước tiên kiểm tra `http://127.0.0.1:8000/health` và khởi động backend đúng thư mục bằng `START_BACKEND.bat`. Một lỗi backend 500 có thể bị trình duyệt hiển thị thành lỗi CORS, vì vậy hãy xem cả cửa sổ terminal backend. Xem `AUDIT_FIX_REPORT.md` để biết các sửa lỗi và phạm vi kiểm thử của bản này.

## Bổ sung AI tạo đề và dựng hình theo dữ kiện (16/10/2026)

- `AI_GENERATION_AND_GEOMETRY_REQUIREMENTS_2026-10-16.md`: tiêu chí sản phẩm cho AI tạo đề đa dạng, kiểm chứng đáp án, chống lặp, dựng hình 2D/3D và tích hợp Practice/Game/Battle.
- `AI_UPGRADE_IMPLEMENTATION_NOTES_2026-10-16.md`: các thay đổi đã đưa vào bản ZIP này và giới hạn còn lại.
- Backend dựng hình giữ lại tọa độ Oxyz và kích thước hình hộp; hình hộp chữ nhật lưu tọa độ 3D chính xác của cả tám đỉnh.
- Với hình có dữ liệu 3D, vùng hình học SVG hỗ trợ xoay trái/phải, nghiêng lên/xuống và đặt lại góc nhìn. Đây là wireframe chiếu 2D có tương tác, chưa phải phần mềm dựng hình 3D đầy đủ kiểu GeoGebra/CAD.
- Các payload hình học cũ có số liệu được chuẩn hóa thành hình theo dữ kiện; bộ kiểm tra từ chối hình rỗng, tọa độ không hợp lệ hoặc ràng buộc hình học mâu thuẫn.
- Kiểm thử tự động trong bản này: `python -m pytest -q` (70 tests). Một lượt kiểm tra độc lập sinh và xác minh 846 câu trên 94 chủ đề, 3 cấp độ và 3 loại câu hỏi; 270 câu có hình, không có lỗi trong lượt kiểm tra đó.
- Ghi chú chi tiết: `AI_UPGRADE_IMPLEMENTATION_NOTES_2026-10-16.md`. Bộ sinh vẫn là AI nội bộ theo ngân hàng dạng bài và quy tắc, không phải LLM tổng quát; những cấu hình không đủ dữ kiện vẫn phải được ghi nhận là hình sơ đồ.


## Hệ thống quản trị MATH WEB

- Mở `admin.html` sau khi chạy frontend và backend.
- Tài khoản bootstrap duy nhất: `admin19022011`. Mật khẩu khởi tạo: `adminsitinh`.
- Đăng nhập lần đầu, chọn **Đổi mật khẩu** và đổi mật khẩu ngay. Không triển khai hệ thống công khai với mật khẩu mặc định.
- Backend xác thực quyền quản trị tại `/api/admin/*`; sửa giao diện hoặc gọi API trực tiếp không thể tự cấp quyền admin.
- Bảng quản trị gồm tổng quan, tìm kiếm tài khoản, hồ sơ học tập, cấm/mở cấm, đặt lại mật khẩu người dùng, ngân hàng câu hỏi và nhật ký quản trị.
- Câu hỏi do admin thêm được đưa vào nguồn sinh đề khi khối, tên chủ đề, mức độ, loại câu hỏi và mã trò chơi khớp với yêu cầu. Để trống mã trò chơi cho luyện tập chung; nhập đúng `game_id` để nhắm tới một trò chơi cụ thể. Trắc nghiệm cần đúng 4 lựa chọn khác nhau; đáp án có thể là nhãn A/B/C/D hoặc nội dung lựa chọn.
- Có thể đặt `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD` trước khi tạo cơ sở dữ liệu lần đầu để đổi mật khẩu bootstrap. Khi tài khoản admin đã tồn tại, khởi động lại không tự đặt lại mật khẩu.
- Dữ liệu quản trị nằm trong SQLite `backend/database/mathweb.db`; hãy cấu hình sao lưu và `MATH_WEB_SECRET_KEY` riêng khi triển khai thật.
