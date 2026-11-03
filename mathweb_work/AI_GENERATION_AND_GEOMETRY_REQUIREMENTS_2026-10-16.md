# BỔ SUNG BẮT BUỘC: AI TẠO ĐỀ TOÁN VÀ AI DỰNG HÌNH THÔNG MINH

Tài liệu yêu cầu đầy đủ do người dùng cung cấp ngày 16/10/2026. Đây là tiêu chí sản phẩm, không phải tuyên bố rằng mọi tiêu chí đã được hoàn thiện.

## B1. AI tạo đề toán phong phú như ChatGPT

### Mục tiêu
Phát triển AI hiểu yêu cầu và sinh bài mới đa dạng; không chỉ thay số trong một số ít mẫu cố định.

### Đa dạng nội dung
- Nhiều dạng bài trong cùng chủ đề; thay đổi cách đặt vấn đề, dữ kiện, yêu cầu và phương pháp giải.
- Kết hợp tính toán, chứng minh, phân tích, suy luận, điều kiện, khảo sát, tham số và cực trị khi phù hợp.
- Có câu hỏi nền tảng đến phức tạp, bài toán thực tế tự nhiên, dữ kiện hợp lý, mục tiêu rõ ràng.
- Kết hợp kiến thức khi đúng chương trình; tùy chỉnh chủ đề, độ khó, số bước, loại đáp án và dạng bài.
- Sinh mới theo yêu cầu, hạn chế câu hỏi đã gặp.

### Đa dạng lời giải
- Trình bày từng bước và lý do chọn công thức/định lý/phương pháp.
- Thể hiện phép tính, lập luận, điều kiện xác định, điều kiện nghiệm và trường hợp đặc biệt.
- Khi phù hợp, đưa cách giải khác; bài chứng minh phải logic; bài thực tế nêu ý nghĩa và đơn vị.

### Kiểm chứng
- Đề đủ dữ kiện, không mâu thuẫn; đáp án khớp lời giải.
- Trắc nghiệm có đáp án đúng và phương án nhiễu hợp lý; đúng/sai có kết luận xác định; tự luận có tiêu chí chấm/xác minh.
- Kiểm tra độc lập bằng công cụ toán học khi có thể. Không tự gắn nhãn đã kiểm chứng nếu còn nghi ngờ.

### Cấp độ
- **Nền tảng:** khái niệm, công thức, kỹ năng cơ bản, ứng dụng trực tiếp.
- **Trung cấp:** vận dụng, nhiều bước, xử lý dữ kiện.
- **Nâng cao:** lập luận sâu, tổng hợp, tham số, cực trị, chứng minh phức tạp.
- **Địa ngục/Olympic:** thử thách tư duy, ý tưởng sáng tạo, lập luận chặt chẽ.

Không tăng độ khó giả tạo bằng cách chỉ tăng số lớn hoặc kéo dài phép tính.

### Cá nhân hóa và chống lặp
- Lưu lịch sử theo tài khoản/phiên phù hợp, hạn chế lặp.
- Có thể tăng độ khó theo kết quả khi được bật.
- Sinh nhiều đề khác nhau trong cùng chủ đề/cấp độ, không đánh đổi độ chính xác để lấy số lượng.
- Tích hợp trực tiếp vào website.

## C1. AI dựng hình toán học thông minh

### Loại hình hỗ trợ
- **2D:** tam giác và đường đặc biệt; tứ giác/đa giác; đường tròn, dây, tiếp tuyến, cát tuyến, góc; song song/vuông góc/giao nhau/đồng quy; biến hình, vectơ, quỹ tích; tọa độ; elip, parabol, hypebol.
- **3D:** chóp, lăng trụ, hộp, lập phương, thiết diện; đường-thẳng-mặt phẳng; góc, khoảng cách, hình chiếu; mặt cầu; Oxyz và cấu hình không gian phù hợp.
- **Tọa độ/đồ thị:** Oxy/Oxyz; điểm theo tọa độ; đường thẳng, đường tròn, đường cong, mặt cong; giao điểm, vectơ, hình chiếu.

### Phân tích trước khi vẽ
Trích xuất đối tượng, tên/ký hiệu, độ dài/góc/tọa độ, quan hệ song song-vuông góc-tiếp xúc-giao nhau-thuộc nhau, điều cần tìm/chứng minh và mọi ràng buộc. Không chọn hình mẫu chung chỉ vì đề có từ khóa hình học.

### Chính xác và tỉ lệ
- Tọa độ phải đặt theo tọa độ; góc vuông đúng đỉnh; song song/vuông góc/tiếp xúc phải thỏa mãn về toán học.
- Kích thước, nhãn, đỉnh, cạnh, mặt và cạnh khuất phải nhất quán với đề.
- Không bóp méo hình để đẹp; chỉ được dịch nhãn để dễ đọc.
- Nếu thiếu dữ kiện xác định duy nhất, không tự thêm điều kiện; ghi rõ đây là hình minh họa/sơ đồ. Không suy luận định lý chỉ từ hình vẽ.

### Kiến trúc đề xuất
AI đọc đề → cấu trúc hóa dữ kiện → bộ tính toán dựng cấu hình → renderer 2D/3D → bộ kiểm chứng → hiển thị. Nếu điều kiện mâu thuẫn/chưa đủ, báo trạng thái phù hợp thay vì giả vờ hình chính xác. Ưu tiên thư viện toán học/dựng hình chính xác hơn ảnh AI thuần túy.

### Tương tác và tích hợp
Khi phù hợp: zoom/pan, xoay 3D, bật/tắt nhãn/đối tượng phụ, tô sáng đối tượng trong lời giải, dựng từng bước, đổi tham số và cập nhật hình. Tích hợp vào AI tạo câu hỏi, Practice, Game, Battle và lời giải mà không phá giao diện hiện có.

### Kiểm thử hình học
Kiểm tra kích thước/góc 2D, tam giác vuông, đường tròn/tiếp tuyến, tọa độ, chóp có quan hệ song song/vuông góc, thiết diện 3D, tham số, thiếu/mâu thuẫn dữ kiện, nhãn gần nhau và hình phức tạp. Xác minh quan hệ bằng tính toán khi có thể.

## C2. Tiêu chuẩn hoàn thành

### AI tạo đề
- Dạng bài thực sự đa dạng; chọn lớp/chủ đề/cấp độ/loại câu hỏi.
- Có đáp án, lời giải và kiểm tra nhất quán.
- Giảm lặp; hoạt động trực tiếp trong hệ thống hiện có.

### AI dựng hình
- Phân tích đúng dữ kiện; hỗ trợ 2D, tọa độ và 3D.
- Thể hiện đúng dữ kiện, không bịa thêm hoặc dùng hình không liên quan.
- Kiểm tra trước khi hiển thị; tích hợp Practice/Game/Battle mà không phá UI đã khóa.

**Nguyên tắc:** chất lượng, độ đa dạng và tính đúng toán học quan trọng hơn số lượng câu hỏi/hình minh họa.
