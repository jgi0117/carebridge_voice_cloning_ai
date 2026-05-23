from pathlib import Path
import sys

# =========================================================
# Project Path Setting
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.config import REFERENCE_VOICE_DIR
from app.services.voice_profile_service import create_voice_profile_from_file


PROMPT_TEXT = (
    "솔직히 저희들이 힘든 게 단순히 뭐, 일자리가 없고 또 뭐, "
    "일을 하는 게 너무 힘들고 이것만은 아니거든요. "
    "분명히 정서적으로도 힘든 것들이 많으니까 그런 것들에 대해서도 "
    "좀 더 공감을 많이 해 주시고, 왜 이 친구들이 이렇게까지 힘들어할까라는 것에 대해서 "
    "더 많이 공감을 해주셨으면 좋겠습니다."
)


DEMO_PROFILES = [
    {
        "voice_profile_id": "register1",
        "source_audio_path": REFERENCE_VOICE_DIR / "daughter.wav",
        "guardian_id": "guardian_001",
        "elder_id": "elder_001",
    },
    {
        "voice_profile_id": "register2",
        "source_audio_path": REFERENCE_VOICE_DIR / "daughter.wav",
        "guardian_id": "guardian_002",
        "elder_id": "elder_002",
    },
    {
        "voice_profile_id": "register3",
        "source_audio_path": REFERENCE_VOICE_DIR / "daughter.wav",
        "guardian_id": "guardian_003",
        "elder_id": "elder_003",
    },
]


def main():
    for profile in DEMO_PROFILES:
        metadata = create_voice_profile_from_file(
            voice_profile_id=profile["voice_profile_id"],
            source_audio_path=profile["source_audio_path"],
            prompt_text=PROMPT_TEXT,
            guardian_id=profile["guardian_id"],
            elder_id=profile["elder_id"],
            consent=True,
        )

        print("[SUCCESS] Voice profile registered")
        print(f"[INFO] voice_profile_id : {metadata['voice_profile_id']}")
        print(f"[INFO] reference_audio   : {metadata['reference_audio_path']}")


if __name__ == "__main__":
    main()
