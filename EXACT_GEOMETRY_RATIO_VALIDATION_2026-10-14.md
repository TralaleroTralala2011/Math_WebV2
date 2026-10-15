# Nâng cấp dựng hình theo tỉ lệ và kiểm định ràng buộc

- Hình chữ nhật lưu chiều dài, chiều rộng và tỉ lệ cạnh ngay trong dữ liệu hình. Ví dụ 5 cm × 4 cm dùng tọa độ có tỉ lệ 5:4, không dùng hình chữ nhật mặc định rồi gắn nhãn 5 và 4.
- Bộ kiểm định hình học kiểm tra ràng buộc hình chữ nhật (góc vuông, hai cặp cạnh đối bằng nhau) và tỉ số độ dài trước khi dữ liệu được coi là hợp lệ.
- Bộ kiểm định đường tròn xác thực các đỉnh được khai báo là đỉnh nội tiếp phải nằm đúng trên đường tròn theo tọa độ và bán kính.
- Bộ dựng SVG hiện dùng cùng một hệ số tỉ lệ cho cả trục x và y để tránh kéo giãn hình làm sai góc và tỉ lệ cạnh.
- Kiểm thử sau thay đổi: 58 bài kiểm thử Python đạt; `node --check js/practise.js` đạt.

Lưu ý: kiểm định chỉ bảo đảm các ràng buộc được biểu diễn và kiểm tra trong dữ liệu hình. Không nên tuyên bố chính xác tuyệt đối cho mọi loại đề tự do trước khi bổ sung parser/ràng buộc chuyên biệt và kiểm thử trình duyệt cho từng nhóm hình.
