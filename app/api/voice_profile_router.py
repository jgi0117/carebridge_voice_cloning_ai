from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.voice_schema import VoiceProfileResponse
from app.services.voice_profile_service import (
    list_voice_profiles,
    save_voice_profile,
)


router = APIRouter(
    prefix="/voices",
    tags=["voices"],
)


@router.post("/register", response_model=VoiceProfileResponse)
def register_voice(
    voice_profile_id: str = Form(...),
    prompt_text: str = Form(...),
    audio_file: UploadFile = File(...),
    guardian_id: str | None = Form(default=None),
    elder_id: str | None = Form(default=None),
    consent: bool = Form(default=True),
):
    metadata = save_voice_profile(
        voice_profile_id=voice_profile_id,
        prompt_text=prompt_text,
        audio_file=audio_file,
        guardian_id=guardian_id,
        elder_id=elder_id,
        consent=consent,
    )

    return VoiceProfileResponse(
        message="Voice profile registered",
        **metadata,
    )


@router.get("/profiles")
def get_voice_profiles():
    return {
        "profiles": list_voice_profiles(),
    }
