# Rà soát lỗi tiềm ẩn MATH_WEB (04/11/2026)

## Lỗi đã xác minh và sửa
- Mapping `quadratic-equation` trỏ nhầm sang `phuong_trinh_he`, khiến game phương trình bậc hai có thể nhận câu hỏi hệ phương trình. Đã đổi sang `ham_so_bac_hai` và hỗ trợ alias có dấu gạch dưới.
- Bộ so sánh đáp án chưa nhận hằng số `pi` trong biểu thức số học, có thể bỏ sót hai đáp án trắc nghiệm tương đương. Đã hỗ trợ `pi` trong biểu thức số học giới hạn, không dùng `eval`.
- Bổ sung kiểm thử hồi quy cho hai lỗi trên.

## Rủi ro chưa khắc phục / chưa xác nhận
- Các alias game cũ như `geometry`, `radical`, `remainder` đang được gán sang `menh_de_tap_hop` không phù hợp nội dung. Cần định nghĩa mapping theo game, lớp và chủ đề trước khi sửa hàng loạt.
- Chưa chứng minh mọi câu hỏi sinh ra đều đúng, duy nhất và không trùng về cấu trúc.
- Chưa kiểm thử tích hợp thực tế nhiều tài khoản, Battle, chat, Admin và đăng nhập qua nhiều lần khởi động.
- Chưa đạt 1.000 dạng bài mỗi chủ đề, 10–15 câu mỗi dạng.
- Mật khẩu token có fallback secret local tĩnh; khi triển khai công khai cần đặt MATH_WEB_SECRET_KEY bí mật trong môi trường và bảo vệ thông tin đăng nhập.

Bản cập nhật này chỉ sửa các lỗi có thể xác minh bằng mã nguồn và kiểm thử; không phải chứng nhận hoàn thiện 100%.
