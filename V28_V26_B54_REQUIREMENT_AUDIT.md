# MATH_WEB V28 Classic · Kiểm toán B54 và mục tiêu 7.500 dạng

**Kết luận: CHƯA ĐẠT chuẩn 100%** về dạng độc lập và đáp án đúng.

- Ngân hàng nguồn B54 (được tích hợp): `Question_Bank_V254 (6).zip`.
- ZIP website có ngân hàng mới: `MATH_WEB_V28_CLASSIC_V26_B54_AUDIT.zip`.
- SQLite: `MATH_WEB_GITHUB_READY/backend/app/ai/storage/v254_candidates.sqlite`.
- Bảng dữ liệu B54: `b54_word_labels` (kho chờ duyệt, chưa được sử dụng làm câu luyện tập).
- Bảng câu hỏi được hệ thống luyện tập truy vấn: `questions` (83.298 bản ghi được giữ từ V24).
- 150 Word gốc B54 nằm trong `MATH_WEB_GITHUB_READY/question_bank_v254_source/Question_Bank_V254_latest_uploaded.zip`.

## Đối chiếu chỉ tiêu

| Tiêu chí | Kết quả |
|---|---:|
| 150 file Word | 150/150 |
| Nhãn câu từ Word | 95.514 |
| Chủ đề có ≥500 nhãn câu | 150/150 |
| Nhóm dạng có nhãn rõ ràng | 201 |
| Nhóm dạng có nhãn rõ ràng ≥10 nhãn câu | 171 |
| Dạng độc lập thực sự đã kiểm chứng | Chưa có chứng nhận |
| Mục tiêu 7.500 dạng độc lập ×10 câu | **CHƯA ĐẠT / CHƯA THỂ CHỨNG NHẬN** |

## Trạng thái nhãn câu B54

- `candidate_unverified`: **77.059** nhãn.
- `duplicate_exact`: **14.290** nhãn.
- `incomplete`: **331** nhãn.
- `unmapped`: **3.834** nhãn.

**Lưu ý:** Nhãn câu không đồng nghĩa với câu hỏi độc lập. Nhóm có tên và đủ 10 nhãn cũng chưa chắc là một dạng toán độc lập hoặc 10 câu hợp lệ. Việc kiểm định độc lập cần đối chiếu bản chất phương pháp, kiến thức, đáp án, lời giải và chống trùng ngữ nghĩa.

## Kiểm toán theo 150 chủ đề

| # | Khối | File Word | Nhãn | Nhóm dạng rõ tên | Nhóm ≥10 nhãn | Trùng nguyên văn | Chưa ánh xạ | Thiếu dữ liệu |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 10 | 001_Toan_10_Bai_toan_thuc_te_Toan_10.docx | 666 | 0 | 0 | 32 | 0 | 0 |
| 2 | 10 | 002_Toan_10_Bai_toan_tong_hop_uong_thang_va_uong_tron_toa_o.docx | 666 | 51 | 50 | 32 | 0 | 0 |
| 3 | 10 | 003_Toan_10_Bat_phuong_trinh_va_he_bat_phuong_trinh.docx | 634 | 0 | 0 | 83 | 0 | 0 |
| 4 | 10 | 004_Toan_10_Bat_ang_thuc_va_cuc_tri_trong_tam_giac.docx | 634 | 0 | 0 | 90 | 0 | 0 |
| 5 | 10 | 005_Toan_10_Bat_ang_thuc_ai_so_va_cuc_tri_nang_cao.docx | 634 | 0 | 0 | 88 | 0 | 0 |
| 6 | 10 | 006_Toan_10_Chung_minh_hinh_hoc_bang_vecto.docx | 634 | 0 | 0 | 86 | 0 | 0 |
| 7 | 10 | 007_Toan_10_Chung_minh_hinh_hoc_va_bai_toan_tong_hop.docx | 634 | 0 | 0 | 90 | 0 | 0 |
| 8 | 10 | 008_Toan_10_Cac_truong_hop_bang_nhau_cua_tam_giac.docx | 634 | 0 | 0 | 90 | 0 | 0 |
| 9 | 10 | 009_Toan_10_Day_cung_cung_va_khoang_cach_en_tam.docx | 634 | 0 | 0 | 90 | 0 | 0 |
| 10 | 10 | 010_Toan_10_Giao_iem_va_vi_tri_tuong_oi_cua_hai_uong_thang.docx | 634 | 1 | 1 | 90 | 0 | 0 |
| 11 | 10 | 011_Toan_10_Goc_noi_tiep_va_goc_o_tam_nang_cao.docx | 634 | 0 | 0 | 92 | 0 | 0 |
| 12 | 10 | 012_Toan_10_Goc_tao_boi_hai_uong_thang_va_uong_cat.docx | 634 | 0 | 0 | 92 | 0 | 0 |
| 13 | 10 | 013_Toan_10_Hoan_vi_chinh_hop_to_hop.docx | 634 | 2 | 1 | 86 | 0 | 0 |
| 14 | 10 | 014_Toan_10_Ham_so.docx | 634 | 2 | 1 | 80 | 0 | 0 |
| 15 | 10 | 015_Toan_10_Ham_so_bac_hai_va_parabol.docx | 634 | 2 | 1 | 100 | 0 | 0 |
| 16 | 10 | 016_Toan_10_Ham_so_bac_nhat.docx | 634 | 2 | 1 | 104 | 0 | 0 |
| 17 | 10 | 017_Toan_10_Hinh_hoc_co_ban_goc_canh_va_dien_tich.docx | 634 | 2 | 1 | 92 | 0 | 0 |
| 18 | 10 | 018_Toan_10_Hinh_hoc_phang.docx | 634 | 1 | 1 | 94 | 0 | 0 |
| 19 | 10 | 019_Toan_10_He_bat_phuong_trinh.docx | 634 | 0 | 0 | 89 | 0 | 0 |
| 20 | 10 | 020_Toan_10_He_phuong_trinh.docx | 654 | 3 | 3 | 98 | 0 | 0 |
| 21 | 10 | 021_Toan_10_He_phuong_trinh_oi_xung_va_hoan_vi.docx | 634 | 0 | 0 | 0 | 634 | 0 |
| 22 | 10 | 022_Toan_10_He_thuc_luong_trong_tam_giac.docx | 634 | 2 | 1 | 92 | 0 | 0 |
| 23 | 10 | 023_Toan_10_Menh_e.docx | 644 | 1 | 1 | 484 | 0 | 0 |
| 24 | 10 | 024_Toan_10_Menh_e_va_tap_hop.docx | 634 | 1 | 1 | 86 | 0 | 20 |
| 25 | 10 | 025_Toan_10_Nhi_thuc_Newton.docx | 664 | 2 | 2 | 116 | 0 | 0 |
| 26 | 10 | 026_Toan_10_Phuong_trinh.docx | 634 | 0 | 0 | 88 | 0 | 0 |
| 27 | 10 | 027_Toan_10_Phuong_trinh_chua_can_thuc_nang_cao.docx | 634 | 0 | 0 | 94 | 0 | 0 |
| 28 | 10 | 028_Toan_10_Phuong_trinh_va_he_phuong_trinh.docx | 634 | 1 | 1 | 110 | 0 | 0 |
| 29 | 10 | 029_Toan_10_Quy_tac_em.docx | 644 | 1 | 1 | 0 | 644 | 0 |
| 30 | 10 | 030_Toan_10_Quy_tich_iem_trong_mat_phang.docx | 634 | 4 | 4 | 86 | 0 | 0 |
| 31 | 10 | 031_Toan_10_Tam_giac_va_tu_giac_co_ban.docx | 634 | 1 | 1 | 103 | 0 | 0 |
| 32 | 10 | 032_Toan_10_Thong_ke.docx | 654 | 2 | 1 | 72 | 0 | 0 |
| 33 | 10 | 033_Toan_10_Tiep_tuyen_va_day_cung_cua_uong_tron.docx | 634 | 1 | 1 | 96 | 0 | 0 |
| 34 | 10 | 034_Toan_10_Trung_iem_va_khoang_cach_trong_toa_o_phang.docx | 634 | 3 | 2 | 53 | 0 | 0 |
| 35 | 10 | 035_Toan_10_Tinh_chat_hinh_binh_hanh_va_hinh_thoi.docx | 634 | 0 | 0 | 96 | 0 | 0 |
| 36 | 10 | 036_Toan_10_Tap_hop_va_cac_phep_toan.docx | 634 | 1 | 1 | 72 | 0 | 0 |
| 37 | 10 | 037_Toan_10_Ti_so_dien_tich_tam_giac.docx | 634 | 0 | 0 | 96 | 0 | 0 |
| 38 | 10 | 038_Toan_10_Toa_o_trong_mat_phang.docx | 634 | 1 | 1 | 110 | 0 | 0 |
| 39 | 10 | 039_Toan_10_Toa_o_va_uong_thang_trong_mat_phang.docx | 634 | 2 | 1 | 90 | 0 | 0 |
| 40 | 10 | 040_Toan_10_To_hop_va_nguyen_ly_Dirichlet_nang_cao.docx | 644 | 0 | 0 | 102 | 0 | 0 |
| 41 | 10 | 041_Toan_10_Vecto.docx | 634 | 2 | 1 | 52 | 0 | 0 |
| 42 | 10 | 042_Toan_10_Xac_suat.docx | 644 | 2 | 1 | 87 | 0 | 0 |
| 43 | 10 | 043_Toan_10_Chia_Du.docx | 654 | 2 | 2 | 0 | 654 | 0 |
| 44 | 10 | 044_Toan_10_Chia_Het.docx | 654 | 2 | 2 | 0 | 654 | 0 |
| 45 | 10 | 045_Toan_10_Phuong_Trinh_Bac_Hai.docx | 644 | 0 | 0 | 120 | 0 | 0 |
| 46 | 10 | 046_Toan_10_uong_thang.docx | 634 | 1 | 1 | 0 | 624 | 10 |
| 47 | 10 | 047_Toan_10_uong_trung_tuyen_phan_giac_va_uong_cao.docx | 634 | 2 | 1 | 96 | 0 | 0 |
| 48 | 10 | 048_Toan_10_uong_tron.docx | 634 | 2 | 1 | 94 | 0 | 0 |
| 49 | 10 | 049_Toan_10_uong_tron_va_cac_goc_co_ban.docx | 634 | 2 | 1 | 96 | 0 | 0 |
| 50 | 10 | 050_Toan_10_inh_ly_Thales_va_tam_giac_ong_dang.docx | 634 | 0 | 0 | 94 | 0 | 0 |
| 51 | 11 | 051_Toan_11_Bien_co_oc_lap_va_xac_suat_co_ieu_kien.docx | 634 | 2 | 1 | 92 | 0 | 0 |
| 52 | 11 | 052_Toan_11_Bai_toan_thuc_te_Toan_11.docx | 634 | 1 | 1 | 94 | 0 | 0 |
| 53 | 11 | 053_Toan_11_Bai_toan_thuc_te_tong_hop_Toan_11.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 54 | 11 | 054_Toan_11_Chung_minh_tong_hop_song_song_va_vuong_goc.docx | 634 | 1 | 1 | 98 | 0 | 0 |
| 55 | 11 | 055_Toan_11_Cong_thuc_luong_giac.docx | 634 | 1 | 1 | 104 | 0 | 0 |
| 56 | 11 | 056_Toan_11_Cap_so_cong.docx | 644 | 1 | 1 | 95 | 0 | 0 |
| 57 | 11 | 057_Toan_11_Cap_so_nhan.docx | 644 | 1 | 1 | 97 | 0 | 0 |
| 58 | 11 | 058_Toan_11_Day_so.docx | 644 | 0 | 0 | 103 | 0 | 0 |
| 59 | 11 | 059_Toan_11_Day_so.docx | 634 | 1 | 1 | 99 | 0 | 0 |
| 60 | 11 | 060_Toan_11_Day_so_truy_hoi.docx | 644 | 1 | 1 | 94 | 0 | 0 |
| 61 | 11 | 061_Toan_11_Day_so_truy_hoi_va_bai_toan_cuc_tri.docx | 634 | 1 | 1 | 104 | 0 | 0 |
| 62 | 11 | 062_Toan_11_Dung_thiet_dien_cua_hinh_chop_va_lang_tru.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 63 | 11 | 063_Toan_11_Gia_tri_luong_giac.docx | 634 | 2 | 1 | 112 | 0 | 0 |
| 64 | 11 | 064_Toan_11_Gioi_han.docx | 644 | 1 | 1 | 83 | 0 | 0 |
| 65 | 11 | 065_Toan_11_Gioi_han_ham_so.docx | 634 | 2 | 1 | 108 | 0 | 0 |
| 66 | 11 | 066_Toan_11_Goc_giua_uong_thang_va_mat_phang.docx | 634 | 1 | 1 | 98 | 0 | 0 |
| 67 | 11 | 067_Toan_11_Goc_va_khoang_cach_trong_khong_gian.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 68 | 11 | 068_Toan_11_Hai_mat_phang_song_song.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 69 | 11 | 069_Toan_11_Ham_so_lien_tuc.docx | 644 | 1 | 1 | 97 | 0 | 0 |
| 70 | 11 | 070_Toan_11_Ham_so_luong_giac.docx | 634 | 1 | 1 | 94 | 0 | 0 |
| 71 | 11 | 071_Toan_11_Hop_thanh_cac_phep_bien_hinh.docx | 644 | 1 | 1 | 104 | 0 | 0 |
| 72 | 11 | 072_Toan_11_Khoang_cach_giua_hai_uong_thang_cheo_nhau.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 73 | 11 | 073_Toan_11_Mo_hinh_xac_suat_co_ieu_kien.docx | 634 | 1 | 1 | 98 | 0 | 0 |
| 74 | 11 | 074_Toan_11_Mat_ben_canh_ben_va_ay_cua_lang_tru_hinh_chop.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 75 | 11 | 075_Toan_11_Nhan_biet_hinh_hoc_khong_gian.docx | 634 | 1 | 1 | 96 | 0 | 10 |
| 76 | 11 | 076_Toan_11_Nhan_biet_uong_thang_va_mat_phang_trong_khong_gian.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 77 | 11 | 077_Toan_11_Nhi_thuc_Newton_va_he_so_to_hop_nang_cao.docx | 644 | 1 | 1 | 122 | 0 | 0 |
| 78 | 11 | 078_Toan_11_Phep_bien_hinh_co_ban.docx | 634 | 1 | 1 | 93 | 0 | 0 |
| 79 | 11 | 079_Toan_11_Phep_bien_hinh_trong_mat_phang.docx | 634 | 1 | 1 | 95 | 0 | 0 |
| 80 | 11 | 080_Toan_11_Phep_quay_va_phep_vi_tu.docx | 644 | 0 | 0 | 104 | 0 | 0 |
| 81 | 11 | 081_Toan_11_Phep_tinh_tien_va_anh_cua_hinh.docx | 634 | 1 | 1 | 104 | 0 | 10 |
| 82 | 11 | 082_Toan_11_Phep_oi_xung_truc.docx | 644 | 0 | 0 | 95 | 0 | 0 |
| 83 | 11 | 083_Toan_11_Phuong_trinh_luong_giac.docx | 634 | 0 | 0 | 96 | 0 | 0 |
| 84 | 11 | 084_Toan_11_Phuong_trinh_luong_giac.docx | 634 | 1 | 1 | 98 | 0 | 0 |
| 85 | 11 | 085_Toan_11_Phuong_trinh_luong_giac_nang_cao.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 86 | 11 | 086_Toan_11_Quan_he_song_song_trong_khong_gian.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 87 | 11 | 087_Toan_11_Quan_he_song_song_va_vuong_goc_trong_khong_gian.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 88 | 11 | 088_Toan_11_Quan_he_vuong_goc_trong_khong_gian.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 89 | 11 | 089_Toan_11_Quy_nap_toan_hoc.docx | 644 | 0 | 0 | 106 | 0 | 0 |
| 90 | 11 | 090_Toan_11_Quy_tac_ao_ham.docx | 634 | 1 | 1 | 86 | 0 | 0 |
| 91 | 11 | 091_Toan_11_Thiet_dien_hinh_khong_gian.docx | 634 | 1 | 1 | 99 | 0 | 10 |
| 92 | 11 | 092_Toan_11_Thiet_dien_va_ti_so_oan_trong_hinh_khong_gian.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 93 | 11 | 093_Toan_11_Thong_ke_Toan_11.docx | 644 | 2 | 1 | 116 | 0 | 0 |
| 94 | 11 | 094_Toan_11_To_hop_va_xac_suat_nang_cao.docx | 644 | 1 | 1 | 98 | 0 | 10 |
| 95 | 11 | 095_Toan_11_Xac_suat.docx | 634 | 1 | 1 | 113 | 0 | 0 |
| 96 | 11 | 096_Toan_11_uong_thang_song_song_voi_mat_phang.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 97 | 11 | 097_Toan_11_uong_thang_vuong_goc_voi_mat_phang.docx | 634 | 1 | 1 | 98 | 0 | 10 |
| 98 | 11 | 098_Toan_11_ao_ham.docx | 634 | 2 | 1 | 105 | 0 | 0 |
| 99 | 11 | 099_Toan_11_inh_ly_ba_uong_vuong_goc.docx | 634 | 1 | 1 | 0 | 624 | 10 |
| 100 | 11 | 100_Toan_11_Ung_dung_ao_ham.docx | 634 | 1 | 1 | 97 | 0 | 0 |
| 101 | 12 | 101_Toan_12_Bieu_dien_so_phuc.docx | 642 | 0 | 0 | 77 | 0 | 1 |
| 102 | 12 | 102_Toan_12_Bai_toan_tham_so_hinh_hoc_Oxyz.docx | 632 | 1 | 1 | 92 | 0 | 10 |
| 103 | 12 | 103_Toan_12_Bai_toan_thuc_te_Toan_12.docx | 632 | 1 | 1 | 94 | 0 | 0 |
| 104 | 12 | 104_Toan_12_Bai_toan_toi_uu_hinh_hoc_khong_gian.docx | 632 | 1 | 1 | 94 | 0 | 10 |
| 105 | 12 | 105_Toan_12_Bai_toan_tong_hop_THPT.docx | 632 | 1 | 1 | 96 | 0 | 10 |
| 106 | 12 | 106_Toan_12_Bat_phuong_trinh_logarit.docx | 632 | 1 | 1 | 86 | 0 | 0 |
| 107 | 12 | 107_Toan_12_Bat_phuong_trinh_mu.docx | 632 | 0 | 0 | 81 | 0 | 0 |
| 108 | 12 | 108_Toan_12_Cac_so_ac_trung_o_xu_the_va_o_phan_tan.docx | 642 | 2 | 1 | 102 | 0 | 0 |
| 109 | 12 | 109_Toan_12_Cuc_tri.docx | 632 | 0 | 0 | 92 | 0 | 0 |
| 110 | 12 | 110_Toan_12_Cuc_tri_khoang_cach_trong_khong_gian_toa_o.docx | 632 | 0 | 0 | 94 | 0 | 0 |
| 111 | 12 | 111_Toan_12_Dien_tich_xung_quanh_va_toan_phan_hinh_khoi.docx | 632 | 2 | 1 | 92 | 0 | 0 |
| 112 | 12 | 112_Toan_12_Giao_tuyen_mat_cau_va_mat_phang.docx | 642 | 0 | 0 | 177 | 0 | 0 |
| 113 | 12 | 113_Toan_12_Giao_iem_uong_thang_va_mat_phang.docx | 632 | 0 | 0 | 94 | 0 | 0 |
| 114 | 12 | 114_Toan_12_Gia_tri_lon_nhat_va_nho_nhat.docx | 632 | 0 | 0 | 94 | 0 | 0 |
| 115 | 12 | 115_Toan_12_Goc_giua_hai_mat_phang.docx | 632 | 0 | 0 | 102 | 0 | 0 |
| 116 | 12 | 116_Toan_12_Goc_giua_uong_thang_va_mat_phang_Oxyz.docx | 632 | 1 | 1 | 94 | 0 | 10 |
| 117 | 12 | 117_Toan_12_Goc_va_khoang_cach_Oxyz.docx | 632 | 1 | 1 | 94 | 0 | 10 |
| 118 | 12 | 118_Toan_12_Ham_so_logarit.docx | 632 | 2 | 1 | 90 | 0 | 0 |
| 119 | 12 | 119_Toan_12_Ham_so_mu.docx | 642 | 1 | 1 | 96 | 0 | 10 |
| 120 | 12 | 120_Toan_12_Hinh_hoc_khong_gian.docx | 632 | 1 | 1 | 104 | 0 | 10 |
| 121 | 12 | 121_Toan_12_Hinh_hoc_so_phuc_va_quy_tich.docx | 652 | 1 | 1 | 103 | 0 | 0 |
| 122 | 12 | 122_Toan_12_Hinh_khoi_va_the_tich_co_ban.docx | 632 | 1 | 1 | 90 | 0 | 0 |
| 123 | 12 | 123_Toan_12_Khoang_cach_tu_iem_en_mat_phang.docx | 632 | 2 | 1 | 88 | 0 | 0 |
| 124 | 12 | 124_Toan_12_Khao_sat_va_ve_o_thi_ham_so.docx | 632 | 1 | 1 | 96 | 0 | 10 |
| 125 | 12 | 125_Toan_12_Mat_cau.docx | 632 | 1 | 1 | 147 | 0 | 0 |
| 126 | 12 | 126_Toan_12_Mat_phang_tiep_xuc_voi_mat_cau.docx | 642 | 1 | 1 | 128 | 0 | 0 |
| 127 | 12 | 127_Toan_12_Mat_phang_trong_Oxyz.docx | 632 | 1 | 1 | 84 | 0 | 0 |
| 128 | 12 | 128_Toan_12_Nguyen_ham_va_tich_phan.docx | 642 | 1 | 1 | 76 | 0 | 0 |
| 129 | 12 | 129_Toan_12_Phuong_trinh_logarit.docx | 632 | 0 | 0 | 106 | 0 | 0 |
| 130 | 12 | 130_Toan_12_Phuong_trinh_mu.docx | 632 | 0 | 0 | 104 | 0 | 0 |
| 131 | 12 | 131_Toan_12_Phuong_trinh_mat_cau_va_tam_ban_kinh.docx | 632 | 0 | 0 | 162 | 0 | 0 |
| 132 | 12 | 132_Toan_12_Phuong_trinh_mat_phang.docx | 652 | 1 | 1 | 130 | 0 | 0 |
| 133 | 12 | 133_Toan_12_Phuong_trinh_so_phuc.docx | 632 | 1 | 1 | 94 | 0 | 0 |
| 134 | 12 | 134_Toan_12_Phuong_trinh_uong_thang_trong_Oxyz.docx | 632 | 2 | 1 | 94 | 0 | 0 |
| 135 | 12 | 135_Toan_12_So_phuc.docx | 632 | 2 | 1 | 114 | 0 | 0 |
| 136 | 12 | 136_Toan_12_The_tich_hinh_hoc_khong_gian.docx | 632 | 2 | 1 | 102 | 0 | 0 |
| 137 | 12 | 137_Toan_12_The_tich_khoi_tron_xoay_va_mo_hinh_thuc_te.docx | 632 | 1 | 1 | 94 | 0 | 10 |
| 138 | 12 | 138_Toan_12_Tiep_tuyen.docx | 632 | 1 | 1 | 94 | 0 | 0 |
| 139 | 12 | 139_Toan_12_Tiem_can.docx | 642 | 1 | 1 | 96 | 0 | 0 |
| 140 | 12 | 140_Toan_12_Tinh_on_ieu.docx | 632 | 1 | 1 | 88 | 0 | 0 |
| 141 | 12 | 141_Toan_12_Tuong_giao_o_thi.docx | 632 | 1 | 1 | 94 | 0 | 0 |
| 142 | 12 | 142_Toan_12_Toa_o_trong_khong_gian.docx | 642 | 0 | 0 | 104 | 0 | 0 |
| 143 | 12 | 143_Toan_12_Toi_uu_va_cuc_tri_bang_tich_phan.docx | 632 | 1 | 1 | 94 | 0 | 10 |
| 144 | 12 | 144_Toan_12_Vecto_va_o_dai_trong_khong_gian_Oxyz.docx | 632 | 0 | 0 | 86 | 0 | 0 |
| 145 | 12 | 145_Toan_12_Van_dung_toa_o_Oxyz.docx | 632 | 1 | 1 | 104 | 0 | 0 |
| 146 | 12 | 146_Toan_12_Vi_tri_tuong_oi_cua_hai_uong_thang_trong_Oxyz.docx | 642 | 1 | 1 | 104 | 0 | 10 |
| 147 | 12 | 147_Toan_12_Xac_suat_va_bien_ngau_nhien.docx | 652 | 2 | 1 | 112 | 0 | 0 |
| 148 | 12 | 148_Toan_12_uong_thang_trong_Oxyz.docx | 632 | 1 | 1 | 92 | 0 | 0 |
| 149 | 12 | 149_Toan_12_Ung_dung_tich_phan.docx | 632 | 2 | 1 | 108 | 0 | 0 |
| 150 | 12 | 150_Toan_12_Ung_dung_ao_ham.docx | 642 | 2 | 1 | 105 | 0 | 0 |

## Cách xác định khi nào thực sự đạt 100%

Đối với mỗi chủ đề, phải lập danh mục 50 dạng độc lập theo bản chất và phương pháp giải; mỗi dạng có 10 câu khác nhau, đáp án và lời giải đã qua kiểm chứng; so khớp với ngân hàng hiện có để tránh đếm trùng. Chỉ khi cả 150 chủ đề đạt các tiêu chí này mới xác nhận 7.500 dạng và 75.000 câu.

## Bảo toàn mã nguồn

Gói V26 không sửa logic luyện tập hoặc giao diện; chỉ thêm báo cáo kiểm toán. Các nhãn B54 chưa thẩm định vẫn không được tự động kích hoạt trong luyện tập.
