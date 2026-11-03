# MATH_WEB: AI hình học và công cụ dựng hình (bản sửa 2026-10)

## Lỗi được xử lý
- Bỏ hình tam giác cân mặc định bị hiển thị cho câu hỏi không có dữ liệu hình học.
- Tam giác vuông được dựng từ đúng hai cạnh góc vuông; dấu góc vuông được đặt tại đỉnh đúng.
- Tam giác nội tiếp có cạnh được nêu là đường kính được dựng bằng tọa độ thỏa Pythagore; góc vuông nằm tại đỉnh đối diện đường kính.
- Hình chữ nhật nội tiếp có các đỉnh nằm trên đường tròn, hai đường chéo đúng bằng đường kính; kích thước cạnh khớp số liệu đề.
- Thêm kiểm tra tính hợp lệ của điểm, đoạn, đường tròn, các đỉnh nội tiếp và góc vuông trước khi trả câu hỏi hình học.

## Công cụ dựng hình
Các primitive dùng chung gồm: tam giác vuông, tam giác từ ba cạnh, tam giác từ góc, tam giác có đáy/chiều cao, tam giác nội tiếp, tam giác cân, tam giác đồng dạng, hình chữ nhật, hình vuông, hình thoi, hình bình hành, hình thang, hình diều, đa giác đều, đường tròn, dây cung, tiếp tuyến, hình tròn nội tiếp đa giác, hình lập phương, hình chóp, lăng trụ tam giác, hình trụ, hình nón, mặt cầu, parabol và các hình tọa độ. Bộ dựng hình trả về tọa độ/đoạn/đường cong có cấu trúc để renderer vẽ, không chọn một hình tĩnh chung cho mọi đề.

## AI hình học
- Gắn hình được dựng từ cùng bộ dữ kiện với lời đề, gồm hình học phẳng, tọa độ, biến hình, hình học không gian, mặt cầu và thể tích.
- Với câu chưa có dữ liệu dựng hình chính xác, renderer không tự vẽ hình giả định gây hiểu nhầm.
- Engine vẫn là bộ sinh theo mẫu/kiến thức có kiểm tra, chưa được kết nối với dịch vụ LLM bên ngoài trong bản này.

## Kiểm thử
- `python -m pytest -q`: 40 tests passed.
- Stress test: 2,700 câu sinh ra từ 9 nhóm kiến thức × 3 mức độ; kiểm tra hình đi kèm và tính hợp lệ của dữ liệu hình.
- JavaScript: `js/practise.js` và 642 script nội tuyến trong các trang game đã qua `node --check`.
- Các kiểm thử là kiểm thử mã nguồn và dữ liệu sinh; vẫn cần mở trang trong trình duyệt để nghiệm thu trực quan ở môi trường chạy thực tế.

## Bổ sung kiểm tra và sửa bản 2026-10-14
- Sửa hình phụ trong tam giác: đường trung tuyến AM thực sự nối tới trung điểm M; đường phân giác AD đặt D theo định lý phân giác; đường cao AH dựng vuông góc với BC và được đánh dấu nét đứt.
- Với câu hỏi nêu đường kính AB, sơ đồ đường tròn hiển thị AB, tâm O, độ dài đường kính và bán kính bằng một nửa đường kính khi dữ kiện cho phép.
- Renderer AI trong `js/practise.js` đã hiển thị `dashed_segments`; dấu góc vuông tự chọn cặp cạnh vuông góc thực tế tại đỉnh thay vì mặc định lấy hai đoạn đầu tiên.
- Thêm kiểm thử hồi quy cho đường cao, trung tuyến, phân giác và đường kính.
- Kết quả xác minh bản vá: `python -m pytest -q` = 43 passed; `node --check js/practise.js` thành công.
