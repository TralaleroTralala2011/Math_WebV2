# MATH_WEB · Rà soát và sửa lỗi lần 3 (11/11/2026)

## Nguồn mã và cách bảo toàn tính năng

- Bản gốc dùng để tiếp tục: `MATH_WEB_GITHUB_READY_REAUDIT_FIXED_2026-11-11.zip` (bản sửa lần hai), có nguồn từ file `Math_WebV2-main(1).zip` do người dùng tải lên.
- Chỉ thay đổi **4 file mã nguồn** trong thư mục chạy chính `MATH_WEB_GITHUB_READY`: `backend/app/matchmaking/routes.py`, `backend/app/ai/routes.py`, `backend/app/questions/answer_checker.py`, `js/battle.js`.
- Thêm `backend/tests/test_audit_round3_regressions.py` và báo cáo này. **Không thay đổi** các thư mục `MATH_WEB/`, `mathweb_work/`, trang game, ngân hàng câu hỏi, tài liệu và CSS của bản trước. Chỉ chạy thư mục chính `MATH_WEB_GITHUB_READY` sau khi giải nén.
- ZIP mới được dựng từ từng tệp của ZIP trước, chỉ thay đúng những đường dẫn trên. Database và khóa bí mật sinh trong quá trình kiểm thử không được đưa vào ZIP.

## Các lỗi thực tế phát hiện và sửa trong đợt 3

1. **Hàng chờ Battle quá hạn không được dọn đúng:** cột thời gian ISO 8601 (`T...+00:00`) bị so sánh trực tiếp dưới dạng chuỗi với `datetime('now', ...)` (`... ...`), khiến các bản ghi quá 10 phút trong cùng ngày không bị xóa. Thay bằng so sánh `julianday(...)`, thêm kiểm thử hàng chờ 5/15 phút và không ghép với người hết hạn.
2. **Trận Battle hết 30 phút có thể kết thúc không có bảng điểm:** code cũ chỉ đổi trạng thái `FINISHED`, thiếu tổng kết đáp án và người thắng. Đã tính đúng/sai/bỏ qua, thời gian từng bên và người thắng trước khi kết thúc do quá hạn.
3. **Nút Bỏ qua vẫn có thể gửi sau khi trận hết giờ:** bổ sung kiểm tra hạn, từ chối 409 và kết thúc với kết quả được tổng kết. Tương tự cho trả lời; trang kết quả/tiến độ cũng chủ động tổng kết trận hết hạn khi được xem.
4. **Thời gian của người hoàn thành tiếp tục tăng khi đối thủ chưa xong:** tiến độ giờ dùng thời gian đã lưu cho người đã hoàn thành; người chưa hoàn thành vẫn xem thời gian thực.
5. **Giao diện Battle gửi sai dữ liệu tới backend:** frontend gửi `question_id` và `skipped` nhưng backend yêu cầu `question_index`; dẫn tới lỗi HTTP 422. Gửi đúng `question_index` và `answer`, tách `/answer` với `/skip`.
6. **Trắc nghiệm bị chấm sai do frontend gửi chỉ số 0–3:** đổi sang gửi chính văn bản lựa chọn mà bộ chấm server có thể ánh xạ chính xác, tránh lệch A–D.
7. **Câu Đúng/Sai 4 nhận định không được hiển thị và chấm đúng:** API trước đó không chuyển danh sách nhận định; frontend không có lựa chọn cho từng nhận định. Hiện API gửi `statements` (không gửi `statement_answers`), frontend có 4 cặp nút Đúng/Sai; bộ chấm dùng `statement_answers` thay vì đáp án số/chữ của bài toán gốc.
8. **Sai thời lượng Battle:** đồng hồ frontend đặt 60 phút, backend đặt 30 phút. Đồng bộ 30 phút; dọn hàng chờ 10 phút. Người đã nộp không bị ngừng chờ đối thủ quá sớm vì đếm số lần poll như giây thực.
9. **Tải lại trang Battle giữa trận gây bắt đầu lại từ câu 1:** trước khi hiển thị đề, frontend lấy tiến độ đã lưu từ API `/progress`, phục hồi chỉ số câu kế tiếp cùng số đúng/sai/bỏ qua.
10. **Màn hình kết quả hiển thị điểm 0 do lấy sai endpoint:** frontend trước chỉ lấy `/match/{id}` không có thống kê cuối; giờ lấy thêm `/match/{id}/result` và kết hợp danh sách hai người từ `/match/{id}`.
11. **Tài khoản cũ đôi khi bị nhận thành ID 0:** frontend Battle giờ đọc `mathweb_profile` và dự phòng từ `mathweb_user`, giúp nhận diện chính xác người thắng và người đối thủ khi cache profile chưa có.
12. **Tiến độ đối thủ không đồng bộ ngay qua WebSocket:** frontend gửi thông báo tiến độ sau khi backend xác nhận đáp án; khi nhận tín hiệu `sync` từ server, đối thủ yêu cầu lại trạng thái do server tính, không tin số điểm từ trình duyệt.
13. **API tạo phòng AI Battle cũ cho phép người lạ/ẩn danh lập phòng:** yêu cầu đăng nhập và xác minh cả hai Player ID/tài khoản là người thật, người gọi phải là thành viên; giữ route cho người dùng hợp lệ, không thay API matchmaking chính.

## Kiểm thử đã thực hiện

- `PYTHONPATH=backend python -m pytest -q backend/tests`: **136 đạt / 136**, 4 cảnh báo `FastAPI.on_event` đã cũ (không có kiểm thử thất bại).
- Thêm **7 bài kiểm thử** ở lượt này về hàng chờ hết hạn, trận 30 phút, thời gian kết thúc, Đúng/Sai không lộ đáp án, sự thống nhất backend/frontend, phân quyền API Battle cũ.
- Quét cú pháp toàn bộ bản chính: **549 file HTML, 1.067 khối JavaScript nhúng, 32 file JavaScript riêng**, tổng **1.099 đoạn JS**, 0 lỗi cú pháp phát hiện được.
- Kiểm thử giao diện thực thi với Chromium **trong trang DOM mô phỏng**, nối `fetch` tới các route của backend **FastAPI TestClient** và SQLite thử nghiệm. Một lượt **10/10 câu được xử lý qua các nút thật của UI**, gồm MCQ, tự luận, Đúng/Sai và 1 lượt Bỏ qua. API trả HTTP 200 cho các câu, kết quả bên chơi có **9 đúng, 1 bỏ** so với đối thủ bỏ cả 10; màn hình UI hiển thị đúng người thắng và đúng thống kê. Không phát sinh lỗi JS trong lượt thử này.
- Các bộ test cũ có kiểm tra tìm bạn theo Player ID, kết bạn, chat, đăng nhập/đăng xuất, Admin, game và Battle. Chúng đều đạt trong vòng kiểm thử này.
- Trên bản ZIP phát hành: kiểm tra tính toàn vẹn bằng `ZipFile.testzip()` và không đưa SQLite thử nghiệm hay khóa HMAC vào tệp phân phối.

## Giới hạn và điều chưa thể cam kết

- **Không thể chứng nhận website không còn bất kỳ lỗi nào.** Kết quả 136/136 chỉ đại diện cho những tình huống có test. Việc tìm ra lỗi hợp đồng API ở lượt này cũng cho thấy test đơn lẻ backend chưa bao phủ được mọi tình huống frontend.
- Chromium của môi trường thử nghiệm bị hạn chế điều hướng tới server chạy thật. Test giao diện dùng HTML/JS chính chủ với DOM Chromium và API FastAPI TestClient, **không phải** trình duyệt kết nối tới backend qua HTTP mạng thực.
- Chưa kiểm thử hàng nghìn người chơi cùng lúc, 4G/Wi-Fi yếu, multi-tab đồng thời quy mô lớn, Safari/iOS/Android vật lý, môi trường triển khai chính thức, camera/điều khiển cảm ứng hình học trên máy thật.
- 549 trang HTML đã qua quét cú pháp; riêng lượt này không kiểm thử tương tác từng trang game (lượt trước quét 529 game), cũng không thẩm định toán học toàn bộ ngân hàng hàng triệu câu hỏi.
- Cần thử thực tế với 2 tài khoản trong 2 thiết bị để xác nhận WebSocket mạng thật, kết quả và tỷ lệ tương thích thiết bị. Database sản xuất phải sao lưu trước khi đổi mã nguồn; ZIP không chứa bản sao dữ liệu người dùng.

## Khởi chạy bản sửa

1. Giải nén bản mới, chọn thư mục **`MATH_WEB_GITHUB_READY`** ở lớp ngoài cùng, không chạy các thư mục sao lưu cũ.
2. Windows chạy `START_MATH_WEB.bat`, mở `http://127.0.0.1:5500` và xem `http://127.0.0.1:8000/health`.
3. Đăng nhập 2 tài khoản thử, gửi lời mời Battle, chơi 10 câu và kiểm tra bảng kết quả. Sau đó thử tạo trận ngẫu nhiên, bỏ qua, tải lại trình duyệt giữa trận.
4. Nếu chuyển máy, sao lưu/copy database và cấu hình mật khẩu riêng từ máy cũ để tránh mất dữ liệu. Tránh thay database thực bằng database thử nghiệm.
