from typing import Optional

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    voice_profile_id: Optional[str] = Field(
        default=None,
        description="Registered voice profile ID. Recommended for backend integration.",
    )
    speaker_id: Optional[str] = Field(
        default=None,
        description="Legacy reference voice ID under data/reference_voices",
    )
    prompt_text: Optional[str] = Field(
        default=None,
        description="Optional override transcript of the reference voice.",
    )
    notification_type: Optional[str] = Field(
        default=None,
        description="Output category, such as medication or meal.",
    )


class TTSResponse(BaseModel):
    message: str
    input_text: str
    voice_profile_id: Optional[str] = None
    speaker_id: Optional[str]
    output_path: str


class VoiceProfileResponse(BaseModel):
    message: str
    voice_profile_id: str
    guardian_id: Optional[str] = None
    elder_id: Optional[str] = None
    reference_audio_path: str
    prompt_text: str
    consent: bool
    created_at: str
