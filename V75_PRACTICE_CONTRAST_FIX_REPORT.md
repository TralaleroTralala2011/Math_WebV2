# MATH_WEB V75 | Sửa tương phản chữ/đáp án trong popup Luyện tập AI

Nguồn: MATH_WEB V74, không thay mã chấm bài, Battle, Admin, database, ngân hàng câu hỏi.

## Nguyên nhân
`css/practice-v44-vio-inspired.css` đổi panel sang màu trắng, trong khi
`js/practise.js` chèn CSS giao diện tối đặt `.mathweb-ai-option { color:#fff }`.
Do đó lựa chọn có chữ trắng trên nền trắng và người học tưởng không có đáp án.

## Tệp thay đổi
- `css/practice-v44-vio-inspired.css`: các quy tắc giới hạn trong `.mathweb-ai-panel`;
  màu văn bản, đáp án, Đúng/Sai, tự luận, nút, phản hồi, lời giải và focus.
- `practice.html`, `practise.html`: thêm `?v=75-contrast` để xóa cache CSS cũ.

## Kiểm tra
- Chạy Chromium bằng Playwright, mô phỏng CSS cũ được JS chèn SAU CSS đã sửa.
- Hai viewport 1280x840 và 393x852: màu nền/chữ thực tế đều rõ, đáp án hiển thị.
- Chữ đáp án: rgb(23,43,69) / nền rgb(242,247,253).
- Nút chính: rgb(255,255,255) / nền rgb(21,110,197).
- Có ảnh minh chứng test nội bộ, không thuộc mã sản phẩm.

## Giới hạn
- Đây là vá lỗi tương phản cho popup AI luyện tập; chưa phải kiểm thử live GitHub Pages hoặc Render.
- Lỗi console Kaspersky (gc.kis.v2.scr.kaspersky-labs.com) thuộc tiện ích/phần mềm
  bảo vệ trình duyệt; không sửa bằng CSS website.
- Không thay thế/động chạm dữ liệu tài khoản hay ngân hàng Word, JSON, SQLite.
