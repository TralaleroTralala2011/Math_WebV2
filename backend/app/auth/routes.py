import base64
import hashlib
import hmac
import json
import os
import secrets

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from database.database import get_connection


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# =========================================================
# CONFIG
# =========================================================

# Có thể đặt MATH_WEB_SECRET_KEY trong biến môi trường khi deploy.
# Nếu chưa đặt thì dùng key local để giữ khả năng chạy ngay trên máy.
SECRET_KEY = os.getenv(
    "MATH_WEB_SECRET_KEY",
    "MATH_WEB_LOCAL_SECRET"
)

TOKEN_EXPIRE_DAYS = 7

PASSWORD_HASH_ALGORITHM = "sha256"
PASSWORD_ITERATIONS = 100_000
PASSWORD_SALT_BYTES = 16

MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 20

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128

MIN_PLAYER_ID_LENGTH = 10
MAX_PLAYER_ID_LENGTH = 30

MAX_TOKEN_LENGTH = 4096


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=100
    )

    password: str = Field(
        min_length=1,
        max_length=256
    )


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=100
    )

    password: str = Field(
        min_length=1,
        max_length=256
    )


# =========================================================
# TIME
# =========================================================

def utc_now():
    """
    Trả về thời gian UTC dạng timezone-aware.
    """
    return datetime.now(timezone.utc)


def utc_now_iso():
    """
    Trả về UTC ISO string không kèm microseconds.
    """
    return utc_now().replace(
        microsecond=0
    ).isoformat()


def utc_timestamp():
    """
    Unix timestamp UTC.
    """
    return utc_now().timestamp()


# =========================================================
# PASSWORD
# =========================================================

def hash_password(password: str) -> str:
    """
    Hash password bằng PBKDF2-HMAC-SHA256.

    Format:
        base64(salt):base64(hash)
    """

    if not isinstance(password, str):
        raise ValueError(
            "Mật khẩu không hợp lệ."
        )

    salt = secrets.token_bytes(
        PASSWORD_SALT_BYTES
    )

    password_hash = hashlib.pbkdf2_hmac(
        PASSWORD_HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS
    )

    salt_text = base64.b64encode(
        salt
    ).decode("ascii")

    hash_text = base64.b64encode(
        password_hash
    ).decode("ascii")

    return f"{salt_text}:{hash_text}"


def verify_password(
    password: str,
    stored_password: str
) -> bool:
    """
    Kiểm tra password với password hash đã lưu.
    """

    if not isinstance(password, str):
        return False

    if not isinstance(stored_password, str):
        return False

    try:
        parts = stored_password.split(":")

        if len(parts) != 2:
            return False

        salt_text = parts[0]
        hash_text = parts[1]

        if not salt_text or not hash_text:
            return False

        salt = base64.b64decode(
            salt_text,
            validate=True
        )

        stored_hash = base64.b64decode(
            hash_text,
            validate=True
        )

        if len(salt) != PASSWORD_SALT_BYTES:
            return False

        if not stored_hash:
            return False

        password_hash = hashlib.pbkdf2_hmac(
            PASSWORD_HASH_ALGORITHM,
            password.encode("utf-8"),
            salt,
            PASSWORD_ITERATIONS
        )

        return hmac.compare_digest(
            password_hash,
            stored_hash
        )

    except Exception:
        return False


# =========================================================
# USERNAME VALIDATION
# =========================================================

def normalize_username(username: str) -> str:
    """
    Chuẩn hóa username.

    Không chuyển thành lowercase vì username hiện tại
    được lưu theo đúng giá trị người dùng đăng ký.
    """

    if not isinstance(username, str):
        raise HTTPException(
            status_code=400,
            detail="Tên tài khoản không hợp lệ."
        )

    username = username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Tên tài khoản không được để trống."
        )

    if len(username) < MIN_USERNAME_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tên tài khoản phải có ít nhất "
                f"{MIN_USERNAME_LENGTH} ký tự."
            )
        )

    if len(username) > MAX_USERNAME_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Tên tài khoản tối đa "
                f"{MAX_USERNAME_LENGTH} ký tự."
            )
        )

    # Không cho phép ký tự điều khiển.
    if any(
        ord(character) < 32
        for character in username
    ):
        raise HTTPException(
            status_code=400,
            detail="Tên tài khoản chứa ký tự không hợp lệ."
        )

    if any(
        ord(character) == 127
        for character in username
    ):
        raise HTTPException(
            status_code=400,
            detail="Tên tài khoản chứa ký tự không hợp lệ."
        )

    return username


# =========================================================
# PASSWORD VALIDATION
# =========================================================

def validate_password(password: str):
    """
    Kiểm tra password trước khi hash.
    """

    if not isinstance(password, str):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu không hợp lệ."
        )

    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Mật khẩu phải có ít nhất "
                f"{MIN_PASSWORD_LENGTH} ký tự."
            )
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Mật khẩu tối đa "
                f"{MAX_PASSWORD_LENGTH} ký tự."
            )
        )

    if any(
        ord(character) < 32
        for character in password
    ):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu chứa ký tự không hợp lệ."
        )


# =========================================================
# PLAYER ID
# =========================================================

def generate_player_id() -> str:
    """
    Sinh Player ID.

    Format:
        MW-123456-789
    """

    first = secrets.randbelow(
        900000
    ) + 100000

    second = secrets.randbelow(
        900
    ) + 100

    return f"MW-{first}-{second}"


def create_player_id(
    connection=None
) -> str:
    """
    Tạo Player ID chưa tồn tại.

    Nếu truyền connection vào thì dùng connection đó.
    Điều này giúp register kiểm tra ID trong cùng transaction.
    """

    owns_connection = False

    if connection is None:
        connection = get_connection()
        owns_connection = True

    try:
        cursor = connection.cursor()

        # Số lượng không gian ID rất lớn, nhưng vẫn giới hạn
        # số lần thử để tránh vòng lặp vô hạn trong trường hợp
        # database có vấn đề.
        for _ in range(100):

            player_id = generate_player_id()

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE player_id = ?
                LIMIT 1
                """,
                (player_id,)
            )

            if cursor.fetchone() is None:
                return player_id

        raise HTTPException(
            status_code=500,
            detail="Không thể tạo Player ID."
        )

    finally:
        if owns_connection:
            connection.close()


# =========================================================
# TOKEN
# =========================================================

def create_token(
    user_id: int,
    player_id: str
) -> str:
    """
    Tạo token HMAC.

    Token format:

        base64url(payload).signature

    Payload gồm:
        user_id
        player_id
        iat
        expires
    """

    if not isinstance(user_id, int):
        raise ValueError(
            "user_id không hợp lệ."
        )

    if user_id <= 0:
        raise ValueError(
            "user_id không hợp lệ."
        )

    if not isinstance(player_id, str):
        raise ValueError(
            "player_id không hợp lệ."
        )

    now = utc_timestamp()
    auth_version = 0
    connection = get_connection()
    try:
        version_row = connection.execute("SELECT auth_version FROM users WHERE id=?", (user_id,)).fetchone()
        if version_row:
            auth_version = int(version_row["auth_version"] or 0)
    finally:
        connection.close()

    payload = {
        "user_id": user_id,
        "player_id": player_id,
        "auth_version": auth_version,
        "iat": now,
        "expires": (
            now
            + timedelta(
                days=TOKEN_EXPIRE_DAYS
            ).total_seconds()
        )
    }

    data = json.dumps(
        payload,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    encoded = base64.urlsafe_b64encode(
        data
    ).decode("ascii").rstrip("=")

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        encoded.encode("ascii"),
        hashlib.sha256
    ).hexdigest()

    token = f"{encoded}.{signature}"

    if len(token) > MAX_TOKEN_LENGTH:
        raise ValueError(
            "Token quá dài."
        )

    return token


def create_admin_token(admin_id: int, username: str, auth_version: int = 0) -> str:
    """Create a signed token for the separate admin_accounts identity store."""
    now = utc_timestamp()
    payload = {
        "user_id": int(admin_id),
        "player_id": f"MWADMIN{int(admin_id)}",
        "auth_version": int(auth_version or 0),
        "role": "admin",
        "admin_username": username,
        "iat": now,
        "expires": now + timedelta(days=TOKEN_EXPIRE_DAYS).total_seconds(),
    }
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    encoded = base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).hexdigest()
    token = f"{encoded}.{signature}"
    if len(token) > MAX_TOKEN_LENGTH:
        raise ValueError("Token quá dài.")
    return token


def verify_token(token: str):
    """
    Kiểm tra:

    - token tồn tại
    - đúng format
    - chữ ký đúng
    - payload hợp lệ
    - user_id hợp lệ
    - player_id hợp lệ
    - thời gian tạo hợp lệ
    - token chưa hết hạn
    """

    if not isinstance(token, str):
        return None

    token = token.strip()

    if not token:
        return None

    if len(token) > MAX_TOKEN_LENGTH:
        return None

    try:
        parts = token.split(".")

        if len(parts) != 2:
            return None

        encoded = parts[0]
        signature = parts[1]

        if not encoded or not signature:
            return None

        # SHA-256 hex digest có đúng 64 ký tự.
        if len(signature) != 64:
            return None

        try:
            int(signature, 16)
        except ValueError:
            return None

        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            encoded.encode("ascii"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            signature,
            expected_signature
        ):
            return None

        padding = "=" * (
            -len(encoded) % 4
        )

        decoded_data = base64.urlsafe_b64decode(
            (
                encoded + padding
            ).encode("ascii")
        )

        payload = json.loads(
            decoded_data.decode("utf-8")
        )

        if not isinstance(payload, dict):
            return None

        user_id = payload.get("user_id")
        player_id = payload.get("player_id")
        issued_at = payload.get("iat")
        expires = payload.get("expires")
        auth_version = payload.get("auth_version", 0)

        if not isinstance(auth_version, int) or isinstance(auth_version, bool) or auth_version < 0:
            return None

        if not isinstance(user_id, int):
            return None

        if isinstance(user_id, bool):
            return None

        if user_id <= 0:
            return None

        if not isinstance(player_id, str):
            return None

        player_id = player_id.strip()

        if not player_id:
            return None

        if len(player_id) > MAX_PLAYER_ID_LENGTH:
            return None

        if not isinstance(issued_at, (int, float)):
            return None

        if isinstance(issued_at, bool):
            return None

        if not isinstance(expires, (int, float)):
            return None

        if isinstance(expires, bool):
            return None

        current_time = utc_timestamp()

        # Token chưa được tạo trong tương lai.
        # Cho phép sai lệch đồng hồ nhỏ 30 giây.
        if issued_at > current_time + 30:
            return None

        # Token phải có thời điểm hết hạn sau thời điểm tạo.
        if expires <= issued_at:
            return None

        # Token đã hết hạn.
        if expires <= current_time:
            return None

        return {
            "user_id": user_id,
            "player_id": player_id,
            "auth_version": auth_version,
            "role": payload.get("role", "user"),
            "admin_username": payload.get("admin_username"),
            "iat": issued_at,
            "expires": expires
        }

    except Exception:
        return None


# =========================================================
# AUTHORIZATION
# =========================================================

def extract_bearer_token(
    authorization: str | None
) -> str:
    """
    Lấy token từ:

        Authorization: Bearer <token>
    """

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bạn chưa đăng nhập."
        )

    if not isinstance(authorization, str):
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ."
        )

    scheme, separator, token = (
        authorization.partition(" ")
    )

    if (
        not separator
        or scheme.lower() != "bearer"
    ):
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ."
        )

    token = token.strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ."
        )

    if len(token) > MAX_TOKEN_LENGTH:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ."
        )

    return token


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    authorization: str | None
):
    """
    Xác thực Bearer token và lấy user hiện tại.

    Đây là helper dùng chung cho các route khác.
    """

    token = extract_bearer_token(
        authorization
    )

    payload = verify_token(
        token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập đã hết hạn hoặc không hợp lệ."
        )

    if payload.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Phiên quản trị không được dùng cho API tài khoản người học.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                player_id,
                username,
                password_hash,
                level,
                xp,
                total_games,
                total_correct,
                total_wrong,
                total_blank,
                total_score,
                last_seen,
                created_at,
                role,
                status,
                ban_reason,
                auth_version
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (payload["user_id"],)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Tài khoản không còn tồn tại."
            )

        # Không tin player_id từ token một cách tuyệt đối.
        # Đối chiếu lại với database.
        if user["player_id"] != payload["player_id"]:
            raise HTTPException(
                status_code=401,
                detail="Token không hợp lệ."
            )

        if int(payload.get("auth_version", 0)) != int(user["auth_version"] or 0):
            raise HTTPException(
                status_code=401,
                detail="Phiên đăng nhập đã bị thu hồi. Vui lòng đăng nhập lại."
            )

        if user["status"] == "banned":
            raise HTTPException(
                status_code=403,
                detail=("Tài khoản đã bị tạm khóa. Lý do: " + (user["ban_reason"] or "Liên hệ quản trị viên."))
            )

        now = utc_now_iso()

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

        connection.commit()

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
                created_at,
                role,
                status
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user["id"],)
        )

        updated_user = cursor.fetchone()

        if not updated_user:
            raise HTTPException(
                status_code=401,
                detail="Không thể đọc thông tin tài khoản."
            )

        return updated_user

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Không thể xác thực tài khoản."
        )

    finally:
        connection.close()


# =========================================================
# USER RESPONSE
# =========================================================

def serialize_user(user):
    """
    Chuyển database row thành dữ liệu an toàn cho API.

    Tuyệt đối không trả password_hash.
    """

    return {
        "id": user["id"],
        "player_id": user["player_id"],
        "username": user["username"],
        "level": user["level"] or 0,
        "xp": user["xp"] or 0,
        "total_games": user["total_games"] or 0,
        "total_correct": user["total_correct"] or 0,
        "total_wrong": user["total_wrong"] or 0,
        "total_blank": user["total_blank"] or 0,
        "total_score": user["total_score"] or 0,
        "last_seen": user["last_seen"],
        "created_at": user["created_at"],
        "role": user["role"] if "role" in user.keys() else "user",
        "status": user["status"] if "status" in user.keys() else "active"
    }


def serialize_login_user(user):
    """
    Dữ liệu user trả về khi login/register.
    """

    return {
        "id": user["id"],
        "player_id": user["player_id"],
        "username": user["username"],
        "level": user["level"] or 0,
        "xp": user["xp"] or 0,
        "total_games": user["total_games"] or 0,
        "total_correct": user["total_correct"] or 0,
        "total_wrong": user["total_wrong"] or 0,
        "total_blank": user["total_blank"] or 0,
        "total_score": user["total_score"] or 0,
        "role": user["role"] if "role" in user.keys() else "user",
        "status": user["status"] if "status" in user.keys() else "active"
    }


# =========================================================
# REGISTER
# =========================================================

@router.post("/register")
def register(
    data: RegisterRequest
):
    """
    Tạo tài khoản mới.
    """

    username = normalize_username(
        data.username
    )

    password = data.password

    if username.casefold() == "admin19022011":
        raise HTTPException(status_code=400, detail="Tên tài khoản này được dành riêng cho hệ thống quản trị.")

    validate_password(
        password
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Khóa transaction để giảm khả năng race condition
        # khi nhiều request đăng ký cùng lúc.
        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            LIMIT 1
            """,
            (username,)
        )

        if cursor.fetchone():
            connection.rollback()

            raise HTTPException(
                status_code=400,
                detail="Tên tài khoản đã tồn tại."
            )

        player_id = create_player_id(
            connection
        )

        password_hash = hash_password(
            password
        )

        cursor.execute(
            """
            INSERT INTO users (
                player_id,
                username,
                password_hash,
                level,
                xp,
                total_games,
                total_correct,
                total_wrong,
                total_blank,
                total_score,
                last_seen
            )
            VALUES (
                ?, ?,
                ?,
                0, 0, 0, 0, 0, 0, 0,
                ?
            )
            """,
            (
                player_id,
                username,
                password_hash,
                utc_now_iso()
            )
        )

        user_id = cursor.lastrowid

        if not user_id:
            connection.rollback()

            raise HTTPException(
                status_code=500,
                detail="Không thể tạo tài khoản."
            )

        connection.commit()

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
            WHERE id = ?
            LIMIT 1
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=500,
                detail="Không thể đọc tài khoản vừa tạo."
            )

    except HTTPException:
        try:
            connection.rollback()
        except Exception:
            pass

        raise

    except Exception as error:
        try:
            connection.rollback()
        except Exception:
            pass

        # UNIQUE constraint có thể xảy ra trong race condition.
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(
                status_code=400,
                detail="Tên tài khoản hoặc Player ID đã tồn tại."
            )

        raise HTTPException(
            status_code=500,
            detail="Không thể tạo tài khoản."
        )

    finally:
        connection.close()

    token = create_token(
        user["id"],
        user["player_id"]
    )

    return {
        "message": "Đăng ký thành công!",
        "token": token,
        "user": serialize_login_user(
            user
        )
    }


# =========================================================
# LOGIN
# =========================================================

@router.post("/login")
def login(
    data: LoginRequest
):
    """
    Đăng nhập bằng username + password.
    """

    username = normalize_username(
        data.username
    )

    password = data.password

    if len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=401,
            detail="Sai tên tài khoản hoặc mật khẩu."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Admin identity lives in admin_accounts, not in the learner users table.
        admin = cursor.execute(
            "SELECT id, username, password_hash, status, auth_version FROM admin_accounts WHERE username=? LIMIT 1",
            (username,)
        ).fetchone()
        if admin:
            if not verify_password(password, admin["password_hash"]):
                raise HTTPException(status_code=401, detail="Sai tên tài khoản hoặc mật khẩu.")
            if admin["status"] != "active":
                raise HTTPException(status_code=403, detail="Tài khoản quản trị đang bị vô hiệu hóa.")
            now = utc_now_iso()
            cursor.execute("UPDATE admin_accounts SET last_login=? WHERE id=?", (now, admin["id"]))
            connection.commit()
            return {
                "message": "Đăng nhập quản trị thành công!",
                "token": create_admin_token(admin["id"], admin["username"], admin["auth_version"]),
                "user": {"id": admin["id"], "player_id": f"MWADMIN{admin['id']}", "username": admin["username"],
                         "level": 0, "xp": 0, "total_games": 0, "total_correct": 0, "total_wrong": 0,
                         "total_blank": 0, "total_score": 0, "role": "admin", "status": admin["status"]}
            }

        cursor.execute(
            """
            SELECT
                id,
                player_id,
                username,
                password_hash,
                level,
                xp,
                total_games,
                total_correct,
                total_wrong,
                total_blank,
                total_score,
                last_seen,
                created_at,
                role,
                status,
                ban_reason
            FROM users
            WHERE username = ?
            LIMIT 1
            """,
            (username,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Sai tên tài khoản hoặc mật khẩu."
            )

        if not verify_password(
            password,
            user["password_hash"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Sai tên tài khoản hoặc mật khẩu."
            )

        if user["status"] == "banned":
            raise HTTPException(
                status_code=403,
                detail=("Tài khoản đã bị tạm khóa. Lý do: " + (user["ban_reason"] or "Liên hệ quản trị viên."))
            )

        now = utc_now_iso()

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

        connection.commit()

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
                created_at,
                role,
                status
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user["id"],)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=500,
                detail="Không thể đọc thông tin tài khoản."
            )

        token = create_token(
            user["id"],
            user["player_id"]
        )

        return {
            "message": "Đăng nhập thành công!",
            "token": token,
            "user": serialize_login_user(
                user
            )
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Không thể đăng nhập."
        )

    finally:
        connection.close()


# =========================================================
# ME
# =========================================================

@router.get("/me")
def me(
    authorization: str | None = Header(
        default=None
    )
):
    """
    Lấy thông tin tài khoản hiện tại.
    """

    token = extract_bearer_token(authorization)
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Phiên đăng nhập đã hết hạn hoặc không hợp lệ.")
    if payload.get("role") == "admin":
        connection = get_connection()
        try:
            admin = connection.execute("SELECT id, username, status, auth_version, created_at, last_login FROM admin_accounts WHERE id=?", (payload["user_id"],)).fetchone()
            if not admin or admin["username"] != payload.get("admin_username") or admin["status"] != "active" or int(admin["auth_version"] or 0) != int(payload.get("auth_version", 0)):
                raise HTTPException(status_code=401, detail="Phiên quản trị đã hết hạn hoặc bị thu hồi.")
            return {"user": {"id": admin["id"], "player_id": f"MWADMIN{admin['id']}", "username": admin["username"],
                             "level": 0, "xp": 0, "total_games": 0, "total_correct": 0, "total_wrong": 0,
                             "total_blank": 0, "total_score": 0, "last_seen": admin["last_login"],
                             "created_at": admin["created_at"], "role": "admin", "status": admin["status"]}}
        finally:
            connection.close()
    user = get_current_user(authorization)
    return {"user": serialize_user(user)}


# =========================================================
# LOGOUT
# =========================================================

@router.post("/logout")
def logout(
    authorization: str | None = Header(
        default=None
    )
):
    """
    Logout phía API.

    Kiến trúc token hiện tại là stateless HMAC token.
    Vì vậy server không lưu session/token trong database.

    Endpoint này xác nhận token hiện tại hợp lệ và yêu cầu
    frontend xóa token khỏi localStorage/sessionStorage/cookie.

    Sau khi frontend xóa token, các request tiếp theo sẽ
    không còn được xác thực.
    """

    token = extract_bearer_token(
        authorization
    )

    payload = verify_token(
        token
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn."
        )

    return {
        "message": "Đăng xuất thành công.",
        "logged_out": True
    }