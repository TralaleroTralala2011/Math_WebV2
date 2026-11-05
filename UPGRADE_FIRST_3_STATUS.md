# Nâng cấp 3 tính năng đầu tiên: trạng thái kiểm chứng

1. **Thư viện**: giữ nguyên 150 chủ đề và dữ liệu bài học gốc, thêm đường dẫn từ `learn.html` sang `curriculum-studio.html`. Chưa biên soạn/kiểm định đủ 150 bài theo SGK; không tuyên bố hoàn thành.
2. **Bản đồ**: trang mới hiển thị chủ đề theo lớp và các cạnh tiên quyết từ API `/api/curriculum/graph`; đồ thị hiện chỉ được biên soạn một phần. Không suy diễn thiếu cạnh thành không có kiến thức tiên quyết.
3. **Gia sư**: API `POST /api/tutor/step` với `question`, `attempt`, `mode` (`hint`, `check`, `solution`). Kiểm chứng tương đương biểu thức và một số biến đổi phương trình một ẩn bằng SymPy. Không hỗ trợ bài toán lời văn, chứng minh tổng quát, hình học. Không sử dụng LLM.

## Kiểm tra
- `python -m compileall -q backend/app/tutor_routes.py backend/app/main.py`
- `node --check js/curriculum-studio.js`
- Chạy backend và frontend như README, truy cập `/curriculum-studio.html`.
- Chưa hoàn thành kiểm thử trình duyệt, bảo mật chuyên sâu, nội dung Toán 150 bài, và hồi quy toàn bộ hệ thống.

## Lưu ý
Các chức năng cũ giữ nguyên ngoại trừ thêm một liên kết điều hướng trong `learn.html` và đăng ký router mới trong `backend/app/main.py`. Bản này là bước triển khai thực tế đầu tiên, không phải bản nghiệm thu 100%.
