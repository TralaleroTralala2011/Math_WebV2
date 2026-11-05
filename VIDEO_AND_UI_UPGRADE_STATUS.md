# MATH_WEB: Video và giao diện Học tập

- Nguồn: FEATURES_10_11_12, giữ nguyên các trang và chức năng cũ.
- Đã thêm giao diện Học tập cùng phong cách tím/trắng của Lộ trình học, giữ ID và JS hiện hữu.
- Đã bổ sung thư viện video tĩnh theo hai nhánh `learning` và `path` để chạy được trên GitHub Pages.
- Danh mục video kiểm duyệt ban đầu rỗng, KHÔNG giả lập 900 video.
- Có 150 chủ đề trong `learn-assets/topics.json`, tương ứng 900 vị trí video trong danh mục này. Cần đối chiếu thêm các danh mục khác trước khi kết luận toàn bộ chủ đề.
- Mỗi video phải có id YouTube, title, channel, status=verified; cấu trúc JSON: `{"10:mệnh đề và tập hợp":{"learning":[{"id":"XXXXXXXXXXX","title":"...","channel":"...","status":"verified"}],"path":[]}}`.
- Chưa có kiểm chứng trực tiếp tính đúng chủ đề, chất lượng, tình trạng nhúng của 900 video.
- Chưa chạy kiểm thử E2E trong trình duyệt.
