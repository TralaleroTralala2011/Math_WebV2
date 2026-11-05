# Thư viện video YouTube trong MATH_WEB

- Học bài và Lộ trình học giữ nguyên các chức năng trước đó; video được tìm khi học sinh chọn tab **Video**.
- Video có `youtube_id` đã xác minh trong `learn-assets/verified-lessons.json` được ưu tiên phát trực tiếp trong trang.
- Nếu chưa có video gắn sẵn, backend tìm tối đa 6 video có thể nhúng bằng **YouTube Data API v3** và trả về tiêu đề, kênh, hình thu nhỏ. Người dùng chọn video để phát trong trang. Không tải bản sao video về máy chủ.
- Để bật tìm video tự động, tạo API key trong Google Cloud, bật YouTube Data API v3, đặt biến môi trường `YOUTUBE_API_KEY` trên **máy chủ backend** trước khi chạy uvicorn. Không đưa key vào JavaScript hoặc GitHub.
  - PowerShell: `$env:YOUTUBE_API_KEY="YOUR_API_KEY"`
  - Sau đó chạy backend như bình thường.
- Không có API key hoặc backend không chạy: trang hiển thị thông báo và liên kết tìm kiếm trên YouTube; không tuyên bố có video khi chưa truy vấn được.
- Kết quả được cache trong bộ nhớ backend 1 giờ và cache trong phiên trang frontend. Có giới hạn 7 giây cho truy vấn YouTube. Các video bên ngoài có thể không còn cho phép nhúng hoặc bị gỡ sau khi tìm thấy.
- Cần đảm bảo việc sử dụng video tuân thủ điều khoản YouTube và quyền tác giả. Không scraping hay tải video về để phát lại.
- Bài test hiện có vẫn chỉ phủ một phần thư viện chủ đề. Không thay đổi thuật toán chấm điểm hay đồng bộ tài khoản trong bản này.
