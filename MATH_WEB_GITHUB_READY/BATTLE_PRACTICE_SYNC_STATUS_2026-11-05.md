# Đồng bộ chấm bài AI và Battle, 05/11/2026

## Đã thực hiện
- Tạo bộ chấm dùng chung `backend/app/questions/answer_checker.py` cho phiên luyện tập và Battle.
- Chấm trắc nghiệm theo nhãn A/B/C/D hoặc nội dung phương án; không dùng logic đúng/sai cho trắc nghiệm.
- Chấm đúng/sai theo giá trị boolean chuẩn, không còn dùng `bool('Sai') == True`.
- Chấm trả lời ngắn theo tương đương toán học hiện có.
- Bộ đề Battle tạo luân phiên theo tối đa hai chủ đề được truyền vào backend, cùng bộ đề phía máy chủ.
- Chặn trùng nguyên văn câu hỏi trong một bộ đề và kiểm tra kiểu câu hỏi.

## Chưa hoàn thành, cần tích hợp tiếp
- Giao diện để **hai người chơi chọn riêng mỗi người một chủ đề** trong toàn bộ thư viện, đồng bộ lựa chọn qua API/phòng chờ; hiện backend chỉ luân phiên theo hai chủ đề *được truyền vào*.
- Phân phối liên tục không giới hạn, phân biệt hàng nghìn dạng bài và tốc độ câu hỏi; trận đấu vẫn giữ giới hạn 10 câu.
- Kiểm thử E2E nhiều tài khoản, UI game, tên game theo chủ đề, các trường hợp lỗi generator.
- Kiểm định toán học độc lập tất cả câu hỏi AI và đáp án; không thể cam kết không lỗi.
