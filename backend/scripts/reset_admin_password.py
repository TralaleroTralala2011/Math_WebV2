"""Reset existing admin credentials on the backend host without embedding secrets in GitHub."""
import os


def main():
    password = os.environ.get('MATHWEB_ADMIN_RESET_PASSWORD', '')
    if not (12 <= len(password) <= 128):
        raise SystemExit('Set MATHWEB_ADMIN_RESET_PASSWORD (12-128 characters) privately on the backend.')

    from database.database import get_connection
    from app.auth.routes import hash_password
    from app.admin_routes import ADMIN_USERNAME, ensure_admin_schema_and_account, now_iso

    ensure_admin_schema_and_account()
    conn = get_connection()
    try:
        row = conn.execute('SELECT id FROM admin_accounts WHERE username=? COLLATE NOCASE', (ADMIN_USERNAME,)).fetchone()
        if row is None:
            raise SystemExit('Admin account missing; check the configured backend database.')
        conn.execute(
            'UPDATE admin_accounts SET password_hash=?, status=?, auth_version=auth_version+1 WHERE id=?',
            (hash_password(password), 'active', row['id']),
        )
        conn.execute(
            'INSERT INTO admin_audit_logs(admin_user_id,action,details,created_at) VALUES(?,?,?,?)',
            (row['id'], 'admin_password_reset', 'operator reset', now_iso()),
        )
        conn.commit()
        print('Admin password reset completed. Previous admin sessions revoked.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
