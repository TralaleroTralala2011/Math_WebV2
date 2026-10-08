# MATH_WEB AI Question Engine v2

## Vai trò
Module này chịu trách nhiệm tạo, kiểm tra và chấm câu hỏi cho cả **Practice** và **Battle Online**.

## API chính
- `GET /api/ai/health`
- `GET /api/ai/knowledge?grade=10`
- `GET /api/ai/knowledge/{topic_id}`
- `POST /api/ai/questions`
- `POST /api/ai/practice/session`
- `POST /api/ai/questions/{question_id}/answer`
- `POST /api/ai/battle/topics`
- `POST /api/ai/battle/create`
- WebSocket `/api/ai/battle/ws/{battle_id}/{user_id}`

## Tích hợp vào app/main.py
Thêm router:

```python
from app.ai.routes import router as ai_router
app.include_router(ai_router)
```

## Luồng Practice
Frontend gửi grade + topics + difficulty + question_type -> `/api/ai/practice/session`.
Server tạo câu, kiểm tra, lưu tạm câu hỏi và trả về bộ câu.
Khi người chơi trả lời, frontend gửi answer -> `/api/ai/questions/{question_id}/answer`.
Server tự chấm và trả feedback/đáp án/lời giải khi sai.

## Luồng Battle
1. Hai người chọn tối đa 5 topic.
2. `/api/ai/battle/topics` lấy phần giao.
3. `/api/ai/battle/create` tạo phòng nếu có topic chung.
4. WebSocket truyền trạng thái realtime.
5. Câu hỏi và chấm điểm vẫn do backend quyết định.

## Lưu ý production
Battle manager hiện giữ trạng thái trong RAM, phù hợp local/single-process. Khi chạy nhiều worker/server, chuyển room/session state sang Redis hoặc database dùng chung.
