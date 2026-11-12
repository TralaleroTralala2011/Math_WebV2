# MATH_WEB_GITHUB_READY | Bản đóng gói và tối ưu có kiểm chứng

Nguồn: MATH_WEB_LEARNING_PATH_YOUTUBE_VIDEO_LIBRARY_2026-11-05.zip. Tên thư mục gốc đã đổi thành MATH_WEB_GITHUB_READY để cập nhật GitHub cũ.

## Chỉnh sửa thực tế
- learning-path.js: tạo chỉ mục câu hỏi theo chủ đề khi tạo bài kiểm tra, bỏ câu trùng hoàn toàn, dùng Fisher–Yates để xáo trộn đồng đều.
- js/quick-navigation.js: giới hạn MutationObserver về khu vực overlay của trang luyện tập, tránh theo dõi mọi thay đổi trong toàn bộ cây DOM trên mọi trang.
- Không xóa các tệp gốc; những tệp khác giữ nguyên nội dung byte-for-byte.

## Kiểm tra
- Kiểm tra cú pháp JavaScript cho các tệp sửa bằng node --check.
- Kiểm tra tính toàn vẹn ZIP và đối chiếu SHA-256 của mọi tệp không chỉnh sửa.
- Chưa kiểm thử trình duyệt, backend tích hợp, hiệu năng tải cao hoặc tốc độ AI thực tế.

## Những hạng mục chưa hoàn tất
- Chưa có 2.000 dạng toán khác nhau cho mỗi chủ đề; chưa bao phủ toàn bộ chủ đề trong bài đánh giá đầu vào.
- Chưa chứng minh tốc độ tạo câu hỏi AI, tính ổn định Battle/Chat, vẽ hình và lưu tiến độ trên server.
- Tìm video YouTube cần YOUTUBE_API_KEY của riêng người triển khai.
- Không tuyên bố 100% hoàn thành khi chưa kiểm thử toàn hệ thống.

## Cập nhật GitHub cũ
Sao lưu thư mục Git cũ; chép nội dung của MATH_WEB_GITHUB_READY vào thư mục repo hiện tại (giữ .git, .env, DB riêng); kiểm tra git status và .gitignore; commit và push như bình thường.
