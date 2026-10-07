import sqlite3

from datetime import datetime, timezone
from pathlib import Path


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "mathweb.db"


# =========================================================
# CONFIG
# =========================================================

MAX_LEVEL = 1000

DATABASE_VERSION = 1

DATABASE_TIMEOUT_SECONDS = 10

DATABASE_BUSY_TIMEOUT_MS = 10000


# =========================================================
# GET UTC TIME
# =========================================================

def utc_now_iso():
    """
    Trả về thời gian UTC dạng ISO.
    """

    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )


# =========================================================
# GET CONNECTION
# =========================================================

def get_connection():
    """
    Tạo SQLite connection dùng chung cho toàn backend.

    Mỗi request tự mở một connection và tự đóng connection.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=DATABASE_TIMEOUT_SECONDS
    )

    connection.row_factory = sqlite3.Row

    # -----------------------------------------------------
    # Foreign keys
    # -----------------------------------------------------

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    # -----------------------------------------------------
    # Busy timeout
    # -----------------------------------------------------

    connection.execute(
        f"PRAGMA busy_timeout = {DATABASE_BUSY_TIMEOUT_MS}"
    )

    # -----------------------------------------------------
    # WAL
    # -----------------------------------------------------
    #
    # Cho phép nhiều reader hoạt động ổn định hơn khi có
    # writer.
    #

    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    # -----------------------------------------------------
    # Synchronous
    # -----------------------------------------------------

    connection.execute(
        "PRAGMA synchronous = NORMAL"
    )

    return connection


# =========================================================
# CHECK TABLE
# =========================================================

def table_exists(
    connection,
    table_name
):
    """
    Kiểm tra table có tồn tại hay không.

    table_name chỉ được sử dụng nội bộ trong code,
    không nhận trực tiếp từ request người dùng.
    """

    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        LIMIT 1
        """,
        (table_name,)
    )

    return cursor.fetchone() is not None


# =========================================================
# GET COLUMNS
# =========================================================

def get_columns(
    connection,
    table_name
):
    """
    Lấy danh sách column của table.
    """

    if not table_exists(
        connection,
        table_name
    ):
        return set()

    cursor = connection.execute(
        f"PRAGMA table_info({table_name})"
    )

    return {
        row["name"]
        for row in cursor.fetchall()
    }


# =========================================================
# ADD COLUMN IF MISSING
# =========================================================

def add_column_if_missing(
    connection,
    table_name,
    column_name,
    column_definition
):
    """
    Thêm column nếu database cũ chưa có.

    Các giá trị table/column ở đây đều là hằng số nội bộ
    của application, không lấy trực tiếp từ user input.
    """

    columns = get_columns(
        connection,
        table_name
    )

    if column_name not in columns:

        connection.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name}
            {column_definition}
            """
        )


# =========================================================
# NORMALIZE INTEGER COLUMN
# =========================================================

def normalize_non_negative_column(
    connection,
    table_name,
    column_name
):
    """
    Đưa NULL hoặc số âm về 0.
    """

    if column_name not in get_columns(
        connection,
        table_name
    ):
        return

    connection.execute(
        f"""
        UPDATE {table_name}
        SET {column_name} = 0
        WHERE {column_name} IS NULL
           OR {column_name} < 0
        """
    )


# =========================================================
# DATABASE METADATA
# =========================================================

def init_database_metadata(
    connection
):
    """
    Bảng metadata nhỏ để theo dõi version database.
    """

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS database_metadata (

            key TEXT PRIMARY KEY,

            value TEXT,

            updated_at TEXT
        )
        """
    )

    connection.execute(
        """
        INSERT INTO database_metadata (
            key,
            value,
            updated_at
        )
        VALUES (
            'schema_version',
            ?,
            ?
        )
        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
        """,
        (
            str(DATABASE_VERSION),
            utc_now_iso()
        )
    )


# =========================================================
# INIT DATABASE
# =========================================================

def init_database():
    """
    Khởi tạo và migrate toàn bộ database.

    Hàm này có thể gọi nhiều lần.
    Nó không xóa dữ liệu cũ.
    """

    connection = get_connection()

    try:

        # =====================================================
        # DATABASE METADATA
        # =====================================================

        init_database_metadata(
            connection
        )

        # =====================================================
        # USERS
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                player_id TEXT UNIQUE NOT NULL,

                username TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                level INTEGER NOT NULL DEFAULT 0,

                xp INTEGER NOT NULL DEFAULT 0,

                total_games INTEGER NOT NULL DEFAULT 0,

                total_correct INTEGER NOT NULL DEFAULT 0,

                total_wrong INTEGER NOT NULL DEFAULT 0,

                total_blank INTEGER NOT NULL DEFAULT 0,

                total_score INTEGER NOT NULL DEFAULT 0,

                last_seen TEXT,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # =====================================================
        # USERS MIGRATION
        # =====================================================

        add_column_if_missing(
            connection,
            "users",
            "level",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "xp",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "total_games",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "total_correct",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "total_wrong",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "total_blank",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "total_score",
            "INTEGER NOT NULL DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "users",
            "last_seen",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "users",
            "created_at",
            "TEXT"
        )

        # =====================================================
        # USERS DATA NORMALIZATION
        # =====================================================

        connection.execute(
            """
            UPDATE users
            SET level = 0
            WHERE level IS NULL
               OR level < 0
            """
        )

        connection.execute(
            """
            UPDATE users
            SET level = ?
            WHERE level > ?
            """,
            (
                MAX_LEVEL,
                MAX_LEVEL
            )
        )

        normalize_non_negative_column(
            connection,
            "users",
            "xp"
        )

        normalize_non_negative_column(
            connection,
            "users",
            "total_games"
        )

        normalize_non_negative_column(
            connection,
            "users",
            "total_correct"
        )

        normalize_non_negative_column(
            connection,
            "users",
            "total_wrong"
        )

        normalize_non_negative_column(
            connection,
            "users",
            "total_blank"
        )

        normalize_non_negative_column(
            connection,
            "users",
            "total_score"
        )

        # =====================================================
        # GAME RESULTS
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS game_results (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                game_id TEXT NOT NULL,

                game_name TEXT NOT NULL,

                topic TEXT NOT NULL,

                total_questions INTEGER NOT NULL DEFAULT 0,

                correct INTEGER NOT NULL DEFAULT 0,

                wrong INTEGER NOT NULL DEFAULT 0,

                blank INTEGER NOT NULL DEFAULT 0,

                score INTEGER NOT NULL DEFAULT 0,

                xp INTEGER NOT NULL DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
            )
            """
        )

        # =====================================================
        # GAME RESULTS MIGRATION
        # =====================================================

        add_column_if_missing(
            connection,
            "game_results",
            "game_id",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "game_name",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "topic",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "total_questions",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "correct",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "wrong",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "blank",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "score",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "xp",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "game_results",
            "created_at",
            "TEXT"
        )

        # =====================================================
        # MIGRATE OLD GAME RESULTS
        # =====================================================

        game_result_columns = get_columns(
            connection,
            "game_results"
        )

        # topic_name -> topic

        if "topic_name" in game_result_columns:

            connection.execute(
                """
                UPDATE game_results
                SET topic = topic_name
                WHERE (
                    topic IS NULL
                    OR topic = ''
                )
                AND topic_name IS NOT NULL
                """
            )

        # total -> total_questions

        if "total" in game_result_columns:

            connection.execute(
                """
                UPDATE game_results
                SET total_questions = total
                WHERE (
                    total_questions IS NULL
                    OR total_questions = 0
                )
                AND total IS NOT NULL
                """
            )

        # =====================================================
        # FIX GAME RESULT DATA
        # =====================================================

        connection.execute(
            """
            UPDATE game_results
            SET game_id = 'legacy-' || id
            WHERE game_id IS NULL
               OR game_id = ''
            """
        )

        connection.execute(
            """
            UPDATE game_results
            SET game_name = 'Luyện tập Toán'
            WHERE game_name IS NULL
               OR game_name = ''
            """
        )

        connection.execute(
            """
            UPDATE game_results
            SET topic = 'tong-hop'
            WHERE topic IS NULL
               OR topic = ''
            """
        )

        normalize_non_negative_column(
            connection,
            "game_results",
            "total_questions"
        )

        normalize_non_negative_column(
            connection,
            "game_results",
            "correct"
        )

        normalize_non_negative_column(
            connection,
            "game_results",
            "wrong"
        )

        normalize_non_negative_column(
            connection,
            "game_results",
            "blank"
        )

        normalize_non_negative_column(
            connection,
            "game_results",
            "score"
        )

        normalize_non_negative_column(
            connection,
            "game_results",
            "xp"
        )

        # =====================================================
        # FRIENDS
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS friends (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                requester_id INTEGER NOT NULL,

                receiver_id INTEGER NOT NULL,

                status TEXT NOT NULL DEFAULT 'pending',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (requester_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                CHECK (
                    requester_id != receiver_id
                ),

                CHECK (
                    status IN (
                        'pending',
                        'accepted',
                        'rejected'
                    )
                )
            )
            """
        )

        # =====================================================
        # FRIENDS MIGRATION
        # =====================================================

        add_column_if_missing(
            connection,
            "friends",
            "requester_id",
            "INTEGER"
        )

        add_column_if_missing(
            connection,
            "friends",
            "receiver_id",
            "INTEGER"
        )

        add_column_if_missing(
            connection,
            "friends",
            "status",
            "TEXT DEFAULT 'pending'"
        )

        add_column_if_missing(
            connection,
            "friends",
            "created_at",
            "TEXT"
        )

        connection.execute(
            """
            UPDATE friends
            SET status = 'pending'
            WHERE status IS NULL
               OR status NOT IN (
                   'pending',
                   'accepted',
                   'rejected'
               )
            """
        )

        # =====================================================
        # MESSAGES
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,

                receiver_id INTEGER NOT NULL,

                content TEXT NOT NULL,

                is_read INTEGER NOT NULL DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (sender_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                CHECK (
                    length(content) > 0
                ),

                CHECK (
                    length(content) <= 1000
                )
            )
            """
        )

        # =====================================================
        # MESSAGES MIGRATION
        # =====================================================

        add_column_if_missing(
            connection,
            "messages",
            "sender_id",
            "INTEGER"
        )

        add_column_if_missing(
            connection,
            "messages",
            "receiver_id",
            "INTEGER"
        )

        add_column_if_missing(
            connection,
            "messages",
            "content",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "messages",
            "is_read",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "messages",
            "created_at",
            "TEXT"
        )

        connection.execute(
            """
            UPDATE messages
            SET is_read = 0
            WHERE is_read IS NULL
               OR is_read NOT IN (0, 1)
            """
        )

        # =====================================================
        # NOTIFICATIONS
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                type TEXT NOT NULL,

                content TEXT NOT NULL DEFAULT '',

                title TEXT,

                message TEXT,

                related_user_id INTEGER,

                related_id TEXT,

                is_read INTEGER NOT NULL DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                FOREIGN KEY (related_user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
            )
            """
        )

        # =====================================================
        # NOTIFICATIONS MIGRATION
        # =====================================================

        add_column_if_missing(
            connection,
            "notifications",
            "type",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "content",
            "TEXT DEFAULT ''"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "title",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "message",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "related_user_id",
            "INTEGER"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "related_id",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "is_read",
            "INTEGER DEFAULT 0"
        )

        add_column_if_missing(
            connection,
            "notifications",
            "created_at",
            "TEXT"
        )

        # =====================================================
        # FIX NOTIFICATION DATA
        # =====================================================

        connection.execute(
            """
            UPDATE notifications
            SET type = 'system'
            WHERE type IS NULL
               OR type = ''
            """
        )

        connection.execute(
            """
            UPDATE notifications
            SET content = ''
            WHERE content IS NULL
            """
        )

        connection.execute(
            """
            UPDATE notifications
            SET is_read = 0
            WHERE is_read IS NULL
               OR is_read NOT IN (0, 1)
            """
        )

        # =====================================================
        # QUESTION SESSIONS
        # =====================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS question_sessions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                game_id TEXT,

                topic TEXT NOT NULL,

                difficulty TEXT NOT NULL,

                concept TEXT,

                question_json TEXT NOT NULL,

                correct_answer TEXT NOT NULL,

                explanation TEXT,

                selected_answer TEXT,

                is_correct INTEGER,

                status TEXT NOT NULL DEFAULT 'active',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                expires_at TEXT,

                answered_at TEXT,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

                CHECK (
                    status IN (
                        'active',
                        'answered',
                        'expired'
                    )
                )
            )
            """
        )

        # =====================================================
        # QUESTION SESSION MIGRATION
        # =====================================================

        add_column_if_missing(
            connection,
            "question_sessions",
            "game_id",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "topic",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "difficulty",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "concept",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "question_json",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "correct_answer",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "explanation",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "selected_answer",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "is_correct",
            "INTEGER"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "status",
            "TEXT DEFAULT 'active'"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "created_at",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "expires_at",
            "TEXT"
        )

        add_column_if_missing(
            connection,
            "question_sessions",
            "answered_at",
            "TEXT"
        )

        # =====================================================
        # FIX QUESTION SESSION DATA
        # =====================================================

        connection.execute(
            """
            UPDATE question_sessions
            SET status = 'active'
            WHERE status IS NULL
               OR status NOT IN (
                   'active',
                   'answered',
                   'expired'
               )
            """
        )

        connection.execute(
            """
            UPDATE question_sessions
            SET is_correct = NULL
            WHERE is_correct NOT IN (0, 1)
            """
        )

        # =====================================================
        # EXPIRE OLD QUESTION SESSIONS
        # =====================================================
        #
        # Không xóa session.
        # Chỉ chuyển active -> expired.
        #

        current_time = utc_now_iso()

        connection.execute(
            """
            UPDATE question_sessions
            SET
                status = 'expired'
            WHERE status = 'active'
              AND expires_at IS NOT NULL
              AND expires_at < ?
            """,
            (current_time,)
        )

        # =====================================================
        # INDEXES: USERS
        # =====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_users_username
            ON users(username)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_users_player_id
            ON users(player_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_users_last_seen
            ON users(last_seen)
            """
        )

        # =====================================================
        # INDEXES: GAME RESULTS
        # =====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_game_results_user_id
            ON game_results(user_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_game_results_created_at
            ON game_results(created_at)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_game_results_game_id
            ON game_results(game_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_game_results_user_game
            ON game_results(
                user_id,
                game_id
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_game_results_user_created
            ON game_results(
                user_id,
                created_at
            )
            """
        )

        # =====================================================
        # INDEXES: FRIENDS
        # =====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_friends_requester
            ON friends(requester_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_friends_receiver
            ON friends(receiver_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_friends_status
            ON friends(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_friends_requester_status
            ON friends(
                requester_id,
                status
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_friends_receiver_status
            ON friends(
                receiver_id,
                status
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_friends_pair
            ON friends(
                requester_id,
                receiver_id,
                status
            )
            """
        )

        # =====================================================
        # INDEXES: MESSAGES
        # =====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_sender
            ON messages(sender_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_receiver
            ON messages(receiver_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_created_at
            ON messages(created_at)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_conversation
            ON messages(
                sender_id,
                receiver_id,
                id
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_messages_receiver_read
            ON messages(
                receiver_id,
                is_read,
                id
            )
            """
        )

        # =====================================================
        # INDEXES: NOTIFICATIONS
        # =====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_notifications_user
            ON notifications(user_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_notifications_unread
            ON notifications(
                user_id,
                is_read
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_notifications_user_created
            ON notifications(
                user_id,
                created_at
            )
            """
        )

        # =====================================================
        # INDEXES: QUESTION SESSIONS
        # =====================================================

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_question_sessions_user
            ON question_sessions(user_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_question_sessions_game
            ON question_sessions(game_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_question_sessions_status
            ON question_sessions(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_question_sessions_expires
            ON question_sessions(expires_at)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_question_sessions_user_status
            ON question_sessions(
                user_id,
                status
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_question_sessions_user_game
            ON question_sessions(
                user_id,
                game_id
            )
            """
        )

        # =====================================================
        # COMMIT
        # =====================================================

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# =========================================================
# AUTO INIT
# =========================================================

init_database()