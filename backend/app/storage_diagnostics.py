"""Honest storage diagnostics: configuration is NOT proof of durability.

This module never deletes, recreates or migrates any user database.
"""
from __future__ import annotations

import os
from pathlib import Path
from database.database import DATABASE_PATH


def get_storage_diagnostics() -> dict:
    from database.persistence_guard import configured_storage, snapshot_status

    safety = configured_storage(DATABASE_PATH)
    rendered = safety['render_detected']
    try:
        statistics = snapshot_status(DATABASE_PATH)
    except (OSError, RuntimeError) as exc:
        statistics = {'snapshot_status_error': str(exc)}

    if rendered and not safety['safe']:
        status = 'risk'
        message = ('NGUY HIỂM: Backend không được phép tạo tài khoản trên ổ tạm Render. '
                   'Cần Render Disk thực sự được mount trước khi hoạt động.')
    elif rendered:
        status = 'mounted_disk_detected'
        message = ('Đã xác nhận thư mục dữ liệu nằm trên một điểm mount riêng. '
                   'Vẫn cần bản sao lưu mã hóa lưu NGOÀI Render Disk để chống mất toàn bộ ổ.')
    else:
        status = 'local'
        message = ('Chạy cục bộ. Cần sao lưu riêng file database; nâng cấp ZIP không được chứa '
                   'hoặc ghi đè tài khoản người dùng.')

    return {
        'status': status,
        'render_detected': rendered,
        'db_exists': Path(DATABASE_PATH).is_file(),
        'db_path': str(Path(DATABASE_PATH).resolve()),
        'data_dir': safety['data_dir'],
        'message': message,
        'concerns': safety['concerns'],
        'disk_mount_verified': safety['mount_verified'],
        'disk_durability_verified': bool(rendered and safety['safe']),
        'external_backup_verified': False,
        'scale_ready_for_millions': False,
        **statistics,
    }
