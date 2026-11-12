# MATH_WEB V181 | Bản mã nguồn website và ngân hàng câu hỏi

## Nguồn thực tế

- Mã nguồn website: `MATH_WEB_GITHUB_READY_V167_INTEGRATION_PATCH.zip` (bản đầy đủ mới nhất có thể mở trong phiên).
- Dữ liệu mới: các checkpoint V179 và V180.
- Không xác minh được commit GitHub mới nhất, không ghi lên máy chủ production.
- **Không phải bản chứng nhận website hoàn thành 100%.**

## Các sửa đổi trực tiếp trong website

1. `backend/app/ai/engine/service.py`: sửa truy vấn câu hỏi Admin theo đúng chủ đề, độ khó, loại câu hỏi và game **trước khi giới hạn kết quả**. Ngăn câu hỏi hợp lệ bị bỏ sót khi ngân hàng tăng lớn.
2. `backend/app/ai/engine/difficulty.py`: chuẩn hóa `foundation`, `intermediate`, `advanced` về `easy`, `medium`, `hard` để không phân loại sai dữ liệu nhập.
3. `backend/app/admin_routes.py`: chấm bài tập được giao bằng cùng bộ chấm toán học như Luyện tập/Battle, nhận đáp án tương đương; chọn câu theo độ khó/định dạng đã yêu cầu; bổ sung bằng AI nếu thiếu và được cho phép; không âm thầm giao ít câu hơn chỉ tiêu.
4. `backend/app/ai/engine/solver.py`: giới hạn độ phức tạp biểu thức số để tránh lũy thừa khổng lồ từ dữ liệu đầu vào; hỗ trợ cú pháp `^` an toàn.
5. `backend/app/verified_bank_routes.py`: tạo chỉ mục vị trí câu hỏi theo tệp 344.280 dòng để không phải phân tích lại toàn bộ JSONL lớn ở mỗi yêu cầu `/next` và `/catalog`. Không thay đổi nội dung ngân hàng gốc.
6. `backend/scripts/import_bank_updates.py` + `IMPORT_BANK_V181.bat`: công cụ nhập có sao lưu, kiểm chứng, kiểm tra trùng, giao dịch nguyên tử và truy vết nguồn.
7. `backend/tests/test_v181_web_regressions.py`: kiểm thử hồi quy cho các sửa đổi trên.

## Bằng chứng

- Bộ kiểm thử backend chạy theo 3 nhóm: **76 + 32 + 7 = 115 bài đạt**. Chưa chạy trọn bộ test suite đến cuối do giới hạn thời gian thực thi.
- JavaScript `node --check`: `battle.js`, `practise.js`, `practice-mathgeo-bridge.js` đạt.
- Geometry runtime: `v96_mathgeo_runtime_test.cjs` và `v97_triangle_sss_test.cjs` đạt.
- Nhập thử nghiệm: 3.695 câu được thêm; lần hai 0; truy xuất từ Luyện tập và bài tập được giao đạt; chấm đúng các đáp án thử nghiệm.
- **35 câu trắc nghiệm bị cách ly**, không nhập do phương án nhiễu tương đương toán học.

## Những gì chưa thể xác nhận

- Không có quyền ghi vào dữ liệu production hoặc commit GitHub mới nhất.
- Chưa kiểm thử trình duyệt thực tế trên Windows, Android và iOS, cũng như tải đồng thời quy mô lớn.
- Chưa chứng nhận tính độc lập của mọi dạng toán, toàn bộ lời giải và mục tiêu 300.000 dạng/3.000.000 câu.
- Không khẳng định Battle, Admin, tài khoản, hình học và tất cả chức năng đạt 100% trong mọi trường hợp chỉ từ các bài kiểm thử đã chạy.

## Bảo toàn dữ liệu

Bản ZIP phát hành **không chứa `mathweb.db`, `question_factory.sqlite3`, tệp `.env` riêng tư hay WAL**. Khi cập nhật dự án đang sử dụng, hãy giữ nguyên thư mục dữ liệu hoặc cấu hình `MATHWEB_DATA_DIR` / `MATHWEB_DB_PATH`; không thay thế database đang hoạt động bằng database thử nghiệm. Dùng `IMPORT_BANK_V181.bat` để bổ sung an toàn.
