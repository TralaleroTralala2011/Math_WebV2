# MATH_WEB: 45 chủ đề hình học tích hợp vào Game

## Đã cập nhật
- Thêm 45 chủ đề hình học vào `js/practise.js`, giữ nguyên cấu trúc thẻ kiến thức và popup hiện tại.
- Tạo 3 trang game cho từng chủ đề mới (Khám phá hình, Nhiệm vụ hình học, Trùm cuối hình học), tổng cộng 135 trang mới.
- Cập nhật `games/individual-games-manifest.json`: 147 chủ đề, 441 đường dẫn game, 3 game/chủ đề.
- Cập nhật bộ kiểm tra danh mục để kiểm tra mục tiêu 147/441.
- Mỗi trang game dùng ID chủ đề riêng, khối lớp đúng và gọi API tạo câu hỏi theo `topicId` đó khi Backend hoạt động.

## Kiểm tra đã chạy
- `python build_individual_games.py`: PASS, 147 chủ đề / 441 trang, mỗi chủ đề có đúng 3 game, không trùng tên hoặc đường dẫn, các đường dẫn đều tồn tại.
- `node --check js/practise.js`: PASS.
- `python -m compileall -q backend/app`: PASS.
- `python -m pytest -q`: 72 passed.
- Bộ sinh hình học được gọi thử trên cả 45 ID mới và trả về câu hỏi; 10 mẫu đại diện có metadata hình minh họa.

## Giới hạn cần nói rõ
- Kiểm thử tự động hiện xác nhận catalog, file, cú pháp và API-level tests, nhưng không thay thế kiểm thử thủ công toàn bộ 147 chủ đề trong trình duyệt.
- Bộ sinh hình học hiện có các bộ sinh theo nhóm dạng bài; việc kiểm tra mẫu phát hiện một số dạng sinh theo nhóm có thể chưa đủ đặc thù cho đúng tên của từng chủ đề. Cần tiếp tục kiểm tra tính khớp nội dung câu hỏi, lời giải và hình vẽ theo từng topic ID trước khi tuyên bố hoàn thành 100%.
- Hình minh họa là sơ đồ SVG theo metadata, không phải bộ dựng hình ràng buộc đầy đủ kiểu GeoGebra/CAD.
