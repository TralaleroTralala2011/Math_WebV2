# Báo cáo phát triển MATH_WEB V112

**Nguồn**: `MATH_WEB_GITHUB_READY_RESEARCH_V111_10000_VERIFIED_CORE_QUESTIONS(1).zip` do người dùng gửi.
**Nguyên tắc**: không xoá tính năng, giữ giao diện Luyện tập/Battle/Học tập/hình học hiện có, thay đổi nhỏ có kiểm thử, lưu toàn bộ tệp gốc trong gói đầu ra.

## Đã triển khai

1. `backend/question_factory/`: tích hợp lõi worker của bản pilot vào backend V111 dưới dạng thư viện riêng.
2. `backend/question_factory/catalog_150.json`: nhập danh mục **150 chủ đề gốc** (49 lớp 10, 51 lớp 11, 50 lớp 12); không đánh tráo số chủ đề thành số dạng toán độc lập.
3. API: `GET /api/factory/health|progress|catalog|next`, `POST /api/factory/answer`, API admin duyệt, enqueue, pause/resume, giới hạn số câu, giới hạn ngân sách; trần phiên làm bài để giảm nguy cơ quá tải. Tích hợp vào `app.main`, không đổi API cũ.
4. DB SQLite WAL riêng: job claim có lease, heartbeat, retry giới hạn, kiểm soát trùng fingerprint, transaction, lưu lại sau restart, phân phối song song 1..16 worker (một máy).
5. 9 dạng minh họa có generator và đối chiếu SymPy, **chỉ sau khi chuyên gia duyệt dạng**; 10 biến thể/cùng phương pháp, không coi là 90 dạng độc lập.
6. Session chấm câu hỏi: không trả đáp án trước khi nộp, phiên một lần, hết hạn; so sánh phân số chính xác hoặc text. Không tuyên bố tương đương toán học đầy đủ mọi dạng tự luận.
7. `factory-dashboard.html`: bảng giám sát 150 chủ đề, số dạng/câu thực tế và điều khiển worker có token, responsive và không thay UI các trang cũ.
8. `Dockerfile.mathweb`, `docker-compose.mathweb.yml`, `.github/workflows/mathweb-ci.yml`, `CHAY_QUESTION_FACTORY.bat`, hướng dẫn vận hành không cần GitHub.
9. `QUESTION_FACTORY_V112_SOURCE_AUDIT.json`: kiểm toán streaming ngân hàng V111 không sửa dữ liệu cũ.

## Kiểm thử

- Mã cuối cùng đã chạy theo **ba nhóm test độc lập** để tránh giới hạn thời gian: **18 + 7 + 114 = 139 passed, 0 failed**. Test toàn bộ trong một tiến trình trước đó đạt **137 passed**; lần chạy đơn tiếp theo bị giới hạn thời gian, nên không báo sai là đã có một phiên đơn chạy xong 139 test. Chi tiết xem `V112_TEST_REPORT.json`. Các bài test Question Factory gồm worker song song, idempotent, crash recovery, terminal lease, tạm dừng, ngân sách, API ẩn đáp án, token, session một lần, giới hạn phiên, seed ổn định theo dạng, catalog 150 và sự tồn tại của route cũ.
- Nhóm API Battle/bạn bè/chat/learning/hình học: **29 passed** trong lần chạy riêng, là tập con của 137.
- Node kiểm tra cú pháp JS Battle/Luyện tập và 2 test hình học (`tools/v96_mathgeo_runtime_test.cjs`, `tools/v97_triangle_sss_test.cjs`): **đạt**.
- **Chưa** chạy trình duyệt thật qua nhiều kích thước màn hình, chưa đo tải máy chủ, chưa chạy Docker thực tế, chưa chạy CI trên GitHub, chưa kiểm thử đầy đủ ghép trận qua hai máy thực. Không tuyên bố đạt 100%.

## Kết quả kiểm kê V111 (chỉ là kiểm toán cấu trúc)

| Kiểm tra | Kết quả |
|---|---:|
| Số dòng JSONL ngân hàng gốc | 344.280 |
| Dòng JSONL lỗi hoặc thiếu trường bắt buộc | 0 |
| Câu trùng nguyên văn cùng lớp/chủ đề | 0 |
| Số nhóm theo (lớp, chủ đề, `form_signature`) | 11.464 |
| Số nhóm theo (lớp, chủ đề, `form_id` hoặc `method_family`) | 34.428 |
| Lời giải dưới 25 ký tự | 10.303 |
| Dòng không có trường `proof` | 240.300 |
| Các trường hợp `linear_isolate` có proof được kiểm tra chính xác | 10 hợp lệ |
| Lớp/chủ đề có tên được ghi trong ngân hàng | 140 cặp |
| Chủ đề trùng chính xác tên và khối lớp với catalog 150 | 89 (không bao gồm alias) |
| Số dạng độc lập được chứng nhận từ kiểm toán này | **Chưa xác định** |

**Diễn giải**: 34.428 ID không tương đương với 34.428 phương pháp độc lập; 344.280 dòng chưa chứng minh có đáp án/lời giải toán học đúng trong mọi câu. Không gộp ngân hàng cũ vào factory chỉ bằng lời khẳng định `verified`. Tên chủ đề có thể dùng alias, nên 89 tên khớp không chứng minh 61 chủ đề còn lại rỗng.

## Những hạng mục chưa thể xác nhận hoàn thành

- 300.000 dạng độc lập, 3.000.000 câu đã kiểm định: **chưa đạt**. Chỉ có 9 dạng demo trong factory, chưa được duyệt tự động. Existing bank vẫn 344.280 câu theo báo cáo/kiểm kê V111.
- Engine AI tạo **dạng mới theo nhiều phương pháp**, thẩm định độc lập về ngữ nghĩa, các bộ xác minh cho toàn bộ Toán 10–12, chấm tự luận nhiều bước: **chưa hoàn thành**.
- Game/practice, Learning, Roadmap và Battle hiện **chưa tự động gọi** API factory mới. API `surface` chuẩn bị đầu mối dùng chung; chuyển traffic thật cần compatibility adapter và bài test riêng.
- Các chức năng tài khoản, kết bạn, chat, notification, Learning, Battle, MathGeo vẫn giữ code V111; nhiều ca hồi quy đã đạt nhưng **không được tuyên bố là sửa/hoàn thiện tất cả**.
- UI responsive trên điện thoại thật, kiểm thử tải, multi-host PostgreSQL, dịch vụ hosting 24/7, backup/monitoring/CI thực: **chưa triển khai xác minh**.

## Bước cần làm để tiếp tục

1. Tạo backup dữ liệu người dùng; chạy test browser E2E cho Battle, tài khoản, chat, geometry, 3 kích thước màn hình.
2. Thiết kế bộ chuyển đổi schema để tích hợp những câu đã được kiểm chứng từ factory vào game/learning/battle theo feature flag; không đổi locked UI.
3. Tạo candidate-method proposals bám sát từng chủ đề, kiểm duyệt con người + phân cụm ngữ nghĩa + bài toán giải kiểm độc lập trước khi duyệt. Đặt mục tiêu chất lượng trước số lượng.
4. Thay SQLite bằng PostgreSQL nếu triển khai nhiều máy chủ, bổ sung Redis/Celery hoặc cơ chế queue phù hợp, lịch backup/restore và cảnh báo.
5. Chạy triển khai staging, đo hiệu năng, xác minh hoạt động 24/7 có watchdog, sau đó mới đưa production.

## Cảnh báo bảo mật V111

Mã gốc có mật khẩu bootstrap admin mặc định. Docker V112 **bắt buộc** người vận hành khai báo `MATHWEB_BOOTSTRAP_ADMIN_PASSWORD`, riêng biệt với `QF_ADMIN_TOKEN`, trước khi khởi động. Việc không truyền mật khẩu admin trong bản chạy local cũ vẫn cần được khắc phục ở lần triển khai tiếp theo.

## Đối chiếu tệp với ZIP đầu vào

3.714 mục gốc được bảo toàn trong ZIP xuất ra; kiểm tra CRC xác nhận `backend/database/mathweb.db`, `verified_seed_bank.jsonl`, `battle.html`, `js/battle.js`, `geometry-studio.html` và `learning-path.html` giống hệt ZIP ban đầu. Chỉ cập nhật nội dung các tệp hiện hữu `.gitignore` và `backend/app/main.py`; các tệp khác của bản nâng cấp được thêm mới.
