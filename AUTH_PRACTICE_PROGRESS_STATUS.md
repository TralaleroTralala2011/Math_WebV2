# MATH_WEB 05/11/2026: Đăng nhập và lưu bài luyện tập

- Các trang luyện tập, lộ trình, tài khoản, Battle, Chat, bạn bè chuyển về đăng nhập nếu thiếu token. Đây là kiểm tra điều hướng frontend; backend vẫn phải kiểm tra quyền truy cập trên từng API.
- Kết quả kiểm tra đầu vào lưu riêng theo tài khoản trên cùng trình duyệt.
- Luyện tập AI lưu tạm bộ câu hỏi, vị trí và điểm vào localStorage riêng từng tài khoản; khi mở lại cửa sổ luyện tập có nút tiếp tục. Dữ liệu lưu 7 ngày, phụ thuộc token phiên và trạng thái câu hỏi còn hiệu lực trên máy chủ. Không đảm bảo tiếp tục được nếu phiên câu hỏi server đã hết hạn.
- Chưa xây dựng ngân hàng 2.000 dạng bài độc lập cho mỗi chủ đề. Với 150 chủ đề, yêu cầu tương ứng 300.000 dạng và 1,5–3 triệu câu; không thể tuyên bố đạt được nếu chưa có kho dữ liệu, kiểm chứng toán học và kiểm thử chống trùng.
- Chưa kiểm thử browser/backend end-to-end, nên không tuyên bố hoàn thiện 100%.
