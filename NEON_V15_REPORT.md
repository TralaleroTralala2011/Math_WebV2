# MATH_WEB NEON V15 - Báo cáo nâng cấp và kiểm thử

**Nguồn:** `MATH_WEB_GITHUB_READY_NEON_V14_DIAGNOSTIC_INTEGRITY_2026-11-11.zip`.

## 1. Kết quả thực hiện

### Đề đầu vào lớp 10, 11, 12

- Giữ 150 chủ đề theo dữ liệu hiện hành: lớp 10 **49**, lớp 11 **51**, lớp 12 **50**.
- Sửa lỗi đọc sai cấu trúc học liệu: câu tự luận và Đúng/Sai lưu đáp án ở trường `answer`, nhưng bộ chọn đề cũ chỉ đọc `correct`. Khôi phục **388 câu ứng viên** từng bị loại sai về mặt cấu trúc.
- Trên bộ học liệu gốc, **1.391/1.391 câu có cấu trúc hợp lệ** sau khi sửa. Đây là kiểm tra cấu trúc, **không phải** chứng nhận đáp án và lời giải đều đúng toán học.
- Lấy **3-4 câu đã được Admin duyệt ở từng mức** khi có đủ dữ liệu. Không thêm câu chưa duyệt vào đề đã đạt đủ độ phủ.
- Bài đầu vào thiếu độ phủ chỉ là **đánh giá thử**. Trạng thái mới `placement_validated`/`placement_state` giúp frontend không nhầm với đánh giá đã đạt chuẩn.
- Không cho bài đầu vào chưa được kiểm chứng mở bài thi chủ đề chính thức 30 câu. Khi chưa đủ câu, API trả mã 409 và lý do `placement_not_validated`.
- Kết quả phân biệt `verified_score` với điểm tổng, đồng thời đánh dấu `roadmap_is_provisional`. Thứ tự ôn luyện chỉ dựa trên câu đã duyệt; chủ đề chưa có bằng chứng giữ thứ tự chương trình.

### Question Factory 2.0 và chấm đáp án

- Kiểm tra các phương án trắc nghiệm **tương đương toán học** ngay từ lúc nhận ứng viên, không chỉ lúc phát đề. Ví dụ `1/2` và `0,5` không được đồng thời xuất hiện trong một câu có một đáp án đúng.
- Kiểm tra lại các lựa chọn trước khi duyệt xuất bản.
- Sửa so sánh ký hiệu toán học **`R` khác `r`**, tránh loại nhầm phương án trong định lý sin.
- Sửa so sánh khoảng **`[3;5]` khác `(3;5)`**, trong khi `(3;5)` và `(3,5)` vẫn có thể biểu diễn cùng cặp tọa độ.
- Giữ quy trình duyệt độc lập; **không tự công nhận** dạng mới chỉ vì thay số.

### AI gia sư và lộ trình

- Chỉ câu đã duyệt cập nhật mô hình ước lượng năng lực theo chủ đề và mức độ; câu ứng viên vẫn được phép xem lại nhưng không được dùng làm bằng chứng đáng tin cậy.
- Giao diện lộ trình hiển thị rõ tổng số câu đã duyệt, câu ứng viên, chủ đề còn thiếu và trạng thái khóa; bổ sung CSS responsive cho trang lộ trình.
- Bài kiểm tra chủ đề vẫn yêu cầu **30 câu đã duyệt** và **25/30** để hoàn thành; ba chủ đề phải đạt mới mở nhóm kế tiếp.
- Đây là mô hình theo dõi năng lực cập nhật từ bài làm, **không phải mô hình ngôn ngữ tự huấn luyện**.

### Admin, giao diện, Battle và Chat

- Admin có bảng **12 chủ đề ưu tiên kiểm định**, tính từ số câu còn thiếu thực tế, không dùng số liệu minh họa của ảnh thiết kế.
- Giao diện NEON của các phiên trước và các nút Học tập, Lộ trình học, Vẽ hình được giữ lại; thêm cải thiện hiển thị kết quả trên điện thoại.
- Chạy thử Chat và Battle qua **hai kết nối WebSocket TCP độc lập** với máy chủ Uvicorn thật: xác thực, Chat REST lưu dữ liệu rồi phát qua WS, ping/pong, trạng thái Battle do máy chủ quyết định, tự kết nối lại. Cả hai bài thử đạt.
- **Chưa** kiểm thử trên hai thiết bị vật lý, hai mạng độc lập hoặc kiểm thử tải nhiều máy chủ.

## 2. Kiểm thử

- **184/184 kiểm thử backend đạt**, chạy theo ba nhóm: **61 + 57 + 66**.
- **25/25 kiểm thử tĩnh và hồi quy liên quan UI, ngân hàng, lộ trình đạt** sau khi cập nhật cache assets.
- **36/36 tệp JS** dưới `js/` và `games/` vượt qua `node --check`.
- Chat và Battle: **2 bài smoke test TCP độc lập đạt** (`python tools/test_live_realtime_tcp.py`).
- **Chưa có chứng nhận pixel-perfect** theo 5 ảnh: trình duyệt thử nghiệm trong môi trường này chặn điều hướng đến cả `localhost` và `file://` (`ERR_BLOCKED_BY_ADMINISTRATOR`). Không tuyên bố đã kiểm thử giao diện trực tiếp trên desktop/mobile thật.

## 3. Độ phủ ngân hàng hiện tại (cài đặt sạch, chưa có duyệt Admin)

| Lớp | Chủ đề | Câu học liệu ứng viên hợp lệ về cấu trúc | Câu đã duyệt độc lập | Thiếu tối thiểu 3 câu/mức | Thiếu cho 30 câu/chủ đề |
|---|---:|---:|---:|---:|---:|
| 10 | 49 | 523 | 0 | 441 | 1.470 |
| 11 | 51 | 458 | 0 | 459 | 1.530 |
| 12 | 50 | 410 | 0 | 450 | 1.500 |
| **Tổng** | **150** | **1.391** | **0** | **1.350** | **4.500** |

**Cảnh báo:** Số liệu 0 câu đã duyệt chỉ phản ánh **database sạch** trong môi trường kiểm thử. Nếu database người dùng đã có câu được duyệt, vào Admin hoặc chạy `python tools/export_placement_blueprint.py` để xuất số liệu thực tế. Không tự coi 1.391 ứng viên là đã được kiểm định toán học.

Ba bản thiết kế độ phủ `placement-audit/placement_grade_10_coverage.json`, `placement_grade_11_coverage.json`, `placement_grade_12_coverage.json` nằm trong ZIP. **Chúng là bản kiểm kê vị trí còn thiếu, không phải ba đề thi đã hoàn thành.**

## 4. Giới hạn chưa đạt 100%

1. **Chưa** kiểm chứng độc lập từng câu của 150 chủ đề, chưa đủ 1.350 câu chuẩn cho bài đầu vào và 4.500 câu chuẩn cho bài thi 30 câu/chủ đề.
2. **Chưa** chứng minh Question Factory có thể tự sinh 300.000 dạng toán thực sự khác bản chất, mỗi dạng 10 câu chuẩn.
3. **Chưa** kiểm thử giao diện giống hoàn toàn năm ảnh trên trình duyệt và thiết bị thật.
4. **Chưa** kiểm thử Battle/Chat trên hai thiết bị vật lý.
5. AI gia sư chưa có mô hình học máy tự huấn luyện từ dữ liệu bài làm; hiện sử dụng mô hình theo dõi năng lực cập nhật theo kết quả.
6. Hai thư mục `MATH_WEB/` và `mathweb_work/` là bản mã nguồn cũ được giữ nguyên để bảo toàn dữ liệu tham chiếu, **không phải** website NEON V15 đang chạy. Hãy mở `index.html` ở thư mục `MATH_WEB_GITHUB_READY` chính.

## 5. Nâng cấp an toàn

- **Không đóng gói** `mathweb.db`, `.mathweb_hmac_secret` hoặc tệp môi trường bí mật.
- Sao lưu database và khóa đăng nhập của bản hiện tại trước khi thay ZIP; giữ dữ liệu trong `%LOCALAPPDATA%\MATH_WEB` trên Windows.
- Khởi chạy từ thư mục gốc bằng `START_MATH_WEB.bat`. Hướng dẫn và các script kiểm thử nằm trong `tools/`.
