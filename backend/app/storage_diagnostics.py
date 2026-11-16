"""Honest storage diagnostics: configuration is NOT proof of durability.

This module never deletes, recreates or migrates any user database.
"""
from __future__ import annotations

import os
from pathlib import Path
from database.database import DATABASE_PATH


def get_storage_diagnostics() -> dict:
    render = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID") or os.getenv("RENDER_EXTERNAL_HOSTNAME"))
    account_path = Path(DATABASE_PATH).expanduser().resolve()
    configured_dir = os.getenv("MATHWEB_DATA_DIR", "").strip()
    data_dir = Path(configured_dir).expanduser().resolve() if configured_dir else None
    path_matches = bool(data_dir and (account_path == data_dir or data_dir in account_path.parents))
    concerns = []
    if render and not configured_dir:
        concerns.append("Render thiếu MATHWEB_DATA_DIR: dữ liệu có nguy cơ nằm trên ổ tạm.")
    if render and not path_matches:
        concerns.append("MATHWEB_DB_PATH không nằm trong MATHWEB_DATA_DIR đã cấu hình.")
    if render and configured_dir and str(data_dir).startswith("/opt/render/project"):
        concerns.append("Thư mục dữ liệu nằm trong vùng mã nguồn của Render.")
    if render and configured_dir and str(data_dir).startswith("/tmp"):
        concerns.append("Thư mục dữ liệu nằm trong /tmp.")
    if render and data_dir and not data_dir.exists():
        concerns.append("Thư mục dữ liệu chưa tồn tại.")
    if render and not concerns:
        status = "configured_not_verified"
        message = "Đã cấu hình đường dẫn dữ liệu riêng. Phải xác nhận Render Disk thực sự đã gắn và có sao lưu ngoài máy chủ."
    elif render:
        status = "risk"
        message = "Cấu hình lưu trữ có nguy cơ mất dữ liệu sau lần deploy. Không khôi phục đè khi chưa có sao lưu."
    else:
        status = "local"
        message = "Chạy cục bộ. Cần sao lưu định kỳ nếu sử dụng dữ liệu thật."
    return {
        "status": status,
        "render_detected": render,
        "db_exists": account_path.is_file(),
        "db_path": str(account_path),
        "data_dir": str(data_dir) if data_dir else None,
        "message": message,
        "concerns": concerns,
        "disk_durability_verified": False,
        "scale_ready_for_millions": False,
    }
