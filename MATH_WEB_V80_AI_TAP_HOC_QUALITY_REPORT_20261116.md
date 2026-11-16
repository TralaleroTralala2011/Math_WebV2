# MATH_WEB V80: AI TẬP HỌC, giữ nguyên Word và ngăn giao đề sai

## Nguồn
- Nền: MATH_WEB V77 đang được dùng để sửa tiếp, giữ các chức năng gọi thoại/video, hồ sơ và bảo vệ tài khoản/Admin sẵn có.
- Tệp Word gốc người dùng cung cấp: `150_CHU_DE_WORD(2).zip`, chứa 150 DOCX.
- Đã đóng kèm bản Word gốc làm nguồn đối chiếu, bên cạnh SQLite Word v62 (không chèn số mới hoặc tự viết lại câu).

## Lỗi được xử lý
1. Bài `Toán 10 · he_bat_phuong_trinh · Chuyên sâu` đang được cấp những câu `a(b+c)` sai chủ đề và thay số hàng loạt. Không tiếp tục dùng AI fallback để lấp bài tập.
2. Chọn câu theo đúng lớp, mã chủ đề, độ khó, phương thức trả lời. Bác bỏ lựa chọn trắc nghiệm thiếu hoặc không hợp lệ.
3. Đối chiếu nguyên văn *đề bài* với tệp DOCX đã gửi. Bỏ các tiền tố ID của đoạn nhập liệu trước đây (vd. `| 019-B20-01-Q01`) vốn không thuộc phần đề bài.
4. Chống lặp bằng mẫu đã chuẩn hóa số, so sánh gần giống và nhóm phương pháp đối với chủ đề Hệ bất phương trình.
5. Bài đã phát sai nhưng chưa nộp được cách ly: sao lưu `questions_json` cũ vào bảng `learning_assignment_quarantine`, rồi chỉ phát đề đúng nếu ngân hàng đủ nguồn.
6. Admin có thể xem sức chứa nguồn Word trước khi giao bài, và chọn “Sửa bài” để điều chỉnh độ khó/số câu đối với bài chưa có bài nộp. Câu đã nộp không bị sửa hoặc thay lại.

## Thực tế nguồn của ví dụ
- Trong tệp Word, chủ đề `he_bat_phuong_trinh`: 634 ứng viên gán metadata chủ đề.
- 23 câu ở mức Trung cấp vượt qua bộ lọc nội dung, loại câu và khớp nguyên văn DOCX (trước khi nhóm phương pháp).
- **6 nhóm phương pháp được chọn làm đại diện** khi áp dụng lọc lặp bảo thủ. Đây không phải chứng nhận độc lập toán học tuyệt đối.
- Mức Chuyên sâu có **0 câu đạt bộ lọc** từ nguồn Word hiện tại.
- Vì vậy không thể giao hợp lệ bộ 30 câu Chuyên sâu trong ví dụ. Hệ thống hiện trả HTTP 422 với số câu thực đủ điều kiện, không tự bịa thêm câu.

## Tài khoản và Render
- Không chèn cơ sở dữ liệu tài khoản runtime vào ZIP, không ghi đè kho tài khoản đang hoạt động.
- Phải sử dụng Render có persistent disk hoặc chuyển dữ liệu người dùng sang cơ sở dữ liệu bền vững. Cơ chế trong mã không tự cứu được tài khoản đã mất nếu không có backup.

## Kiểm thử phiên này
- 28/28 kiểm thử chọn lọc đạt, gồm kiểm thử AI TẬP HỌC, Word v62, tài khoản bảo vệ, gọi điện, quy trình giao bài.
- JavaScript của admin kiểm tra cú pháp đạt; mã Python vá đã biên dịch được.
- Mã không tự chứng minh độ đúng toán học của mọi câu Word; trò chơi khác và toàn bộ website chưa được kiểm thử end-to-end trên Render trong phiên này.

## Hướng dẫn xử lý bài lỗi đang giao
1. Đăng nhập Admin → Trung tâm sư phạm → Bài tập đã giao.
2. Chọn **Sửa bài** tại bài `AI TẬP HỌC` bị lỗi. Nếu đã có người nộp, cần tạo bài mới để giữ nguyên kết quả cũ.
3. Chọn chủ đề, mức độ, số câu đúng khả năng nguồn Word đang có. Với `he_bat_phuong_trinh`, mức Trung cấp hiện lọc được 6 nhóm phương pháp; mức Chuyên sâu chưa đủ câu.
4. Nếu muốn 30 dạng thật sự không trùng, cần bổ sung các câu Word có phương pháp độc lập và đáp án/lời giải đã kiểm chứng; không tính thay số thành dạng mới.
