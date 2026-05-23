from fastapi import FastAPI

from app.api.voice_profile_router import router as voice_profile_router
from app.api.voice_router import router as voice_router
from app.config import create_directories

# =========================================================
# App Initialization
# =========================================================

create_directories()

app = FastAPI(
    title="Family Voice Guide",
    description="Voice Cloning 기반 가족 맞춤 음성 안내 API",
    version="0.1.0",
)

# =========================================================
# Router
# =========================================================

app.include_router(voice_router)
app.include_router(voice_profile_router)

# =========================================================
# Health Check
# =========================================================

@app.get("/")
def root():
    return {
        "message": "Family Voice Guide API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }
