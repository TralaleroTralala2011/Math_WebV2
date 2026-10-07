# MATH WEB

Nền tảng luyện Toán bằng HTML/CSS/JavaScript + FastAPI, có 45 game và AI sinh câu hỏi nội bộ.

## AI Question Engine 4.0

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
- `practice.html`: khu luyện tập.
- `battle.html`: PvP.
- `account.html`: tài khoản.
- `chat.html`: chat.
- `games/`: 45 game.
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
