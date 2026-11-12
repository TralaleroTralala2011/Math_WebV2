# MATH_WEB · Báo cáo quét lỗi, nâng cấp và tối ưu lần 4

**Ngày:** 11/11/2026  
**Nguồn duy nhất:** `MATH_WEB_GITHUB_READY_AUDIT_FIXED_ROUND3_2026-11-11.zip`  
**Thư mục chạy chính:** `MATH_WEB_GITHUB_READY/`.

## 1. Nguyên tắc giữ nguyên hệ thống

- Không sửa nội dung các trang HTML, các CSS giao diện, nội dung ngân hàng bài tập, database người dùng hoặc những bản lưu `MATH_WEB/`, `mathweb_work/`.
- Chỉ chỉnh logic trong **11 file nguồn có sẵn**, thêm 2 file khởi chạy/máy chủ frontend mới, 2 file kiểm thử mới và báo cáo này.
- Những API cũ vẫn được duy trì. Các endpoint tổng hợp là API *bổ sung*, không thay API cũ; frontend có đường dự phòng khi backend chưa cập nhật.
- Không gộp dữ liệu thực vào bản ZIP, không đóng gói database hoặc khóa ký token tạo ra khi thử nghiệm. **Sao lưu database thực trước khi nâng cấp.**

## 2. Các lỗi và vấn đề đã sửa

1. **Chat dài bị mất tin gần nhất khi mở lại.** API trước đây trả 200 tin đầu tiên theo ID tăng dần. Giờ chọn 200 tin mới nhất, rồi trả theo thứ tự thời gian; `after_id` vẫn lấy tin mới, `offset` cho phép truy cập đoạn lịch sử cũ.
2. **Quá nhiều yêu cầu mạng để hiển thị chat.** Trước đây mỗi bạn bè cần một request riêng để lấy số tin chưa đọc và một request riêng để lấy trạng thái online. Thêm `/api/chat/unread-by-friend` và `/api/presence/friends`: mỗi phần chỉ cần một request, lọc theo tài khoản đã đăng nhập và danh sách bạn đã chấp nhận. Giữ các API cũ cho ứng dụng cũ.
3. **Tạo bảng SQLite và chèn seed lặp lại ở module học tập.** Hai module `study-suite` và `final-features` khởi tạo schema trong mọi request; chuyển sang khởi tạo một lần mỗi file DB, thêm chỉ mục cho lịch ôn và dữ liệu giáo viên. Có khóa đồng bộ cho nhiều request cùng lúc, phát hiện DB mới tại đường dẫn cũ và vẫn tự tạo schema.
4. **Bài thi có thể nộp đồng thời hai lần.** Dùng `BEGIN IMMEDIATE` trước khi đọc trạng thái bài thi để hai lượt nộp cạnh tranh không cùng được chấp nhận. Kiểm thử: một yêu cầu 200, yêu cầu còn lại 409.
5. **Câu hỏi hỗn hợp đôi lúc thiếu dạng Đúng/Sai.** Lỗi do trộn khối 10 câu rồi cắt còn 9. Giờ phân bổ đủ chỉ tiêu *trước* khi xáo trộn. Bộ 9 câu: 6 trắc nghiệm, 2 tự luận, 1 Đúng/Sai; bộ 10 câu: 7/2/1. Với bộ từ 3 câu trở lên, bảo đảm có đủ 3 định dạng.
6. **Bộ tìm đề đã biên soạn bỏ sót câu cũ đúng chủ đề.** Trước đây đọc 500 câu mới nhất của *toàn khối*, rồi mới lọc chủ đề/độ khó. Giờ lọc bằng SQL theo chủ đề, định dạng và cấp độ trước, có truy vấn dự phòng cho dữ liệu nhập cũ. Kiểm thử với hơn 1.100 câu mới hơn vẫn tìm thấy câu phù hợp cũ.
7. **Battle có thể sinh câu quá lâu khi lịch sử chống trùng dày.** Cho đường tạo câu Battle chuyển sang bộ sinh dự phòng đã có sẵn sau 12 lần thử mỗi giai đoạn, thay vì 150 lần thử mỗi giai đoạn. Các câu dự phòng vẫn qua bước kiểm tra hợp lệ và không trùng nguyên văn trong một trận. Đường luyện tập không đổi giới hạn kiểm chứng.
8. **Điện thoại dùng Wi-Fi bị điều hướng nhầm tới API đã lưu từ môi trường public.** Khi truy cập từ mạng nội bộ, bỏ qua cấu hình API public đã lưu trước đó, ưu tiên backend nội bộ. Vẫn hỗ trợ `?api=...` tường minh trên cài đặt local.
9. **Tải file tĩnh chưa được nén khi chạy local.** Thêm `scripts/serve_frontend.py`, gzip cho HTML/CSS/JS/JSON phù hợp, ETag và 304, kiểm tra file thay đổi, không đổi URL và hiển thị. Đã nối với `START_MATH_WEB.bat` và `CHAY_WEBSITE.bat`. Thư viện chuẩn Python, không cần cài thêm gói.
10. **API dùng cơ chế startup/shutdown FastAPI đã cũ.** Chuyển sang lifespan mới, giữ công việc maintenance khởi động và dừng như trước.
11. **Thiếu cách bật backend LAN cho điện thoại.** Thêm `START_MATH_WEB_LAN.bat` làm chế độ *tùy chọn*, chỉ dùng khi đã tin tưởng mạng Wi-Fi; cách khởi chạy cục bộ mặc định vẫn bind `127.0.0.1`.

## 3. Kiểm thử và số liệu

- **Backend:** 144/144 bài kiểm thử đạt trong lần chạy cuối (bao gồm toàn bộ các bộ thử cũ), không còn cảnh báo FastAPI `on_event`.
- **Quét tĩnh:** 549 trang HTML, 1.067 script nhúng, 32 file JavaScript riêng. **1.099 đoạn JavaScript** đều qua bước kiểm tra cú pháp; **2.868 liên kết nội bộ** đã rà soát, không phát hiện file thiếu.
- **API chức năng có test:** đăng ký/đăng nhập, tìm bạn theo Player ID, kết bạn, chat, trạng thái online, phân quyền, quản trị, bài học/bài giao, ngân hàng đề và Battle.
- **HTTP thực của frontend:** test khởi tạo máy chủ nội bộ, thử gzip, không gzip, ETag/304 và HEAD đạt. 12 trang/script/style mẫu có tổng dung lượng chưa nén **761.305 bytes**, gzip còn **124.585 bytes**, giảm **83,6% dữ liệu truyền** trong ví dụ này khi trình duyệt chấp nhận gzip. Đây không phải số đo thời gian tải trang thực tế và chỉ áp dụng cho máy chủ local mới.
- **Database:** microbenchmark 200 lần mở kết nối/đọc một câu: module study-suite trước khoảng **98 ms**, sau khoảng **45 ms**; module teacher/final-features trước **59 ms**, sau **23 ms** trong môi trường thử. Số đo tham khảo, không cam kết tốc độ cho máy khác hoặc dữ liệu lớn.
- Kiểm thử 250 tin nhắn trong một hội thoại, lấy 200 tin mới nhất, phân trang ngược và đếm chưa đọc đúng. Kiểm tra API mới từ tài khoản chưa đăng nhập, từ người lạ, và khi cùng có nhiều bạn.
- Mã nguồn đã được biên dịch Python và JavaScript không có lỗi cú pháp.

## 4. Giới hạn chưa xác nhận (quan trọng)

Không thể chứng nhận website đã **hết 100% lỗi** chỉ từ các bộ thử này. Trình duyệt Chromium trong môi trường kiểm thử từ chối điều hướng HTTP tới máy chủ local bằng `ERR_BLOCKED_BY_ADMINISTRATOR`; vì vậy phần tương tác desktop/mobile qua *trình duyệt nối server thật* chưa kiểm chứng được. Các bài thử HTTP vẫn chạy được qua Python; nhiều luồng API chạy qua FastAPI TestClient. Cần thử trên Chrome/Edge/Android/iOS thực tế với hai tài khoản và mạng Wi-Fi/4G để kiểm chứng hoạt động UI, WebSocket hai thiết bị và responsive.

Chưa kiểm định độc lập hàng triệu đáp án/toán học và mức độ khác bản chất của tất cả dạng bài; chưa thực hiện kiểm thử tải hàng nghìn tài khoản, thông lượng database hay kiểm thử bảo mật chuyên sâu ở production. Bản phát hành đã sửa các lỗi **được xác nhận** và vượt qua bộ kiểm thử hiện tại, không phải cam kết không có lỗi chưa được phát hiện.

## 5. Cách khởi động

- **Máy tính Windows:** giải nén, mở đúng thư mục `MATH_WEB_GITHUB_READY`, chạy `START_MATH_WEB.bat`, sau đó mở `http://127.0.0.1:5500/`.
- **Điện thoại cùng Wi-Fi:** đóng các cửa sổ server cũ, trên PC chạy `START_MATH_WEB_LAN.bat` và chỉ cho phép tường lửa Python trên mạng tin cậy. Dùng `ipconfig` trên PC xem IPv4, điện thoại truy cập `http://<IPv4-của-PC>:5500/`. Đảm bảo PC và điện thoại cùng mạng; Wi-Fi khách có thể chặn các thiết bị nhìn thấy nhau. Không sử dụng LAN mode trên mạng công cộng.
- **Máy khác / deployment:** backend phải cấu hình chính xác địa chỉ CORS/API, HTTPS, secret và lưu DB bền vững; chạy localhost script không tự động triển khai online.

## 6. Đề xuất nâng cấp tiếp theo (chưa triển khai)

**Ưu tiên 1:** chuyển chat, presence và notification từ polling sang WebSocket hoặc SSE có fallback. Sẽ giảm lượng request và cập nhật gần thời gian thực, nhất là khi có nhiều bạn bè.

**Ưu tiên 2:** chạy bộ kiểm thử trình duyệt end-to-end trên Windows, Android và iPhone thật, tự động chụp các kích thước màn hình 320–1440px, kiểm tra Battle hai thiết bị, kết bạn/nhắn tin, chuyển mạng và khôi phục phiên.

**Ưu tiên 3:** audit ngân hàng đề theo từng dạng toán độc lập; kiểm thử lời giải, một đáp án đúng, hình học có tính nhất quán với dữ kiện và chống trùng *bản chất*, không chỉ trùng chuỗi. Không công nhận các dạng được sinh tự động khi chưa thẩm định.

**Ưu tiên 4:** khi số người dùng tăng, đo thời gian từng API và `EXPLAIN QUERY PLAN`, thêm giám sát lỗi/tracing và cân nhắc PostgreSQL thay SQLite ở các dịch vụ ghi đồng thời cao.

**Ưu tiên 5:** kiểm tra chất lượng các video/nguồn học và thiết kế PWA cache cho bài học đọc ngoại tuyến, có giao diện thông báo trạng thái mạng và đồng bộ sau khi kết nối lại.

## 7. Danh sách file nguồn đã sửa

`CHAY_WEBSITE.bat`, `START_MATH_WEB.bat`, `backend/app/ai/engine/service.py`, `backend/app/chat/routes.py`, `backend/app/final_features_routes.py`, `backend/app/main.py`, `backend/app/matchmaking/routes.py`, `backend/app/presence/routes.py`, `backend/app/study_suite_routes.py`, `js/api-config.js`, `js/chat.js`.

**File mới:** `START_MATH_WEB_LAN.bat`, `scripts/serve_frontend.py`, `backend/tests/test_audit_round4_chat_performance.py`, `backend/tests/test_audit_round4_static_server.py`, `AUDIT_FIX_REPORT_ROUND4_2026-11-11.md`.
