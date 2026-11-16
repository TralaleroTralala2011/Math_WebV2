from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from threading import Lock
import logging
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes import router as auth_router
from .learner_activity_routes import router as learner_activity_router
from .users.routes import router as users_router
from .friends.routes import router as friends_router
from .notifications.routes import router as notifications_router
from .presence.routes import router as presence_router
from .games.routes import router as games_router
from .chat.routes import router as chat_router
from .chat.live import router as chat_live_router
from .chat.calls import router as call_router
from .matchmaking.routes import router as matchmaking_router
from app.ai.routes import router as ai_router
from .admin_routes import router as admin_router
from .update_backup_routes import router as update_backup_router
from .video_routes import router as video_router
from .quality_routes import router as quality_router
from .tutor_routes import router as tutor_router
from .learning_progress_routes import router as learning_progress_router
from .roadmap_v2_routes import router as roadmap_v2_router
from .question_factory_v2_routes import router as qf2_router
from .study_suite_routes import router as study_suite_router
from .final_features_routes import router as final_features_router
from .ai.maintenance_worker import start_worker, stop_worker
from .account_backup_worker import start_account_backup_worker, stop_account_backup_worker
from question_factory.api import make_router as make_question_factory_router
from question_factory.bootstrap import database_path as question_factory_database_path
from question_factory.bootstrap import initialize_factory


# =========================================================
# APP
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background maintenance once per API process; always stop cleanly.
    start_worker()
    start_account_backup_worker()
    try:
        yield
    finally:
        stop_account_backup_worker()
        stop_worker()


app = FastAPI(
    title="MATH WEB API",
    description="Backend API cho nền tảng luyện toán MATH WEB",
    version="1.0.0",
    lifespan=lifespan
)


# Catch unexpected request failures INSIDE CORS middleware so that
# GitHub Pages receives a readable 500 instead of an opaque CORS failure.
# Never reveal tracebacks or credentials to the browser.
@app.middleware("http")
async def safe_unexpected_errors(request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logging.getLogger("mathweb.api").exception("Unhandled API exception for %s", request.url.path)
        return JSONResponse({"detail": "Backend gặp lỗi nội bộ. Kiểm tra Logs của Render."}, status_code=500)

# =========================================================
# CORS
# =========================================================
#
# Cho phép frontend chạy bằng:
#   - localhost
#   - 127.0.0.1
#   - IP LAN của máy
#
# Cho phép nhiều port frontend:
#   5500
#   5501
#   5502
#   ...
#
# Ví dụ:
#   http://192.168.1.3:5500
#   http://192.168.1.3:5501
#
# Backend:
#   http://127.0.0.1:8000
#   http://192.168.1.3:8000
#

app.add_middleware(
    CORSMiddleware,

    # Local development: localhost, loopback và IP private trong LAN.
    # Production: GitHub Pages origin đã cấu hình cho dự án.
    # Chỉ cho phép origin dạng HTTP(S), không cho phép wildcard * khi dùng cookie/token.
    allow_origin_regex=(
        r"^https?://(?:"
        r"localhost|"
        r"127(?:\.\d{1,3}){3}|"
        r"10(?:\.\d{1,3}){3}|"
        r"192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|"
        r"tralalerotralala2011\.github\.io"
        r")(?::\d+)?$"
    ),

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_router)
app.include_router(learner_activity_router)
app.include_router(users_router)
app.include_router(friends_router)
app.include_router(notifications_router)
app.include_router(presence_router)
app.include_router(games_router)
app.include_router(chat_router)
app.include_router(chat_live_router)
app.include_router(call_router)
app.include_router(matchmaking_router)
app.include_router(ai_router)
app.include_router(admin_router)
app.include_router(update_backup_router)
app.include_router(video_router)
app.include_router(quality_router)
app.include_router(tutor_router)
app.include_router(learning_progress_router)
app.include_router(roadmap_v2_router)
app.include_router(qf2_router)
app.include_router(study_suite_router)
app.include_router(final_features_router)
# Keep the existing Question Factory API accessible without altering other routes.
_factory_db_path = question_factory_database_path()
_factory_bootstrap_lock = Lock()
_factory_initialized = False


def ensure_question_factory_ready():
    """Initialize the factory's separate SQLite store only on first API use.

    Do not make unrelated user endpoints depend on the optional factory DB.
    A lock prevents two concurrent initial requests from racing initialization.
    """
    global _factory_initialized
    if _factory_initialized:
        return
    with _factory_bootstrap_lock:
        if not _factory_initialized:
            initialize_factory(_factory_db_path)
            _factory_initialized = True


app.include_router(
    make_question_factory_router(_factory_db_path),
    dependencies=[Depends(ensure_question_factory_ready)],
)

# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "success": True,
        "message": "MATH WEB API đang hoạt động.",
        "version": "1.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "online",
        "service": "MATH WEB API",
        "release": "v33-github-mobile",
        "features": {
            "roadmap_v2": True,
            "activity_heatmap": True,
            "tutor_recommendations": True
        }
    }

