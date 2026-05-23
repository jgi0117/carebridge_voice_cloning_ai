from pathlib import Path

ALLOWED_AUDIO_EXTENSIONS = [".wav", ".mp3"]


def validate_audio_file(file_path: Path) -> bool:
    """
    지원 가능한 음성 파일인지 확인
    """

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")

    if file_path.suffix.lower() not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValueError(
            f"지원하지 않는 파일 형식: {file_path.suffix}"
        )

    return True