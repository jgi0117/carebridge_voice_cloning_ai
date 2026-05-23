import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app.config import VOICE_PROFILE_DIR


REFERENCE_FILENAME = "reference.wav"
METADATA_FILENAME = "metadata.json"


def _safe_profile_id(voice_profile_id: str) -> str:
    value = voice_profile_id.strip()

    if not value:
        raise ValueError("voice_profile_id is required")

    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError(
            "voice_profile_id can only contain letters, numbers, underscores, and hyphens"
        )

    return value


def get_profile_dir(voice_profile_id: str) -> Path:
    return VOICE_PROFILE_DIR / _safe_profile_id(voice_profile_id)


def get_reference_audio_path(voice_profile_id: str) -> Path:
    return get_profile_dir(voice_profile_id) / REFERENCE_FILENAME


def get_metadata_path(voice_profile_id: str) -> Path:
    return get_profile_dir(voice_profile_id) / METADATA_FILENAME


def save_voice_profile(
    voice_profile_id: str,
    prompt_text: str,
    audio_file: UploadFile,
    guardian_id: str | None = None,
    elder_id: str | None = None,
    consent: bool = True,
) -> dict:
    profile_id = _safe_profile_id(voice_profile_id)
    profile_dir = get_profile_dir(profile_id)
    profile_dir.mkdir(parents=True, exist_ok=True)

    reference_audio_path = profile_dir / REFERENCE_FILENAME

    with reference_audio_path.open("wb") as output:
        shutil.copyfileobj(audio_file.file, output)

    metadata = {
        "voice_profile_id": profile_id,
        "guardian_id": guardian_id,
        "elder_id": elder_id,
        "reference_audio_path": str(reference_audio_path),
        "prompt_text": prompt_text,
        "consent": consent,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with (profile_dir / METADATA_FILENAME).open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return metadata


def create_voice_profile_from_file(
    voice_profile_id: str,
    source_audio_path: str | Path,
    prompt_text: str,
    guardian_id: str | None = None,
    elder_id: str | None = None,
    consent: bool = True,
) -> dict:
    profile_id = _safe_profile_id(voice_profile_id)
    source = Path(source_audio_path)

    if not source.exists():
        raise FileNotFoundError(f"Reference audio not found: {source}")

    profile_dir = get_profile_dir(profile_id)
    profile_dir.mkdir(parents=True, exist_ok=True)
    reference_audio_path = profile_dir / REFERENCE_FILENAME

    shutil.copy2(source, reference_audio_path)

    metadata = {
        "voice_profile_id": profile_id,
        "guardian_id": guardian_id,
        "elder_id": elder_id,
        "reference_audio_path": str(reference_audio_path),
        "prompt_text": prompt_text,
        "consent": consent,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with (profile_dir / METADATA_FILENAME).open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return metadata


def load_voice_profile(voice_profile_id: str) -> dict:
    metadata_path = get_metadata_path(voice_profile_id)

    if not metadata_path.exists():
        raise FileNotFoundError(f"Voice profile not found: {voice_profile_id}")

    with metadata_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)

    reference_audio_path = Path(metadata["reference_audio_path"])

    if not reference_audio_path.exists():
        raise FileNotFoundError(
            f"Reference audio for profile '{voice_profile_id}' not found: {reference_audio_path}"
        )

    return metadata


def list_voice_profiles() -> list[dict]:
    if not VOICE_PROFILE_DIR.exists():
        return []

    profiles = []

    for metadata_path in sorted(VOICE_PROFILE_DIR.glob(f"*/{METADATA_FILENAME}")):
        with metadata_path.open("r", encoding="utf-8") as f:
            profiles.append(json.load(f))

    return profiles
