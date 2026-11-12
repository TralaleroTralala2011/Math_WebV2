# V81: Kiểm toán ngân hàng theo lô

Kế thừa V80, không thay đổi câu hỏi hoặc tính năng cũ.

Chạy: `python tools/bank_scale_audit.py backend/app/ai/verified_seed/verified_seed_bank.jsonl --output bank_audit.json`

Báo cáo số bản ghi, số mã, cặp lớp/chủ đề, số mã không có đúng 10 câu, nhóm phương pháp chia sẻ, mẫu câu hỏi trùng sau chuẩn hóa Unicode và khoảng trắng.

**Không thêm 10.000 mã mới**: tạo 10.000 ID từ vài công thức không đạt tiêu chuẩn 10.000 dạng toán độc lập. Không chứng nhận 100%.
