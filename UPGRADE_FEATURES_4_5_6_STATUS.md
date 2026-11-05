# MATH_WEB: nâng cấp tính năng 4–6 (bản triển khai giới hạn)

## 4. Hình học tương tác
- Trang `geometry-lab.html` có đường tròn và tam giác OBC, kéo điểm B/C, đổi bán kính và góc.
- Ràng buộc OB=OC=r luôn được duy trì bằng tọa độ lượng giác. Độ dài BC tính theo công thức dây cung.
- Chưa hỗ trợ tất cả hình phẳng, Oxyz và 3D. Trang geometry-studio.html cũ được giữ nguyên.

## 5. Đánh giá thành thạo
- Backend `/api/learning-progress/overview`, `/diagnostic/{topic_id}`, `/answer` yêu cầu token học sinh.
- Chỉ chấm câu hỏi số được định nghĩa và kiểm chứng phía server; mỗi câu chỉ ghi lần đầu. Không cộng XP.
- Chỉ có 7 chủ đề với 2 câu chẩn đoán mỗi chủ đề; điểm số chỉ là tín hiệu sơ bộ, không thể kết luận thành thạo toàn diện.

## 6. Lộ trình thích ứng
- `/api/learning-progress/path` đối chiếu bằng chứng chẩn đoán với danh sách kiến thức tiên quyết đã tuyển chọn từ bản trước.
- Chưa có bài kiểm tra đầu vào toàn diện, thuật toán tâm trắc hay lộ trình cá nhân đầy đủ 150 chủ đề.

## Hướng dẫn
- Chạy backend theo README cũ và frontend `python -m http.server 5500`.
- Mở `geometry-lab.html` để xem mô hình hình học; `learning-progress.html` sau khi đăng nhập tài khoản học sinh.
- Cần kiểm thử E2E nhiều trình duyệt, đa thiết bị trước khi triển khai thực tế.
- Các trang luyện tập, game, battle hiện hữu không bị chỉnh sửa trực tiếp.
