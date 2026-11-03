# Báo cáo tích hợp yêu cầu AI tạo đề + AI dựng hình + 45 chủ đề

## Phần đã tích hợp trong bản này

- Giữ nguyên nền dự án MATH_WEB và các trang hiện có; không thay thế giao diện.
- Giữ tài liệu yêu cầu 45 chủ đề và tài liệu B1/C1 do người dùng cung cấp.
- Thêm tài liệu đặc tả tổng hợp `MATH_WEB_MASTER_REQUIREMENTS_AI_GEOMETRY_2026-10-16.md`, gom các tiêu chí về đa dạng câu hỏi, lời giải, kiểm chứng, cấp độ, chống lặp, dựng hình 2D/3D/tọa độ, tính đúng dữ kiện, tích hợp và tiêu chuẩn nghiệm thu.
- Thêm `backend/scripts/audit_ai_geometry_catalog.py` để kiểm tra ID trùng, tổng số bản ghi và phân bổ chính xác 45 chủ đề hình học theo khối/cấp độ.
- Không chỉnh sửa HTML/CSS của Practice, Game, Battle, kết bạn và trò chuyện trong đợt tích hợp đặc tả này.

## Kết quả kiểm tra trong môi trường đóng gói

- `cd backend && python -m pytest -q`: **72 passed**.
- `cd backend && python scripts/audit_ai_geometry_catalog.py`: **PASS**.
- Danh mục: lớp 10 = 45, lớp 11 = 47, lớp 12 = 47; tổng 139 bản ghi; 139 ID duy nhất.
- 45 chủ đề hình học mới: lớp 10 = 5/5/5, lớp 11 = 5/5/5, lớp 12 = 5/5/5 theo Nền tảng/Trung cấp/Nâng cao.

## Chênh lệch chưa được phép che giấu

Yêu cầu nêu 102 chủ đề hiện có + 45 chủ đề mới = mục tiêu dự kiến 147. Nhưng danh mục `backend/app/ai/knowledge/index.json` hiện có 139 bản ghi, trong đó 45 là chủ đề mới, tức chỉ có 94 bản ghi không thuộc đợt mở rộng. Còn thiếu căn cứ để giải thích 8 chủ đề so với mốc 102. Bản này **không** tự thêm tám chủ đề giả và **không** tuyên bố đã đạt 147.

## Giới hạn sản phẩm cần tiếp tục xử lý

- Bộ sinh hiện tại là hệ thống quy tắc/ngân hàng mẫu/bộ ghép bài toán nội bộ, không phải kết nối LLM tổng quát tương đương ChatGPT. Nó chưa đảm bảo suy luận mở cho mọi yêu cầu tự do.
- Dựng hình chính xác hiện được hỗ trợ bởi các hàm cấu trúc cho những dạng đã triển khai; không phải bộ giải ràng buộc hình học phổ quát.
- Xoay 3D là hiển thị wireframe có phép chiếu, không phải trình dựng hình tham số đầy đủ kiểu GeoGebra/CAD.
- Chưa tuyên bố 45 chủ đề mới có 45 engine game HTML độc lập.
- Kiểm thử tự động không thay thế kiểm tra thủ công trình duyệt trên máy người dùng; cần chạy smoke test các luồng Practice, Battle, kết bạn, chat và các game sau khi tải bản ZIP.

## Kết luận

Đặc tả mới đã được đưa vào gói dự án và có công cụ kiểm toán dữ liệu để tránh tuyên bố sai về số lượng. Đây là bản tích hợp đặc tả và kiểm tra tự động, không phải tuyên bố mọi tiêu chí AI tổng quát đã hoàn tất.
