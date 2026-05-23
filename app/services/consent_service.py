import json
from pathlib import Path

from app.config import CONSENT_DIR


def save_consent(
    user_id: str,
    agreed: bool,
):
    """
    사용자 동의 여부 저장
    """

    CONSENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_path = CONSENT_DIR / f"{user_id}.json"

    data = {
        "user_id": user_id,
        "agreed": agreed,
    }

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return save_path


def load_consent(user_id: str):
    """
    사용자 동의 여부 불러오기
    """

    save_path = CONSENT_DIR / f"{user_id}.json"

    if not save_path.exists():
        return None

    with open(save_path, "r", encoding="utf-8") as f:
        return json.load(f)