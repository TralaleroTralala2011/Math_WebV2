# MATH_WEB: trạng thái video thực tế

- Đã nâng cấp bộ phát để ưu tiên video đã kiểm duyệt trong JSON tĩnh và tránh trùng ID giữa Học tập/Lộ trình.
- Đã bổ sung kiểm tra catalogue tại `scripts/audit_video_catalogue.py`.
- **Chưa có 900 video được xác minh.** File catalogue hiện rỗng; không được coi 900 ô video là 900 bài giảng.
- Backend tìm kiếm YouTube chỉ là nguồn gợi ý, không chứng minh video đúng chủ đề hay cho phép nhúng.
- Để hoàn thành: nghiên cứu, tuyển chọn và xác minh từng URL, đối chiếu với 150 chủ đề, kiểm tra chất lượng và phát nhúng thực tế.
- Không thể tuyên bố 100% khi các bước này chưa thực hiện.
