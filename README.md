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
- Câu hỏi hình học hiển thị hình SVG theo dữ liệu hình học mà backend trả về; bài toán nhiều ý có thể dùng chung dữ kiện và hình.
- Thành tích từng trò chơi được lưu trong trình duyệt. Đây là lưu cục bộ, không tự đồng bộ giữa các thiết bị.

Xem `UNIFIED_FEATURES_2026-10.md` và `LOCAL_RUN.md` để biết chi tiết. Trên Windows, có thể chạy nhanh bằng `START_BACKEND.bat` và `START_FRONTEND.bat`.
