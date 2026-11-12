# MATH_WEB · NEON V24 · Trainable AI Tutor

Ngày: 2026-11-12. Nền: ZIP NEON V23 `MATH_WEB_GITHUB_READY_NEON_V23_ADAPTIVE_AI_TUTOR_2026-11-12.zip`.

## Đã triển khai

1. **Mô hình có huấn luyện thật từ dữ liệu:** `backend/app/learner_online.py` xây dựng logistic predictor cá nhân và cập nhật hệ số bằng online stochastic gradient descent. Đặc trưng gồm mức độ câu hỏi (Nền tảng/Trung cấp/Nâng cao), tỉ lệ đúng trước đó theo chủ đề và tỉ lệ đúng theo mức độ. Dự đoán mục tiêu là **khả năng trả lời đúng câu hỏi mới**, không phải kết luận IQ/học lực hay bằng chứng về độ chuẩn hóa.
2. **Tự động train khi chấm bài:** `roadmap_v2_routes.py` chỉ đưa kết quả **đúng/sai** của **câu đã kiểm chứng độc lập** vào mô hình; không train từ câu ứng viên, câu bỏ qua hoặc lần làm lặp cùng mã câu. Luồng cập nhật diễn ra trong cùng giao dịch SQLite khi nộp bài. Vẫn giữ BKT V23 để theo dõi kỹ năng.
3. **Dữ liệu được cô lập:** bảng SQLite `roadmap_v2_personal_predictors` có khóa `(user_id, grade)`, chứa hệ số và số liệu tổng hợp. Không đưa câu hỏi, đáp án hay danh tính khác vào bảng hệ số. Đề và đáp án vẫn do máy chủ chấm.
4. **Tự tái huấn luyện/khôi phục:** Endpoint đăng nhập `POST /api/roadmap-v2/tutor/retrain/{grade}` tái dựng từ lịch sử V23 có xác thực; cùng dữ liệu cho kết quả nhất quán. Hồ sơ V23 có thể khởi tạo mô hình mới khi mở gia sư.
5. **Lộ trình ôn luyện cá nhân hóa:** dự đoán ba mức độ cho từng chủ đề chỉ khi có tối thiểu 12 câu đã dùng huấn luyện, ít nhất ba câu ở chủ đề đó và sai số Brier tuần tự nhỏ hơn mốc 0,25. Nếu không đủ thì dùng gợi ý theo dữ liệu trước đó, không phán đoán bừa. Khóa ba chủ đề và ngưỡng 25/30 **không đổi**.
6. **Giao diện:** trong `learning-path.html`, bảng gia sư có nút tái huấn luyện, số bằng chứng đã học, và dự đoán thử nghiệm theo mức độ khi đủ dữ liệu. Xác suất được làm tròn theo chục phần trăm và luôn cảnh báo chưa hiệu chuẩn. Xuất JSON hồ sơ cá nhân có thêm báo cáo mô hình.

## Đường dẫn API được cập nhật

- `POST /api/roadmap-v2/submit/{attempt_id}`: cập nhật BKT và mô hình logistic cùng giao dịch.
- `POST /api/roadmap-v2/tutor/retrain/{grade}`: khôi phục/huấn luyện lại từ lịch sử **đã duyệt**, theo tài khoản đang đăng nhập.
- `GET /api/roadmap-v2/tutor/{grade}`: trả `online_training` và dự đoán theo chủ đề khi đủ điều kiện.
- `GET /api/roadmap-v2/tutor-plan/{grade}`: trả `trained_predictor` và `predicted_correct_by_tier`, không mở khóa vượt quy tắc.
- `GET /api/roadmap-v2/tutor-data/{grade}`: xuất dữ liệu riêng của tài khoản và thống kê mô hình, không chứa đáp án chuẩn.

## Kiểm thử thực tế

- **203/203** kiểm thử backend chính đạt (`pytest -q --ignore=tests/test_trig_generation.py`).
- **13/13** kiểm thử sinh lượng giác đạt (`pytest -q tests/test_trig_generation.py`).
- **216/216** tổng ca đạt, chạy hai nhóm riêng.
- **5 kiểm thử mới**: cập nhật hệ số từ dữ liệu, bảo vệ bỏ qua/lặp/ứng viên, hành vi xác suất, tái huấn luyện nhất quán, cách ly hai tài khoản, endpoint nộp bài thật và giao diện.
- `node --check js/roadmap-v5.js` và `py_compile` đạt.

## Giới hạn cần công bố

- Đây là **AI dự đoán online cá nhân theo dữ liệu** chứ không phải huấn luyện lại một LLM; hệ số được học nhưng chưa **hiệu chuẩn hay thẩm định trên tập học sinh đại diện**. Sai số Brier tuần tự chỉ là chỉ số kỹ thuật, không phải bằng chứng về tính công bằng hay khả năng phân loại năng lực tổng thể.
- Vẫn **chưa đủ bộ đề đầu vào lớp 10–12 được kiểm chứng và công bố**. Do đó, việc sử dụng AI với bài đầu vào chính thức vẫn bị hệ thống khóa khi thiếu dữ liệu đạt chuẩn.
- Dữ liệu Luyện tập/Battle không mặc nhiên nhập vào mô hình vì chưa có bảo chứng chất lượng/nguồn gốc tương đương đề đã duyệt. Các bước tiếp theo cần kiểm định ngân hàng, thử nghiệm giáo dục thực tế, hiệu chuẩn mô hình.
- Chưa kiểm thử end-to-end ngoài thực địa trên điện thoại và nhiều người dùng cùng lúc trong lần nâng cấp này.
- ZIP **không** chứa `backend/database/mathweb.db` hoặc `.mathweb_hmac_secret`. Cần sao lưu cả database và khóa trước khi cập nhật.
