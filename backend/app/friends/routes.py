from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from ..auth.routes import get_current_user
from ..presence.routes import is_user_online
from database.database import get_connection


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/friends",
    tags=["Friends"]
)


# =========================================================
# CONFIG
# =========================================================

MAX_PLAYER_ID_LENGTH = 100
MAX_REQUEST_ID = 2_147_483_647


# =========================================================
# REQUEST MODEL
# =========================================================

class FriendRequest(BaseModel):

    player_id: str


# =========================================================
# AUTH
# =========================================================

def get_user_from_token(
    authorization
):

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
        )

    return get_current_user(
        authorization
    )


# =========================================================
# VALIDATE PLAYER ID
# =========================================================

def normalize_player_id(
    player_id: str
) -> str:

    if not isinstance(player_id, str):

        raise HTTPException(
            status_code=400,
            detail="Player ID không hợp lệ."
        )

    player_id = player_id.strip()

    if not player_id:

        raise HTTPException(
            status_code=400,
            detail="Player ID không được để trống."
        )

    if len(player_id) > MAX_PLAYER_ID_LENGTH:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Player ID không được vượt quá "
                f"{MAX_PLAYER_ID_LENGTH} ký tự."
            )
        )

    return player_id


# =========================================================
# VALIDATE REQUEST ID
# =========================================================

def validate_request_id(
    request_id: int
):

    if isinstance(request_id, bool):

        raise HTTPException(
            status_code=400,
            detail="Request ID không hợp lệ."
        )

    if request_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Request ID không hợp lệ."
        )

    if request_id > MAX_REQUEST_ID:

        raise HTTPException(
            status_code=400,
            detail="Request ID không hợp lệ."
        )


# =========================================================
# FIND USER BY PLAYER ID
# =========================================================

def find_user_by_player_id(
    cursor,
    player_id: str
):

    cursor.execute(
        """
        SELECT
            id,
            username,
            player_id,
            level,
            last_seen
        FROM users
        WHERE player_id = ?
        LIMIT 1
        """,
        (
            player_id,
        )
    )

    return cursor.fetchone()


# =========================================================
# GET RELATION
# =========================================================

def get_friend_relation(
    cursor,
    user_id: int,
    target_user_id: int
):

    cursor.execute(
        """
        SELECT
            id,
            requester_id,
            receiver_id,
            status
        FROM friends
        WHERE
            (
                requester_id = ?
                AND receiver_id = ?
            )
            OR
            (
                requester_id = ?
                AND receiver_id = ?
            )
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            user_id,
            target_user_id,
            target_user_id,
            user_id
        )
    )

    return cursor.fetchone()


# =========================================================
# FORMAT USER
# =========================================================

def format_user(
    user,
    online: bool = False
):

    return {
        "id": user["id"],
        "username": user["username"],
        "player_id": user["player_id"],
        "level": user["level"],
        "online": online,
    }


# =========================================================
# SEARCH USER
# =========================================================

@router.get("/search")
def search_user(
    player_id: str,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    player_id = normalize_player_id(
        player_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        user = find_user_by_player_id(
            cursor,
            player_id
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy người chơi."
            )

        if user["id"] == current_user["id"]:

            raise HTTPException(
                status_code=400,
                detail="Bạn không thể kết bạn với chính mình."
            )

        relation = get_friend_relation(
            cursor,
            current_user["id"],
            user["id"]
        )

        friend_status = None

        if relation:

            friend_status = relation["status"]

        is_friend = (
            friend_status == "accepted"
        )

        online = is_user_online(
            user["last_seen"]
        )

        return {
            "id": user["id"],
            "player_id": user["player_id"],
            "username": user["username"],
            "level": user["level"],
            "online": online,
            "is_friend": is_friend,
            "friend_status": friend_status,
            "relation_id": (
                relation["id"]
                if relation
                else None
            ),
            "requester_id": (
                relation["requester_id"]
                if relation
                else None
            ),
            "receiver_id": (
                relation["receiver_id"]
                if relation
                else None
            ),
        }

    finally:

        connection.close()


# =========================================================
# GET FRIEND STATUS
# =========================================================

@router.get("/status/{player_id}")
def get_friend_status(
    player_id: str,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    player_id = normalize_player_id(
        player_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        user = find_user_by_player_id(
            cursor,
            player_id
        )

        if not user:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy người chơi."
            )

        if user["id"] == current_user["id"]:

            return {
                "player_id": player_id,
                "status": "self",
                "is_friend": False,
                "is_self": True,
            }

        relation = get_friend_relation(
            cursor,
            current_user["id"],
            user["id"]
        )

        if not relation:

            return {
                "player_id": player_id,
                "status": None,
                "is_friend": False,
                "is_self": False,
                "relation_id": None,
            }

        return {
            "player_id": player_id,
            "status": relation["status"],
            "is_friend": (
                relation["status"]
                == "accepted"
            ),
            "is_self": False,
            "relation_id": relation["id"],
            "requester_id": relation[
                "requester_id"
            ],
            "receiver_id": relation[
                "receiver_id"
            ],
        }

    finally:

        connection.close()


# =========================================================
# SEND FRIEND REQUEST
# =========================================================

@router.post("/request")
def send_friend_request(
    data: FriendRequest,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    target_player_id = normalize_player_id(
        data.player_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # KHÓA TRANSACTION
        # -------------------------------------------------

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        # -------------------------------------------------
        # TÌM NGƯỜI NHẬN
        # -------------------------------------------------

        receiver = find_user_by_player_id(
            cursor,
            target_player_id
        )

        if not receiver:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy người chơi."
            )

        # -------------------------------------------------
        # KHÔNG TỰ KẾT BẠN
        # -------------------------------------------------

        if (
            receiver["id"]
            ==
            current_user["id"]
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Bạn không thể gửi lời mời "
                    "cho chính mình."
                )
            )

        # -------------------------------------------------
        # KIỂM TRA QUAN HỆ
        # -------------------------------------------------

        existing = get_friend_relation(
            cursor,
            current_user["id"],
            receiver["id"]
        )

        if existing:

            status = existing["status"]

            if status == "accepted":

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Hai bạn đã là bạn bè."
                    )
                )

            if status == "pending":

                if (
                    existing["requester_id"]
                    ==
                    current_user["id"]
                ):

                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Bạn đã gửi lời mời "
                            "trước đó."
                        )
                    )

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Người này đã gửi lời mời "
                        "cho bạn."
                    )
                )

        # -------------------------------------------------
        # TẠO LỜI MỜI
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO friends (
                requester_id,
                receiver_id,
                status
            )
            VALUES (?, ?, 'pending')
            """,
            (
                current_user["id"],
                receiver["id"]
            )
        )

        request_id = cursor.lastrowid

        # -------------------------------------------------
        # THÔNG BÁO
        # -------------------------------------------------

        message = (
            current_user["username"]
            +
            " đã gửi lời mời kết bạn cho bạn."
        )

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
                receiver["id"],
                "friend_request",
                "Lời mời kết bạn",
                message,
                message,
                current_user["id"],
                request_id
            )
        )

        connection.commit()

        return {
            "success": True,
            "message": "Đã gửi lời mời kết bạn.",
            "player_id": receiver["player_id"],
            "request_id": request_id,
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Không thể gửi lời mời kết bạn."
            )
        )

    finally:

        connection.close()


# =========================================================
# GET INCOMING FRIEND REQUESTS
# =========================================================

@router.get("/requests")
def get_friend_requests(
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                friends.id,
                users.id AS user_id,
                users.username,
                users.player_id,
                users.level,
                users.last_seen
            FROM friends
            JOIN users
                ON users.id =
                   friends.requester_id
            WHERE
                friends.receiver_id = ?
                AND friends.status = 'pending'
            ORDER BY friends.id DESC
            """,
            (
                current_user["id"],
            )
        )

        requests = cursor.fetchall()

        result = []

        for request in requests:

            result.append({
                "id": request["id"],
                "user_id": request["user_id"],
                "username": request["username"],
                "player_id": request["player_id"],
                "level": request["level"],
                "online": is_user_online(
                    request["last_seen"]
                ),
            })

        return result

    finally:

        connection.close()


# =========================================================
# GET OUTGOING FRIEND REQUESTS
# =========================================================

@router.get("/requests/sent")
def get_sent_friend_requests(
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                friends.id,
                users.id AS user_id,
                users.username,
                users.player_id,
                users.level,
                users.last_seen
            FROM friends
            JOIN users
                ON users.id =
                   friends.receiver_id
            WHERE
                friends.requester_id = ?
                AND friends.status = 'pending'
            ORDER BY friends.id DESC
            """,
            (
                current_user["id"],
            )
        )

        requests = cursor.fetchall()

        result = []

        for request in requests:

            result.append({
                "id": request["id"],
                "user_id": request["user_id"],
                "username": request["username"],
                "player_id": request["player_id"],
                "level": request["level"],
                "online": is_user_online(
                    request["last_seen"]
                ),
            })

        return result

    finally:

        connection.close()


# =========================================================
# ACCEPT FRIEND REQUEST
# =========================================================

@router.post("/accept/{request_id}")
def accept_friend(
    request_id: int,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    validate_request_id(
        request_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        # -------------------------------------------------
        # TÌM LỜI MỜI
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                requester_id,
                receiver_id,
                status
            FROM friends
            WHERE id = ?
            LIMIT 1
            """,
            (
                request_id,
            )
        )

        request = cursor.fetchone()

        if not request:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lời mời."
            )

        # -------------------------------------------------
        # KIỂM TRA QUYỀN
        # -------------------------------------------------

        if (
            request["receiver_id"]
            !=
            current_user["id"]
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Bạn không có quyền xử lý "
                    "lời mời này."
                )
            )

        if request["status"] != "pending":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Lời mời này không còn "
                    "hiệu lực."
                )
            )

        # -------------------------------------------------
        # ACCEPT
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE friends
            SET status = 'accepted'
            WHERE
                id = ?
                AND receiver_id = ?
                AND status = 'pending'
            """,
            (
                request_id,
                current_user["id"]
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Lời mời này không còn "
                    "hiệu lực."
                )
            )

        # -------------------------------------------------
        # THÔNG BÁO NGƯỜI GỬI
        # -------------------------------------------------

        message = (
            current_user["username"]
            +
            " đã chấp nhận lời mời kết bạn."
        )

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
                request["requester_id"],
                "friend_accepted",
                "Đã chấp nhận lời mời",
                message,
                message,
                current_user["id"],
                request_id
            )
        )

        connection.commit()

        return {
            "success": True,
            "message": "Đã chấp nhận lời mời.",
            "request_id": request_id,
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Không thể chấp nhận lời mời."
            )
        )

    finally:

        connection.close()


# =========================================================
# REJECT FRIEND REQUEST
# =========================================================

@router.post("/reject/{request_id}")
def reject_friend(
    request_id: int,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    validate_request_id(
        request_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT
                id,
                requester_id,
                receiver_id,
                status
            FROM friends
            WHERE id = ?
            LIMIT 1
            """,
            (
                request_id,
            )
        )

        request = cursor.fetchone()

        if not request:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lời mời."
            )

        if (
            request["receiver_id"]
            !=
            current_user["id"]
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Bạn không có quyền xử lý "
                    "lời mời này."
                )
            )

        if request["status"] != "pending":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Lời mời này không còn "
                    "hiệu lực."
                )
            )

        # -------------------------------------------------
        # XÓA LỜI MỜI
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM friends
            WHERE
                id = ?
                AND receiver_id = ?
                AND status = 'pending'
            """,
            (
                request_id,
                current_user["id"]
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Lời mời này không còn "
                    "hiệu lực."
                )
            )

        connection.commit()

        return {
            "success": True,
            "message": "Đã từ chối lời mời.",
            "request_id": request_id,
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Không thể từ chối lời mời."
            )
        )

    finally:

        connection.close()


# =========================================================
# CANCEL SENT FRIEND REQUEST
# =========================================================

@router.post("/cancel/{request_id}")
def cancel_friend_request(
    request_id: int,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    validate_request_id(
        request_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT
                id,
                requester_id,
                receiver_id,
                status
            FROM friends
            WHERE id = ?
            LIMIT 1
            """,
            (
                request_id,
            )
        )

        request = cursor.fetchone()

        if not request:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lời mời."
            )

        if (
            request["requester_id"]
            !=
            current_user["id"]
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Bạn không có quyền hủy "
                    "lời mời này."
                )
            )

        if request["status"] != "pending":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Lời mời này không còn "
                    "hiệu lực."
                )
            )

        cursor.execute(
            """
            DELETE FROM friends
            WHERE
                id = ?
                AND requester_id = ?
                AND status = 'pending'
            """,
            (
                request_id,
                current_user["id"]
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Lời mời này không còn "
                    "hiệu lực."
                )
            )

        connection.commit()

        return {
            "success": True,
            "message": "Đã hủy lời mời kết bạn.",
            "request_id": request_id,
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Không thể hủy lời mời kết bạn."
            )
        )

    finally:

        connection.close()


# =========================================================
# GET FRIEND LIST
# =========================================================

@router.get("")
def get_friends(
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                users.id,
                users.username,
                users.player_id,
                users.level,
                users.last_seen
            FROM friends
            JOIN users
                ON users.id =
                    CASE
                        WHEN friends.requester_id = ?
                        THEN friends.receiver_id
                        ELSE friends.requester_id
                    END
            WHERE
                (
                    friends.requester_id = ?
                    OR
                    friends.receiver_id = ?
                )
                AND friends.status = 'accepted'
            ORDER BY
                CASE
                    WHEN users.last_seen IS NOT NULL
                         THEN 0
                    ELSE 1
                END,
                users.username ASC
            """,
            (
                current_user["id"],
                current_user["id"],
                current_user["id"]
            )
        )

        friends = cursor.fetchall()

        result = []

        for friend in friends:

            online = is_user_online(
                friend["last_seen"]
            )

            result.append({
                "id": friend["id"],
                "username": friend["username"],
                "player_id": friend["player_id"],
                "level": friend["level"],
                "online": online,
            })

        return result

    finally:

        connection.close()


# =========================================================
# REMOVE FRIEND
# =========================================================

@router.delete("/{player_id}")
def remove_friend(
    player_id: str,
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    player_id = normalize_player_id(
        player_id
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        # -------------------------------------------------
        # TÌM USER
        # -------------------------------------------------

        target_user = find_user_by_player_id(
            cursor,
            player_id
        )

        if not target_user:

            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy người chơi."
            )

        if (
            target_user["id"]
            ==
            current_user["id"]
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Bạn không thể xóa chính mình "
                    "khỏi danh sách bạn bè."
                )
            )

        # -------------------------------------------------
        # TÌM QUAN HỆ
        # -------------------------------------------------

        relation = get_friend_relation(
            cursor,
            current_user["id"],
            target_user["id"]
        )

        if not relation:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Hai bạn không phải là "
                    "bạn bè."
                )
            )

        if relation["status"] != "accepted":

            raise HTTPException(
                status_code=400,
                detail=(
                    "Quan hệ hiện tại không phải "
                    "là bạn bè."
                )
            )

        # -------------------------------------------------
        # XÓA QUAN HỆ
        # -------------------------------------------------

        cursor.execute(
            """
            DELETE FROM friends
            WHERE id = ?
            """,
            (
                relation["id"],
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Không thể xóa quan hệ "
                    "bạn bè."
                )
            )

        connection.commit()

        return {
            "success": True,
            "message": "Đã xóa bạn bè.",
            "player_id": target_user[
                "player_id"
            ],
        }

    except HTTPException:

        connection.rollback()

        raise

    except Exception:

        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Không thể xóa bạn bè."
        )

    finally:

        connection.close()


# =========================================================
# FRIEND COUNTS
# =========================================================

@router.get("/counts")
def get_friend_counts(
    authorization: str = Header(default=None)
):

    current_user = get_user_from_token(
        authorization
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # FRIEND COUNT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM friends
            WHERE
                (
                    requester_id = ?
                    OR receiver_id = ?
                )
                AND status = 'accepted'
            """,
            (
                current_user["id"],
                current_user["id"]
            )
        )

        friend_count = cursor.fetchone()

        # -------------------------------------------------
        # INCOMING REQUEST COUNT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM friends
            WHERE
                receiver_id = ?
                AND status = 'pending'
            """,
            (
                current_user["id"],
            )
        )

        incoming_count = cursor.fetchone()

        # -------------------------------------------------
        # OUTGOING REQUEST COUNT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM friends
            WHERE
                requester_id = ?
                AND status = 'pending'
            """,
            (
                current_user["id"],
            )
        )

        outgoing_count = cursor.fetchone()

        return {
            "friends": (
                int(friend_count["total"])
            ),
            "incoming_requests": (
                int(incoming_count["total"])
            ),
            "outgoing_requests": (
                int(outgoing_count["total"])
            ),
        }

    finally:

        connection.close()