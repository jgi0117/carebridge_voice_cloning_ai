from fastapi import APIRouter

from app.schemas.voice_schema import TTSRequest, TTSResponse
from app.services.cosyvoice_service import generate_tts_file

router = APIRouter(
    prefix="/tts",
    tags=["tts"],
)

# =========================================================
# TTS Router Health Check
# =========================================================

@router.get("/health")
def tts_health_check():
    return {
        "status": "tts router ok"
    }

# =========================================================
# TTS Generate API
# =========================================================

@router.post("/generate", response_model=TTSResponse)
def generate_tts(request: TTSRequest):
    output_path = generate_tts_file(
        text=request.text,
        voice_profile_id=request.voice_profile_id,
        speaker_id=request.speaker_id,
        prompt_text=request.prompt_text,
        notification_type=request.notification_type,
    )

    return TTSResponse(
        message="TTS file generated",
        input_text=request.text,
        voice_profile_id=request.voice_profile_id,
        speaker_id=request.speaker_id,
        output_path=str(output_path),
    )
