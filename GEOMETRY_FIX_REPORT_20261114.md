# Geometry / Diagram Fix Report (2026-11-14)

## Đã chỉnh sửa

1. **Khung hình minh họa trong game**
   - Vá renderer `addDiagram(...)` cho toàn bộ các trang game có hình minh họa.
   - Hỗ trợ hiển thị tốt hơn cho:
     - câu hình học tọa độ 2D
     - câu Oxyz / không gian 3D
     - câu có 1 điểm duy nhất
     - câu có vectơ chỉ phương 3D
     - dữ liệu dạng `curves`, `marked_points`, `x_range`, `y_range`
   - Bổ sung trục `Ox, Oy, Oz` trong hình Oxyz.
   - Khắc phục lỗi khung hình trống khi đề có điểm 3D nhưng chỉ có 1 điểm hoặc có vectơ chỉ phương.

2. **Geometry Studio**
   - Mở rộng zoom rất lớn và thu nhỏ rất sâu (`MIN_ZOOM = 0.03`, `MAX_ZOOM = 40`).
   - Làm lưới chấm thưa hơn khi zoom nhỏ để không bị dày đặc trắng màn hình.
   - Thu nhỏ bán kính hiển thị điểm và cỡ chữ nhãn khi zoom nhỏ để giảm chồng chéo.
   - Thêm trục `Ox, Oy, Oz` khi dựng / xem mô hình 3D.

## File chính đã đụng đến

- `geometry-studio.html`
- Hàng loạt file trong `games/` có hàm `addDiagram(...)`

## Kiểm tra đã chạy

- Kiểm tra cú pháp JavaScript với `node --check` cho `geometry-studio.html`.
- Kiểm tra cú pháp JS cho toàn bộ 483 file `games/knowledge/*.html`.
- Kiểm tra mẫu ở các game ngoài `knowledge`.

## Lưu ý

- Tôi đã vá theo đúng phạm vi lỗi hình và zoom/trục mà bạn yêu cầu.
- Chưa thể xác nhận 100% mọi luồng runtime ngoài trình duyệt thật, nhưng cú pháp và bản vá logic đã được áp vào toàn bộ nhóm file liên quan.
