"""Problem archetypes for the additive MATH WEB problem generator.

This module intentionally does not replace the old question bank.  It provides
reusable *problem shapes* that can be combined with different topics, contexts,
data sets and part types.
"""
from __future__ import annotations

ARCHETYPES = [
    {"id": "missing_data", "name": "Dữ liệu bị thiếu", "tags": ["table", "real_life", "reverse"]},
    {"id": "reverse_result", "name": "Bài toán ngược", "tags": ["reverse", "reasoning"]},
    {"id": "multi_stage_real_life", "name": "Tình huống thực tế nhiều bước", "tags": ["real_life", "multi_step"]},
    {"id": "experiment_to_model", "name": "Thí nghiệm → mô hình toán", "tags": ["experiment", "application"]},
    {"id": "data_table_analysis", "name": "Bảng dữ liệu → phân tích", "tags": ["table", "statistics"]},
    {"id": "compare_plans", "name": "So sánh phương án", "tags": ["decision", "application"]},
    {"id": "hidden_condition", "name": "Tìm điều kiện ẩn", "tags": ["reasoning", "constraint"]},
    {"id": "error_hunt", "name": "Phát hiện và sửa lỗi", "tags": ["mistake_check", "reasoning"]},
    {"id": "parameter_change", "name": "Thay đổi tham số", "tags": ["parameter", "reasoning"]},
    {"id": "optimization", "name": "Tối ưu hóa", "tags": ["optimization", "real_life"]},
    {"id": "schedule", "name": "Lịch trình và thời gian", "tags": ["time", "application"]},
    {"id": "production", "name": "Sản xuất và năng suất", "tags": ["work", "system"]},
    {"id": "geometry_measurement", "name": "Đo đạc hình học", "tags": ["geometry", "diagram"]},
    {"id": "coordinate_map", "name": "Bản đồ tọa độ", "tags": ["coordinate", "diagram"]},
    {"id": "probability_experiment", "name": "Thí nghiệm xác suất", "tags": ["probability", "experiment"]},
    {"id": "counting_design", "name": "Thiết kế lựa chọn", "tags": ["counting", "combinatorics"]},
    {"id": "sequence_growth", "name": "Tăng trưởng theo dãy", "tags": ["sequence", "real_life"]},
    {"id": "function_model", "name": "Lập mô hình hàm số", "tags": ["function", "real_life"]},
    {"id": "statistics_survey", "name": "Khảo sát thực tế", "tags": ["statistics", "survey"]},
    {"id": "mixed_topics", "name": "Liên kết nhiều kiến thức", "tags": ["mixed", "advanced"]},
]

BY_ID = {item["id"]: item for item in ARCHETYPES}
