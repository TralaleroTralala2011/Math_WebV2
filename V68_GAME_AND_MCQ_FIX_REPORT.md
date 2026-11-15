# MATH_WEB V68 · Sửa lỗi game không lấy được câu hỏi và phương án quá dễ đoán

## Nền tảng và phạm vi
- Nền: `MATH_WEB_V67_GEOMETRY_AI_3D_UI_FIXED_20261115.zip`.
- Không sửa các file Word, SQLite ngân hàng câu hỏi, tài khoản, Battle, MathGeo Studio, HTML ngoài ba game Dãy số.
- Sửa 6 file gốc (3 Python + 3 HTML), bổ sung 2 file code/test và báo cáo này.

## Nguyên nhân lỗi HTTP 400 (`No valid topics`)
- Ba game lớp 10 gửi mã `SEQUENCE`, nhưng alias cũ trỏ sang `day_so` lớp 11.
- Ba game lớp 10 gửi mã `ALGEBRAIC_FRACTION`, nhưng không có alias dấu gạch dưới.
- Thêm hai topic chỉ dành cho game, ID `day_so_10` và `phan_thuc_dai_so`; **không thêm vào danh mục 150 chuyên đề**.
- Giữ `sequence` ở các trang game gốc lớp 11 ánh xạ sang `day_so` lớp 11.
- Thêm generator đúng nội dung: quy luật/điền số/tổng dãy; rút gọn phân thức/điều kiện xác định/phân thức đơn giản.
- Không dùng bài toán cộng trừ không liên quan làm đề thay thế.

## Cải thiện đáp án trắc nghiệm
- Thêm `mcq_quality_v68.py`: đối với câu có đáp án dạng `a/√b` và chỉ đáp án đúng mang căn thức, tạo ba phương án sai cùng kiểu ký hiệu, kiểm tra chúng khác giá trị đáp án.
- Ví dụ 7/√113: phương án thay thế cũng dùng mẫu `.../√113`, không còn số 1 nổi bật.
- Không chèn phương án “Giá trị khác” / “Không xác định” vào câu có đáp án là số nếu không đủ phương án có thể kiểm tra; thay vào đó validator từ chối để sinh lại.
- Lớp lọc chỉ có thể xử lý các mẫu đã xác định, không kiểm chứng tự động toàn bộ 91.026 câu nguồn.

## Chống trùng và chống cạn ngân hàng
- Cấp đề vẫn dùng `seen` và lịch sử người dùng gửi lên để tránh trùng nội dung trong một lượt bài.
- Game không bị chặn chỉ vì **người khác** đã từng nhận câu đó trong ledger toàn hệ thống; ledger vẫn ghi nhận dữ liệu, không xóa.
- Không lấy câu sai chủ đề hay lấy lại cùng một câu để bù số lượng.

## Kiểm thử trong môi trường độc lập
- Rà 528 HTML game có metadata: **528/528** mã chủ đề được nhận diện (game mặc định grade=10 khi metadata không có grade).
- API `/api/ai/practice/session`: 9 luồng, mỗi luồng 8 câu không trùng (SEQUENCE lớp 10, ALGEBRAIC_FRACTION lớp 10, sequence lớp 11; mỗi nhóm ba chế độ).
- Kiểm tra 1 câu trắc nghiệm mức trung bình cho mỗi chuyên đề chính: **150/150** có câu khả dụng.
- Kiểm thử hồi quy ngân hàng V59/V61/V62/V63: **34/34 đạt**.
- Kiểm tra lỗi phương án căn thức: 4 lựa chọn cùng dạng, chỉ một phương án bằng đáp án.
- Môi trường thử nghiệm sử dụng SQLite riêng. Tất cả file database/cache của V67 được khôi phục nguyên byte trước khi xuất.

## Giới hạn
- Chưa xác minh trên Render/GitHub Pages thực tế. Cần deploy cả backend V68 lên Render và frontend V68 lên GitHub Pages; cập nhật frontend đơn lẻ không chữa lỗi 400 từ backend cũ.
- Kiểm thử chủ đề 150/150 chỉ là smoke test một câu ở mức trung bình, không bảo đảm đủ câu ở mọi độ khó.
- Chưa thẩm định độc lập đáp án và độ khó của toàn bộ ngân hàng.
- Không thể cam kết mọi lỗi website đã được loại bỏ 100%; phạm vi V68 là lỗi API game và mẫu phương án dễ đoán đã xác nhận.
