# MATH_WEB V113 - báo cáo minh bạch

**Nhiệm vụ:** tập trung ngân hàng 150 chủ đề / 2.000 phương pháp mỗi chủ đề / 10 câu mỗi phương pháp.

## Đã thực hiện trong bản này

- Kiểm toán lại toàn bộ 344.280 bản ghi nguồn JSONL, không làm thay đổi bank cũ.
- Phát hiện 11.464 nhóm chữ ký chính xác, chỉ 1.691 nhóm sau khi chuẩn hóa con số trong nhãn, 39.140 câu có nhãn tự nhận là biến thể. Các con số này **không** chứng minh loại dạng độc lập.
- Phân loại 11.464 ứng viên theo mức ưu tiên xem xét: 1.196 ưu tiên cao, 99 trung bình, 10.169 thấp (dựa trên chỉ báo cấu trúc, không khẳng định đúng toán).
- Xuất báo cáo 150 chủ đề, số lượng chưa được chứng nhận của từng chủ đề, và mẫu câu để chuyên gia xem xét.
- Viết 60 blueprint tường minh trong 55 chủ đề và tạo 600 câu có kết quả tự tính lại bằng SymPy; mỗi blueprint có 10 câu stem không trùng nhau; 0 câu trùng nguyên văn với 344.280 stem nguồn.
- Thiết lập 54 nhóm khái niệm thô sau khi gom các blueprint gần nhau; không cộng trùng vào tiến độ dạng độc lập.
- Chấm câu số, phân số, căn thức, π bằng biểu thức toán AST giới hạn an toàn; không thực thi mã từ câu trả lời của học sinh.
- Đưa blueprint mới vào bảng archetypes theo quy trình chờ duyệt, tách khỏi ngân hàng hoạt động. API cũ, Battle, tài khoản, giao diện, dữ liệu game được giữ nguyên.

## Kiểm thử

- V112 + V113 Question Factory: **25/25 đạt**.
- Bộ API và chất lượng ngân hàng gốc: **7/7 đạt**.
- Bộ backend khác, trừ hai nhóm trên: **114/114 đạt**.
- **146/146 test backend đã chạy đạt theo ba nhóm độc lập**. Các phép kiểm định 600 câu là một phần trong nhóm test v113, không cộng thêm 600 vào tổng số test.
- Chưa kiểm thử thực tế trên hai máy khác nhau, trình duyệt điện thoại, hosting, hay kiểm định ngữ nghĩa toàn bộ ngân hàng.

## Cần thực hiện tiếp

- Viết bộ đề xuất dạng **thực sự mới** dựa trên kiến thức/định lý/ứng dụng, không chỉ đổi số. Cần quy trình thẩm định ngữ nghĩa và người duyệt nội dung.
- Xây dựng bộ chứng minh độc lập cho từng họ đề, các định dạng đúng/sai, trắc nghiệm nhiễu hợp lý, hình học dựng và mô tả, tự luận nhiều bước.
- Đối chiếu ngữ nghĩa ứng viên 11.464 nhóm cũ với những phương pháp mới, xử lý 240.300 dòng thiếu trường proof và 10.303 lời giải ngắn.
- Kiểm tra đúng tên chủ đề/alias trong 150 mục danh mục; 86 chủ đề có tên khớp duy nhất chính xác với nguồn cũ, không đồng nghĩa 64 chủ đề còn lại rỗng.
- Tự động tạo ứng viên trong môi trường có nhà cung cấp mô hình, ngân sách, rate limit, giám sát, nhiều worker, PostgreSQL và máy chủ chạy dài hạn; chưa có API key, máy chủ hoặc ủy quyền để thực hiện phần đó trong phiên này.

**KẾT LUẬN:** 150 chủ đề tồn tại trong danh mục; 60 blueprint có 600 câu mẫu đã kiểm tra đáp án và chờ duyệt; mục tiêu **300.000 dạng độc lập và 3.000.000 câu chưa hoàn thành**.
