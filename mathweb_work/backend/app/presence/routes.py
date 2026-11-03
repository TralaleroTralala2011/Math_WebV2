from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException

from ..auth.routes import get_current_user
from database.database import get_connection


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/presence",
    tags=["Presence"]
)


# =========================================================
# CONFIG
# =========================================================

ONLINE_TIMEOUT_SECONDS = 30


# =========================================================
# AUTH
# =========================================================

def get_user_from_token(
    authorization: str | None
):
    """
    Lấy thông tin người dùng hiện tại từ Authorization header.
    """

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
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
            "PRESENCE AUTH ERROR:",
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
    # vì user có thể là sqlite3.Row.
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
# TIME HELPERS
# =========================================================

def get_current_utc_time() -> datetime:
    """
    Trả về thời gian UTC hiện tại.
    """

    return datetime.now(
        timezone.utc
    )


def get_current_utc_iso() -> str:
    """
    Trả về thời gian UTC dạng ISO 8601.
    """

    return get_current_utc_time().isoformat()


def parse_datetime(
    value
):
    """
    Chuyển chuỗi ISO timestamp thành datetime UTC.

    Hỗ trợ:
    - 2026-09-28T12:00:00+00:00
    - 2026-09-28T12:00:00Z
    - datetime object

    Nếu dữ liệu không hợp lệ thì trả về None.
    """

    if not value:

        return None

    try:

        if isinstance(
            value,
            datetime
        ):

            parsed = value

        else:

            parsed = datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00"
                )
            )

        if parsed.tzinfo is None:

            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        else:

            parsed = parsed.astimezone(
                timezone.utc
            )

        return parsed

    except Exception:

        return None


# =========================================================
# ONLINE CHECK
# =========================================================

def is_user_online(
    last_seen
) -> bool:
    """
    Kiểm tra người dùng có đang online hay không.
    """

    last_time = parse_datetime(
        last_seen
    )

    if last_time is None:

        return False

    try:

        now = get_current_utc_time()

        seconds = (
            now - last_time
        ).total_seconds()

        if seconds < 0:

            return True

        return (
            seconds <= ONLINE_TIMEOUT_SECONDS
        )

    except Exception:

        return False


# =========================================================
# HEARTBEAT
# =========================================================

@router.post("/heartbeat")
def heartbeat(
    authorization: str | None = Header(
        default=None
    )
):
    """
    Cập nhật last_seen của tài khoản hiện tại.
    """

    user = get_user_from_token(
        authorization
    )

    now = get_current_utc_iso()

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET last_seen = ?
            WHERE id = ?
            """,
            (
                now,
                user["id"]
            )
        )

        if cursor.rowcount == 0:

            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy người dùng."
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
            "PRESENCE HEARTBEAT ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể cập nhật trạng thái online."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    return {
        "success": True,
        "online": True,
        "last_seen": now
    }


# =========================================================
# GET USER PRESENCE
# =========================================================

@router.get("/{user_id}")
def get_presence(
    user_id: int,
    authorization: str | None = Header(
        default=None
    )
):
    """
    Lấy trạng thái online của một người dùng.
    """

    get_user_from_token(
        authorization
    )

    if user_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="User ID không hợp lệ."
        )

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                username,
                player_id,
                last_seen
            FROM users
            WHERE id = ?
            """,
            (
                user_id,
            )
        )

        user = cursor.fetchone()

    except Exception as error:

        print(
            "PRESENCE GET ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể lấy trạng thái người dùng."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người dùng."
        )

    last_seen = user["last_seen"]

    online = is_user_online(
        last_seen
    )

    return {
        "user_id": user["id"],
        "player_id": user["player_id"],
        "username": user["username"],
        "online": online,
        "last_seen": last_seen
    }