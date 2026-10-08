from fastapi import APIRouter, Header, HTTPException

from ..auth.routes import get_current_user
from ..presence.routes import is_user_online
from database.database import get_connection


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# =========================================================
# CONFIG
# =========================================================

MAX_LEVEL = 1000

MAX_PLAYER_ID_LENGTH = 100


# =========================================================
# XP CONFIG
# =========================================================

def get_required_xp(
    level
) -> int:
    """
    XP cần để lên level tiếp theo.

    Công thức:
        required_xp = 100 + level * 50

    Ví dụ:
        Level 0 -> 100 XP
        Level 1 -> 150 XP
        Level 2 -> 200 XP
        ...
    """

    try:

        level = int(
            level or 0
        )

    except (
        TypeError,
        ValueError
    ):

        level = 0

    level = max(
        0,
        min(
            level,
            MAX_LEVEL
        )
    )

    return 100 + (
        level * 50
    )


# =========================================================
# NORMALIZE LEVEL
# =========================================================

def normalize_level(
    level
) -> int:
    """
    Chuẩn hóa level về khoảng 0 -> MAX_LEVEL.
    """

    try:

        level = int(
            level or 0
        )

    except (
        TypeError,
        ValueError
    ):

        level = 0

    return max(
        0,
        min(
            level,
            MAX_LEVEL
        )
    )


# =========================================================
# NORMALIZE XP
# =========================================================

def normalize_xp(
    xp
) -> int:
    """
    Chuẩn hóa XP thành số nguyên không âm.
    """

    try:

        xp = int(
            xp or 0
        )

    except (
        TypeError,
        ValueError
    ):

        xp = 0

    return max(
        0,
        xp
    )


# =========================================================
# XP PERCENT
# =========================================================

def calculate_xp_percent(
    xp,
    level
) -> float:
    """
    Tính phần trăm XP hiện tại trong level.
    """

    level = normalize_level(
        level
    )

    xp = normalize_xp(
        xp
    )

    required_xp = get_required_xp(
        level
    )

    if required_xp <= 0:

        return 0.0

    xp_percent = (
        xp
        /
        required_xp
    ) * 100

    xp_percent = max(
        0,
        min(
            xp_percent,
            100
        )
    )

    return round(
        xp_percent,
        2
    )


# =========================================================
# INTEGER STAT
# =========================================================

def normalize_stat(
    value
) -> int:
    """
    Chuẩn hóa statistic thành số nguyên không âm.
    """

    try:

        value = int(
            value or 0
        )

    except (
        TypeError,
        ValueError
    ):

        value = 0

    return max(
        0,
        value
    )


# =========================================================
# USER STATISTICS
# =========================================================

def build_statistics(
    total_games,
    total_correct,
    total_wrong,
    total_blank,
    total_score
):
    """
    Chuẩn hóa và tính toán toàn bộ thống kê người dùng.
    """

    total_games = normalize_stat(
        total_games
    )

    total_correct = normalize_stat(
        total_correct
    )

    total_wrong = normalize_stat(
        total_wrong
    )

    total_blank = normalize_stat(
        total_blank
    )

    total_score = normalize_stat(
        total_score
    )

    total_questions = (
        total_correct
        +
        total_wrong
        +
        total_blank
    )

    accuracy_percent = 0.0

    if total_questions > 0:

        accuracy_percent = (
            total_correct
            /
            total_questions
        ) * 100

    accuracy_percent = max(
        0,
        min(
            accuracy_percent,
            100
        )
    )

    accuracy_percent = round(
        accuracy_percent,
        2
    )

    return {
        "total_games": total_games,

        "completed_games": total_games,

        "total_questions":
            total_questions,

        "total_correct":
            total_correct,

        "total_wrong":
            total_wrong,

        "total_blank":
            total_blank,

        "total_score":
            total_score,

        "accuracy_percent":
            accuracy_percent
    }


# =========================================================
# USER XP DATA
# =========================================================

def build_xp_data(
    level,
    xp
):
    """
    Chuẩn hóa level + XP và tạo dữ liệu XP bar.
    """

    current_level = normalize_level(
        level
    )

    current_xp = normalize_xp(
        xp
    )

    required_xp = get_required_xp(
        current_level
    )

    xp_percent = calculate_xp_percent(
        xp=current_xp,
        level=current_level
    )

    return {
        "level":
            current_level,

        "xp":
            current_xp,

        "required_xp":
            required_xp,

        "xp_percent":
            xp_percent
    }


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

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không hợp lệ."
        )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Không thể xác định tài khoản."
        )

    if "id" not in user:

        raise HTTPException(
            status_code=401,
            detail="Thông tin tài khoản không hợp lệ."
        )

    return user


# =========================================================
# PLAYER ID VALIDATION
# =========================================================

def normalize_player_id(
    player_id
) -> str:
    """
    Chuẩn hóa Player ID.
    """

    player_id = str(
        player_id or ""
    ).strip()

    if not player_id:

        raise HTTPException(
            status_code=400,
            detail="Player ID không được để trống."
        )

    if len(player_id) > MAX_PLAYER_ID_LENGTH:

        raise HTTPException(
            status_code=400,
            detail="Player ID quá dài."
        )

    return player_id


# =========================================================
# GET MY PROFILE
# =========================================================

@router.get("/me")
def get_my_profile(
    authorization: str | None = Header(
        default=None
    )
):

    # =====================================================
    # AUTH
    # =====================================================

    user = get_user_from_token(
        authorization
    )

    # =====================================================
    # XP
    # =====================================================

    xp_data = build_xp_data(
        level=user["level"],
        xp=user["xp"]
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    statistics = build_statistics(
        total_games=user["total_games"],
        total_correct=user["total_correct"],
        total_wrong=user["total_wrong"],
        total_blank=user["total_blank"],
        total_score=user["total_score"]
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "user": {

            "id":
                user["id"],

            "player_id":
                user["player_id"],

            "username":
                user["username"],

            "level":
                xp_data["level"],

            "xp":
                xp_data["xp"],

            "required_xp":
                xp_data["required_xp"],

            "xp_percent":
                xp_data["xp_percent"],

            "total_games":
                statistics["total_games"],

            "completed_games":
                statistics["completed_games"],

            "total_questions":
                statistics["total_questions"],

            "total_correct":
                statistics["total_correct"],

            "total_wrong":
                statistics["total_wrong"],

            "total_blank":
                statistics["total_blank"],

            "total_score":
                statistics["total_score"],

            "accuracy_percent":
                statistics["accuracy_percent"],

            "last_seen":
                user["last_seen"],

            "created_at":
                user["created_at"]
        }
    }


# =========================================================
# GET OTHER USER PROFILE
# =========================================================

@router.get("/profile/{player_id}")
def get_user_profile(
    player_id: str,
    authorization: str | None = Header(
        default=None
    )
):

    # =====================================================
    # AUTH
    # =====================================================

    current_user = get_user_from_token(
        authorization
    )

    # =====================================================
    # VALIDATE PLAYER ID
    # =====================================================

    search_player_id = normalize_player_id(
        player_id
    )

    # =====================================================
    # DON'T VIEW OWN PROFILE
    # =====================================================

    if (
        search_player_id
        ==
        str(
            current_user["player_id"]
        ).strip()
    ):

        raise HTTPException(
            status_code=400,
            detail="Đây là Player ID của bạn."
        )

    # =====================================================
    # DATABASE
    # =====================================================

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                player_id,
                username,
                level,
                xp,
                total_games,
                total_correct,
                total_wrong,
                total_blank,
                total_score,
                last_seen,
                created_at
            FROM users
            WHERE player_id = ?
            """,
            (
                search_player_id,
            )
        )

        user = cursor.fetchone()

    except Exception as error:

        print(
            "GET USER PROFILE ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể tải hồ sơ người chơi."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    # =====================================================
    # NOT FOUND
    # =====================================================

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    # =====================================================
    # XP
    # =====================================================

    xp_data = build_xp_data(
        level=user["level"],
        xp=user["xp"]
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    statistics = build_statistics(
        total_games=user["total_games"],
        total_correct=user["total_correct"],
        total_wrong=user["total_wrong"],
        total_blank=user["total_blank"],
        total_score=user["total_score"]
    )

    # =====================================================
    # ONLINE
    # =====================================================

    online = is_user_online(
        user["last_seen"]
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "user": {

            "id":
                user["id"],

            "player_id":
                user["player_id"],

            "username":
                user["username"],

            "level":
                xp_data["level"],

            "xp":
                xp_data["xp"],

            "required_xp":
                xp_data["required_xp"],

            "xp_percent":
                xp_data["xp_percent"],

            "total_games":
                statistics["total_games"],

            "completed_games":
                statistics["completed_games"],

            "total_questions":
                statistics["total_questions"],

            "total_correct":
                statistics["total_correct"],

            "total_wrong":
                statistics["total_wrong"],

            "total_blank":
                statistics["total_blank"],

            "total_score":
                statistics["total_score"],

            "accuracy_percent":
                statistics["accuracy_percent"],

            "online":
                online,

            "last_seen":
                user["last_seen"],

            "created_at":
                user["created_at"]
        }
    }


# =========================================================
# SEARCH USER
# =========================================================

@router.get("/search")
def search_user(
    player_id: str,
    authorization: str | None = Header(
        default=None
    )
):

    # =====================================================
    # AUTH
    # =====================================================

    current_user = get_user_from_token(
        authorization
    )

    # =====================================================
    # VALIDATE
    # =====================================================

    search_player_id = normalize_player_id(
        player_id
    )

    # =====================================================
    # DON'T SEARCH SELF
    # =====================================================

    if (
        search_player_id
        ==
        str(
            current_user["player_id"]
        ).strip()
    ):

        raise HTTPException(
            status_code=400,
            detail="Bạn không thể tìm chính mình."
        )

    # =====================================================
    # DATABASE
    # =====================================================

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                player_id,
                username,
                level,
                xp,
                last_seen,
                created_at
            FROM users
            WHERE player_id = ?
            """,
            (
                search_player_id,
            )
        )

        user = cursor.fetchone()

    except Exception as error:

        print(
            "SEARCH USER ERROR:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Không thể tìm người chơi."
        )

    finally:

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass

    # =====================================================
    # NOT FOUND
    # =====================================================

    if not user:

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy người chơi."
        )

    # =====================================================
    # XP
    # =====================================================

    xp_data = build_xp_data(
        level=user["level"],
        xp=user["xp"]
    )

    # =====================================================
    # ONLINE
    # =====================================================

    online = is_user_online(
        user["last_seen"]
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "user": {

            "id":
                user["id"],

            "player_id":
                user["player_id"],

            "username":
                user["username"],

            "level":
                xp_data["level"],

            "xp":
                xp_data["xp"],

            "required_xp":
                xp_data["required_xp"],

            "xp_percent":
                xp_data["xp_percent"],

            "online":
                online,

            "last_seen":
                user["last_seen"],

            "created_at":
                user["created_at"]
        }
    }