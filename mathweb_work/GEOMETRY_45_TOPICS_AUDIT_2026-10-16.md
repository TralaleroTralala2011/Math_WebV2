# Báo cáo bổ sung 45 chủ đề hình học - 16/10/2026

## Thay đổi thực hiện
- Bổ sung 15 chủ đề hình học cho mỗi khối 10, 11, 12.
- Mỗi khối có 5 chủ đề Nền tảng, 5 Trung cấp, 5 Nâng cao.
- Mỗi chủ đề mới có ID, tên, kỹ năng con và ánh xạ sang bộ sinh câu hỏi hình học theo khối.
- Cập nhật danh mục chương trình và thêm kiểm thử tự động cho số lượng, phân bổ và ID.
- Bổ sung cơ chế hình minh họa theo nhóm chủ đề cho 45 chủ đề mới khi câu hỏi chưa có sơ đồ.
- Không chỉnh sửa HTML/CSS giao diện Practice, Game, Battle, kết bạn hoặc trò chuyện.

## Đếm dữ liệu trong ZIP nguồn và bản sau sửa
- Trong `backend/app/ai/knowledge/index.json` của ZIP nguồn: 30 chủ đề lớp 10, 32 lớp 11, 32 lớp 12, tổng 94 bản ghi chủ đề.
- Vì vậy, con số 102 được nêu trong yêu cầu không khớp với số bản ghi trong file index của ZIP này. Cần tiếp tục rà soát những nguồn danh mục khác trước khi xác nhận tổng chính thức.
- Sau khi thêm: lớp 10 = 45, lớp 11 = 47, lớp 12 = 47, tổng = 139 bản ghi chủ đề.
- Tổng ID duy nhất sau sửa: 139. Tên của 45 chủ đề mới không trùng chính xác với tên chủ đề đã có; đây chưa phải bằng chứng loại trừ mọi chồng lấn ngữ nghĩa với các chủ đề rộng cũ.

## Kiểm thử thực hiện
- Đã chạy 30 bài kiểm thử liên quan đến mở rộng chủ đề, sinh câu hỏi hình học, sơ đồ và độ phủ game: tất cả đạt.
- Đã gọi thử bộ sinh cho cả 45 ID mới: 45/45 trả về câu hỏi, đáp án, lời giải và sơ đồ hình học hợp lệ ở lượt kiểm tra.
- Đây là kiểm thử mẫu tự động, không thay thế việc rà soát thủ công toàn bộ đề, hình vẽ và trải nghiệm từng game.

## Giới hạn cần nói rõ
- 45 chủ đề đã được đưa vào danh mục API và ánh xạ đến bộ sinh câu hỏi hình học theo khối/cấp độ.
- Không tuyên bố đã tạo 45 bộ game HTML độc lập mới; game-specific UX và toàn bộ từng câu hỏi/hình vẽ vẫn cần kiểm thử tích hợp riêng.
- Số lượng game hiện có không được dùng thay cho số lượng chủ đề.
