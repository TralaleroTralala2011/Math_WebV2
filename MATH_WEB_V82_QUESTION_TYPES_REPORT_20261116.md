# MATH_WEB V82 | Phân loại dạng trả lời theo đề bài

Nguồn: ZIP đầy đủ MATH_WEB V81 (2026-11-16), giữ nguyên tính năng không liên quan và các file Word, SQLite câu hỏi.

## Sửa đổi
- Chuẩn hóa hiển thị câu hỏi chia hết có mã `1 nếu có, 0 nếu không` thành câu Đúng/Sai hai lựa chọn, không còn các nút 1, 2, 0, 3.
- Sửa cả nhóm Word có dạng học sinh nhận định mã 1/2 là đúng hay sai. Không đồng nhất câu hỏi về nhận định của học sinh với câu chia hết trực tiếp.
- Backend tự tính lại thương/số dư, chỉ chấp nhận nếu đáp án nguồn tương thích; giữ `source_question_original`, `source_answer_original` và `source_options_original` để đối chiếu.
- `true_false` một mệnh đề dùng hai nút rõ ràng Đúng/Sai, khác với loại đúng/sai bốn nhận định dùng các ô tích.
- Các câu trắc nghiệm bốn lựa chọn và trả lời ngắn không bị chuyển đổi tùy tiện. Giữ chế độ chấm theo loại câu tại backend và dự phòng cục bộ khi mạng lỗi.
- Chỉ chuyển đổi khi nhận diện chắc chắn cấu trúc đề, không viết lại câu toán khác hoặc chỉnh sửa ngân hàng SQLite.
- Các trang game đều giữ giao diện cũ; sửa nhãn nút và feedback liên quan tới câu đúng/sai một mệnh đề.

## Kiểm thử
- 40/40 kiểm thử tự động chọn lọc (bộ phân loại, xác thực đáp án, Word và kiểm tra đáp án) đạt.
- 528 trang game, 1.056 đoạn JavaScript nội tuyến đã qua kiểm tra cú pháp (0 lỗi).
- JavaScript kiểm tra lượt chơi ba trò: chặn trùng nguyên văn và trùng cấu trúc chỉ đổi số, cho phép bắt đầu lượt mới.
- Đối chiếu hai kho Word ứng viên: mỗi kho có 250 câu mang cấu trúc mã chia hết, 250/250 chuyển đổi được. Các kho có thể chứa cùng câu; không cộng hai số này thành 500 câu độc lập.
- Các phép kiểm tra này không chứng nhận toàn bộ ngân hàng hoàn toàn đúng toán học hay chống trùng tuyệt đối.

## Lưu ý triển khai
- MATH_WEB V82 kế thừa cơ chế bảo vệ dữ liệu khỏi mất tài khoản trong V81. Render Free không có ổ đĩa bền vững gắn kèm; có thể vẫn không khởi động nếu cấu hình SQLite runtime không an toàn. Không bỏ cơ chế bảo vệ dữ liệu chỉ để ép deploy.
- Nên kiểm thử trên hai tài khoản/trình duyệt thật trước khi khẳng định toàn bộ tính năng hoạt động trên production.
