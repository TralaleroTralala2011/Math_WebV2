from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from ..auth.routes import get_current_user
from database.database import get_connection


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


# =========================================================
# CONFIG
# =========================================================

MAX_MESSAGE_LENGTH = 1000

DEFAULT_MESSAGE_LIMIT = 200
MAX_MESSAGE_LIMIT = 200

MAX_OFFSET = 1_000_000

MAX_USER_ID = 2_147_483_647
MAX_MESSAGE_ID = 2_147_483_647


# =========================================================
# REQUEST MODEL
# =========================================================

class MessageRequest(BaseModel):

    content: str = Field(
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH
    )


# =========================================================
# AUTH
# =========================================================

def get_user_from_token(
    authorization
):

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Chưa đăng nhập."
        )

    return get_current_user(
        authorization
    )


# =========================================================
# VALIDATE USER ID
# =========================================================

def validate_user_id(
    user_id: int
):

    if isinstance(user_id, bool):

        raise HTTPException(
            status_code=400,
            detail="User ID không hợp lệ."
        )

    if not isinstance(user_id, int):

        raise HTTPException(
            status_code=400,
            detail="User ID không hợp lệ."
        )

    if user_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="User ID không hợp lệ."
        )

    if user_id > MAX_USER_ID:

        raise HTTPException(
            status_code=400,
            detail="User ID không hợp lệ."
        )


# =========================================================
# VALIDATE MESSAGE ID
# =========================================================

def validate_message_id(
    message_id: int
):

    if isinstance(message_id, bool):

        raise HTTPException(
            status_code=400,
            detail="Message ID không hợp lệ."
        )

    if not isinstance(message_id, int):

        raise HTTPException(
            status_code=400,
            detail="Message ID không hợp lệ."
        )

    if message_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Message ID không hợp lệ."
        )

    if message_id > MAX_MESSAGE_ID:

        raise HTTPException(
            status_code=400,
            detail="Message ID không hợp lệ."
        )


# =========================================================
# CHECK FRIENDSHIP
# =========================================================

def check_friendship(
    user_id,
    friend_id
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM friends
            WHERE status = 'accepted'
            AND (
                (
                    requester_id = ?
                    AND receiver_id = ?
                )
                OR
                (
                    requester_id = ?
                    AND receiver_id = ?
                )
            )
            LIMIT 1
            """,
            (
                user_id,
                friend_id,
                friend_id,
                user_id
            )
        )

        row = cursor.fetchone()

        return row is not None

    finally:

        connection.close()


# =========================================================
# CHECK TARGET USER
# =========================================================

def user_exists(
    user_id
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (
                user_id,
            )
        )

        row = cursor.fetchone()

        return row is not None

    finally:

        connection.close()


# =========================================================
# VALIDATE CHAT TARGET
# =========================================================

def validate_chat_target(
    current_user_id,
    friend_id
):

    validate_user_id(
        friend_id
    )

    if (
        current_user_id
        ==
        friend_id
    ):

        raise HTTPException(
            status_code=400,
            detail="Không thể chat với chính mình."
        )

    if not user_exists(
        friend_id
    ):

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    if not check_friendship(
        current_user_id,
        friend_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Hai tài khoản chưa là bạn bè."
        )


# =========================================================
# FORMAT MESSAGE
# =========================================================

def format_message(
    row
):

    return {
        "id": row["id"],
        "sender_id": row["sender_id"],
        "receiver_id": row["receiver_id"],
        "content": row["content"],
        "is_read": bool(row["is_read"]),
        "created_at": row["created_at"],
    }


# =========================================================
# CREATE CHAT NOTIFICATION
# =========================================================

def create_chat_notification(
    user_id,
    content
):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO notifications (
                user_id,
                type,
                content
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                "chat_message",
                content
            )
        )

        connection.commit()

        return True

    except Exception:

        connection.rollback()

        return False

    finally:

        connection.close()


# =========================================================
# GET MESSAGES
# =========================================================

@router.get("/{friend_id}/messages")
def get_messages(
    friend_id: int,
    authorization: str = Header(default=None),
    limit: int = Query(
        default=DEFAULT_MESSAGE_LIMIT,
        ge=1,
        le=MAX_MESSAGE_LIMIT
    ),
    offset: int = Query(
        default=0,
        ge=0,
        le=MAX_OFFSET
    ),
    after_id: int | None = Query(
        default=None,
        ge=1,
        le=MAX_MESSAGE_ID
    )
):

    user = get_user_from_token(
        authorization
    )

    validate_chat_target(
        user["id"],
        friend_id
    )

    if after_id is not None:

        validate_message_id(
            after_id
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # TẢI TIN NHẮN MỚI HƠN after_id
        # -------------------------------------------------

        if after_id is not None:

            cursor.execute(
                """
                SELECT
                    id,
                    sender_id,
                    receiver_id,
                    content,
                    is_read,
                    created_at
                FROM messages
                WHERE
                    id > ?
                    AND
                    (
                        (
                            sender_id = ?
                            AND receiver_id = ?
                        )
                        OR
                        (
                            sender_id = ?
                            AND receiver_id = ?
                        )
                    )
                ORDER BY id ASC
                LIMIT ?
                """,
                (
                    after_id,
                    user["id"],
                    friend_id,
                    friend_id,
                    user["id"],
                    limit
                )
            )

        # -------------------------------------------------
        # TẢI LỊCH SỬ
        # -------------------------------------------------

        else:

            cursor.execute(
                """
                SELECT
                    id,
                    sender_id,
                    receiver_id,
                    content,
                    is_read,
                    created_at
                FROM messages
                WHERE
                    (
                        sender_id = ?
                        AND receiver_id = ?
                    )
                    OR
                    (
                        sender_id = ?
                        AND receiver_id = ?
                    )
                ORDER BY id ASC
                LIMIT ? OFFSET ?
                """,
                (
                    user["id"],
                    friend_id,
                    friend_id,
                    user["id"],
                    limit,
                    offset
                )
            )

        rows = cursor.fetchall()

        return [
            format_message(row)
            for row in rows
        ]

    finally:

        connection.close()


# =========================================================
# SEND MESSAGE
# =========================================================

@router.post("/{friend_id}/messages")
def send_message(
    friend_id: int,
    data: MessageRequest,
    authorization: str = Header(default=None)
):

    user = get_user_from_token(
        authorization
    )

    validate_chat_target(
        user["id"],
        friend_id
    )

    content = data.content.strip()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Tin nhắn không được để trống."
        )

    if len(content) > MAX_MESSAGE_LENGTH:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Tin nhắn tối đa "
                f"{MAX_MESSAGE_LENGTH} ký tự."
            )
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        # -------------------------------------------------
        # INSERT MESSAGE
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO messages (
                sender_id,
                receiver_id,
                content,
                is_read
            )
            VALUES (?, ?, ?, 0)
            """,
            (
                user["id"],
                friend_id,
                content
            )
        )

        message_id = cursor.lastrowid

        if not message_id:

            connection.rollback()

            raise HTTPException(
                status_code=500,
                detail="Không thể tạo tin nhắn."
            )

        # -------------------------------------------------
        # LẤY MESSAGE VỪA TẠO
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                sender_id,
                receiver_id,
                content,
                is_read,
                created_at
            FROM messages
            WHERE id = ?
            LIMIT 1
            """,
            (
                message_id,
            )
        )

        message = cursor.fetchone()

        if not message:

            connection.rollback()

            raise HTTPException(
                status_code=500,
                detail="Không thể đọc tin nhắn vừa tạo."
            )

        connection.commit()

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Không thể gửi tin nhắn."
        )

    finally:

        connection.close()


    # -----------------------------------------------------
    # NOTIFICATION
    # -----------------------------------------------------

    create_chat_notification(
        friend_id,
        (
            f"{user['username']} "
            "đã gửi cho bạn một tin nhắn."
        )
    )


    return format_message(
        message
    )


# =========================================================
# MARK MESSAGES READ
# =========================================================

@router.post("/{friend_id}/read")
def mark_messages_read(
    friend_id: int,
    authorization: str = Header(default=None)
):

    user = get_user_from_token(
        authorization
    )

    validate_chat_target(
        user["id"],
        friend_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE messages
            SET is_read = 1
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND is_read = 0
            """,
            (
                friend_id,
                user["id"]
            )
        )

        changed = cursor.rowcount

        connection.commit()

        return {
            "success": True,
            "message": (
                "Đã đánh dấu tin nhắn đã đọc."
            ),
            "updated": changed,
        }

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Không thể đánh dấu "
                "tin nhắn đã đọc."
            )
        )

    finally:

        connection.close()


# =========================================================
# UNREAD COUNT WITH FRIEND
# =========================================================

@router.get("/{friend_id}/unread-count")
def get_unread_count(
    friend_id: int,
    authorization: str = Header(default=None)
):

    user = get_user_from_token(
        authorization
    )

    validate_chat_target(
        user["id"],
        friend_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM messages
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND is_read = 0
            """,
            (
                friend_id,
                user["id"]
            )
        )

        row = cursor.fetchone()

        return {
            "count": int(
                row["count"]
            )
        }

    finally:

        connection.close()


# =========================================================
# TOTAL UNREAD COUNT
# =========================================================

@router.get("/unread-count")
def get_total_unread_count(
    authorization: str = Header(default=None)
):

    user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM messages
            WHERE
                receiver_id = ?
                AND is_read = 0
            """,
            (
                user["id"],
            )
        )

        row = cursor.fetchone()

        return {
            "count": int(
                row["count"]
            )
        }

    finally:

        connection.close()


# =========================================================
# DELETE OWN MESSAGE
# =========================================================

@router.delete("/message/{message_id}")
def delete_message(
    message_id: int,
    authorization: str = Header(default=None)
):

    user = get_user_from_token(
        authorization
    )

    validate_message_id(
        message_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                sender_id,
                receiver_id
            FROM messages
            WHERE id = ?
            LIMIT 1
            """,
            (
                message_id,
            )
        )

        message = cursor.fetchone()

        if not message:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy tin nhắn."
            )

        # -------------------------------------------------
        # CHỈ NGƯỜI GỬI ĐƯỢC XÓA
        # -------------------------------------------------

        if (
            message["sender_id"]
            !=
            user["id"]
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Bạn chỉ có thể xóa "
                    "tin nhắn của mình."
                )
            )

        cursor.execute(
            """
            DELETE FROM messages
            WHERE
                id = ?
                AND sender_id = ?
            """,
            (
                message_id,
                user["id"]
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=400,
                detail="Không thể xóa tin nhắn."
            )

        connection.commit()

        return {
            "success": True,
            "message": "Đã xóa tin nhắn.",
            "message_id": message_id,
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Không thể xóa tin nhắn."
        )

    finally:

        connection.close()


# =========================================================
# CHAT SUMMARY
# =========================================================

@router.get("/{friend_id}/summary")
def get_chat_summary(
    friend_id: int,
    authorization: str = Header(default=None)
):

    user = get_user_from_token(
        authorization
    )

    validate_chat_target(
        user["id"],
        friend_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # TOTAL MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM messages
            WHERE
                (
                    sender_id = ?
                    AND receiver_id = ?
                )
                OR
                (
                    sender_id = ?
                    AND receiver_id = ?
                )
            """,
            (
                user["id"],
                friend_id,
                friend_id,
                user["id"]
            )
        )

        total_row = cursor.fetchone()

        # -------------------------------------------------
        # UNREAD
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM messages
            WHERE
                sender_id = ?
                AND receiver_id = ?
                AND is_read = 0
            """,
            (
                friend_id,
                user["id"]
            )
        )

        unread_row = cursor.fetchone()

        # -------------------------------------------------
        # LAST MESSAGE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                sender_id,
                receiver_id,
                content,
                is_read,
                created_at
            FROM messages
            WHERE
                (
                    sender_id = ?
                    AND receiver_id = ?
                )
                OR
                (
                    sender_id = ?
                    AND receiver_id = ?
                )
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                user["id"],
                friend_id,
                friend_id,
                user["id"]
            )
        )

        last_message = cursor.fetchone()

        return {
            "total_messages": int(
                total_row["count"]
            ),
            "unread_count": int(
                unread_row["count"]
            ),
            "last_message": (
                format_message(
                    last_message
                )
                if last_message
                else None
            ),
        }

    finally:

        connection.close()