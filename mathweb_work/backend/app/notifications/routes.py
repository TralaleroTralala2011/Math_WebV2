from fastapi import APIRouter, Header, HTTPException

from ..auth.routes import get_current_user
from database.database import get_connection


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


# =========================================================
# CONFIG
# =========================================================

MAX_NOTIFICATIONS = 50


# =========================================================
# AUTH
# =========================================================

def get_user_from_token(
    authorization: str | None
):
    """
    Lấy user hiện tại từ Authorization header.
    """

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Chưa đăng nhập."
        )

    try:

        user = get_current_user(
            authorization
        )

    except HTTPException:

        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không hợp lệ."
        )

    except Exception as error:

        print(
            "NOTIFICATION AUTH ERROR:",
            error
        )

        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không hợp lệ."
        )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Không thể xác định tài khoản."
        )

    # -----------------------------------------------------
    # Không dùng:
    #
    #     if "id" not in user
    #
    # vì sqlite3.Row không nên được kiểm tra theo cách này.
    # -----------------------------------------------------

    try:

        user_id = user["id"]

    except (
        KeyError,
        IndexError,
        TypeError
    ):

        raise HTTPException(
            status_code=401,
            detail="Thông tin tài khoản không hợp lệ."
        )

    if user_id is None:

        raise HTTPException(
            status_code=401,
            detail="Thông tin tài khoản không hợp lệ."
        )

    return user


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_notification_connection():
    """
    Tạo database connection cho Notifications.
    """

    try:

        return get_connection()

    except Exception as error:

        print(
            "NOTIFICATION DATABASE CONNECTION ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể kết nối cơ sở dữ liệu."
        )


# =========================================================
# CREATE NOTIFICATION
# =========================================================

def create_notification(
    user_id,
    notification_type,
    title,
    message,
    related_user_id=None,
    related_id=None
):
    """
    Tạo một notification cho user.

    Hàm này được các module khác gọi khi cần tạo
    thông báo, ví dụ:
    - lời mời kết bạn
    - kết quả game
    - thông báo hệ thống
    - PvP
    """

    if not user_id:

        raise ValueError(
            "user_id không hợp lệ."
        )

    if not notification_type:

        raise ValueError(
            "notification_type không hợp lệ."
        )

    notification_type = str(
        notification_type
    ).strip()

    title = (
        str(title).strip()
        if title is not None
        else ""
    )

    message = (
        str(message).strip()
        if message is not None
        else ""
    )

    if not title and not message:

        raise ValueError(
            "Thông báo phải có nội dung."
        )

    if not message:

        message = title

    if not title:

        title = message

    connection = None

    try:

        connection = get_notification_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO notifications (
                user_id,
                type,
                title,
                message,
                content,
                related_user_id,
                related_id,
                is_read
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                notification_type,
                title,
                message,
                message,
                related_user_id,
                related_id
            )
        )

        connection.commit()

        notification_id = cursor.lastrowid

        return notification_id

    except HTTPException:

        raise

    except Exception as error:

        if connection is not None:

            try:
                connection.rollback()
            except Exception:
                pass

        print(
            "CREATE NOTIFICATION ERROR:",
            error
        )

        raise

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass


# =========================================================
# FORMAT NOTIFICATION
# =========================================================

def format_notification(
    row
):
    """
    Chuẩn hóa database row thành JSON response.
    """

    title = row["title"]

    message = row["message"]

    content = row["content"]

    if not title:

        title = content

    if not message:

        message = content

    if not content:

        content = message

    return {
        "id": row["id"],

        "type": row["type"] or "",

        "title": title or "",

        "message": message or "",

        "content": content or "",

        "related_user_id":
            row["related_user_id"],

        "related_id":
            row["related_id"],

        "is_read": bool(
            row["is_read"]
        ),

        "created_at":
            row["created_at"]
    }


# =========================================================
# GET NOTIFICATIONS
# =========================================================

@router.get("")
def get_notifications(
    authorization: str | None = Header(
        default=None
    )
):

    user = get_user_from_token(
        authorization
    )

    connection = None

    try:

        connection = get_notification_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                type,
                title,
                message,
                content,
                related_user_id,
                related_id,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user["id"],
                MAX_NOTIFICATIONS
            )
        )

        rows = cursor.fetchall()

    except HTTPException:

        raise

    except Exception as error:

        print(
            "GET NOTIFICATIONS ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể tải thông báo."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    notifications = []

    for row in rows:

        notifications.append(
            format_notification(
                row
            )
        )

    return notifications


# =========================================================
# GET UNREAD COUNT
# =========================================================

@router.get("/unread-count")
def get_unread_count(
    authorization: str | None = Header(
        default=None
    )
):

    user = get_user_from_token(
        authorization
    )

    connection = None

    try:

        connection = get_notification_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) AS count
            FROM notifications
            WHERE user_id = ?
            AND is_read = 0
            """,
            (
                user["id"],
            )
        )

        row = cursor.fetchone()

    except HTTPException:

        raise

    except Exception as error:

        print(
            "GET UNREAD COUNT ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể lấy số thông báo chưa đọc."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    count = 0

    if row:

        count = row["count"] or 0

    return {
        "count": count
    }


# =========================================================
# MARK ONE NOTIFICATION AS READ
# =========================================================

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    authorization: str | None = Header(
        default=None
    )
):

    user = get_user_from_token(
        authorization
    )

    if notification_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Notification ID không hợp lệ."
        )

    connection = None

    try:

        connection = get_notification_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE id = ?
            AND user_id = ?
            """,
            (
                notification_id,
                user["id"]
            )
        )

        changed = cursor.rowcount

        if changed == 0:

            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy thông báo."
            )

        connection.commit()

    except HTTPException:

        raise

    except Exception as error:

        if connection is not None:

            try:
                connection.rollback()
            except Exception:
                pass

        print(
            "MARK NOTIFICATION READ ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể cập nhật thông báo."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    return {
        "success": True,
        "message": "Đã đánh dấu thông báo đã đọc."
    }


# =========================================================
# MARK ALL NOTIFICATIONS AS READ
# =========================================================

@router.post("/read-all")
def mark_all_notifications_read(
    authorization: str | None = Header(
        default=None
    )
):

    user = get_user_from_token(
        authorization
    )

    connection = None

    try:

        connection = get_notification_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = ?
            AND is_read = 0
            """,
            (
                user["id"],
            )
        )

        changed = cursor.rowcount

        connection.commit()

    except HTTPException:

        raise

    except Exception as error:

        if connection is not None:

            try:
                connection.rollback()
            except Exception:
                pass

        print(
            "MARK ALL NOTIFICATIONS READ ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể cập nhật thông báo."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    return {
        "success": True,
        "message": "Đã đánh dấu tất cả thông báo đã đọc.",
        "updated": changed
    }