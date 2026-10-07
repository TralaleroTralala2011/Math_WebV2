from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes import router as auth_router
from .users.routes import router as users_router
from .friends.routes import router as friends_router
from .notifications.routes import router as notifications_router
from .presence.routes import router as presence_router
from .games.routes import router as games_router
from .chat.routes import router as chat_router
from .matchmaking.routes import router as matchmaking_router
from app.ai.routes import router as ai_router


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="MATH WEB API",
    description="Backend API cho nền tảng luyện toán MATH WEB",
    version="1.0.0"
)


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

    # Cho phép localhost / 127.0.0.1 / IP LAN
    # với bất kỳ port nào.
    allow_origin_regex=(
        r"^https?://"
        r"(localhost|127\.0\.0\.1|192\.168\.1\.3|tralalerotralala2011\.github\.io)"
        r"(:\d+)?$"
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
app.include_router(users_router)
app.include_router(friends_router)
app.include_router(notifications_router)
app.include_router(presence_router)
app.include_router(games_router)
app.include_router(chat_router)
app.include_router(matchmaking_router)
app.include_router(ai_router)

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
        "service": "MATH WEB API"
    }