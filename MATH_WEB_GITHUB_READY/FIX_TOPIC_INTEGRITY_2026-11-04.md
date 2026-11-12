# Sửa lỗi câu hỏi sai chuyên đề

- Chặn fallback sinh phép cộng chung cho các game khi API thất bại.
- Với 474 trang game chuyên đề, lọc câu hỏi hình học không có dấu hiệu nội dung hình học; từ chối topic_id khác chuyên đề được yêu cầu.
- Với chủ đề g12_geom_3d_optimization, bổ sung ba họ bài toán tối ưu hình hộp/hình trụ, có công thức, đáp án và lời giải.
- Sửa đoạn script thừa bị hỏng trong trang g12_geom_3d_optimization/1-kham-pha.html.
- Nếu không có câu hỏi hợp lệ, hiển thị lỗi và cho tải lại, không tự chuyển sang phép cộng.

**Giới hạn:** Chưa chứng minh mọi câu hỏi do backend sinh đều đúng chuyên đề hoặc đúng toán học; kiểm tra này là lớp phòng vệ bổ sung, không thay thế thẩm định ngân hàng câu hỏi. Các game chưa có câu hỏi phù hợp sẽ tạm dừng thay vì đưa câu sai chủ đề.
