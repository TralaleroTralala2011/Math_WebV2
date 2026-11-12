# MATH_WEB V128 · Kiểm toán nguồn phương pháp và trạng thái duyệt

Nền: V127 (bản ZIP mới nhất trong hội thoại). Chỉ thêm công cụ đọc dữ liệu, kiểm thử và báo cáo; không thay đổi mã runtime, ngân hàng công khai, Battle hay giao diện.

- Rà trực tiếp **1.050 dạng ứng viên** và **10.500 câu** V123, thuộc **150 chủ đề**, 7 dạng ứng viên/chủ đề và 10 câu/ứng viên.
- Phát hiện **150 phương pháp nguồn**; mỗi phương pháp nguồn được tái sử dụng ở **7 cấu trúc ứng viên**. Tất cả 1.050 cấu trúc được gắn cờ dùng chung lõi phương pháp.
- Có **8 nhãn phép xử lý** trong dữ liệu (không tương đương 8 phương pháp toán độc lập); một số chủ đề dùng tập con các phép xử lý.
- **0 dạng độc lập được chứng nhận**, **0 dạng mới**, **0 câu mới** trong V128.
- Không phát hiện sai trạng thái chờ duyệt, chứng nhận nhầm, hoặc thiếu bộ 10 câu trong phạm vi dữ liệu V123.
- Unit test mới: **6/6 đạt**. Chưa chạy hồi quy backend/frontend toàn diện. Kiểm tra này không xác minh đáp án toán học hoặc tính phù hợp chuyên đề.
- Mục tiêu trung gian: **75.000 dạng độc lập / 750.000 câu**. Không cộng 1.050 ứng viên chưa duyệt vào số dạng độc lập.

Kết quả chi tiết: `V128_RESULTS.json`. Công cụ: `backend/question_factory/v128_method_audit.py`.
