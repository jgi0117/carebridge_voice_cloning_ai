import csv
from pathlib import Path
import sys

# =========================================================
# Project Path Setting
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.config import EVALUATION_RESULT_DIR, OUTPUT_DIR
from app.services.voice_profile_service import load_voice_profile
from evaluation.speaker_similarity import SpeakerSimilarityEvaluator
from evaluation.wer_evaluation import WEREvaluator


EVALUATION_TARGETS = [
    {
        "elder_id": "elder_001",
        "voice_profile_id": "register1",
        "notification_type": "medication",
        "reference_text": "안녕하세요. 오늘 복약 안내를 시작하겠습니다.",
    },
    {
        "elder_id": "elder_002",
        "voice_profile_id": "register2",
        "notification_type": "medication",
        "reference_text": (
            "아버님, 지금은 혈압약을 드실 시간이에요. "
            "약 봉투에 적힌 아침 약을 확인하시고, 물을 충분히 마시면서 천천히 드셔 주세요. "
            "혹시 어지럽거나 불편하시면 바로 보호자에게 연락해 주세요."
        ),
    },
    {
        "elder_id": "elder_003",
        "voice_profile_id": "register3",
        "notification_type": "medication",
        "reference_text": (
            "어머님, 점심 식사는 잘 하셨나요. "
            "이제 식후 약을 챙겨 드실 시간이에요. "
            "약을 드신 뒤에는 잠시 앉아서 쉬시고, 복용을 마치면 앱에서 확인 버튼을 눌러 주세요."
        ),
    },
]


def find_latest_output(elder_id: str, notification_type: str, voice_profile_id: str) -> Path:
    output_dir = OUTPUT_DIR / elder_id / notification_type
    candidates = sorted(
        output_dir.glob(f"{voice_profile_id}_*.wav"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise FileNotFoundError(
            f"No generated wav found for {elder_id}/{notification_type}/{voice_profile_id}"
        )

    return candidates[0]


def main():
    EVALUATION_RESULT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = EVALUATION_RESULT_DIR / "voice_profile_evaluation.csv"

    similarity_evaluator = SpeakerSimilarityEvaluator()
    wer_evaluator = WEREvaluator(model_name="base")

    rows = []

    for target in EVALUATION_TARGETS:
        profile = load_voice_profile(target["voice_profile_id"])
        output_path = find_latest_output(
            elder_id=target["elder_id"],
            notification_type=target["notification_type"],
            voice_profile_id=target["voice_profile_id"],
        )

        similarity_score = similarity_evaluator.calculate_similarity(
            reference_audio_path=profile["reference_audio_path"],
            generated_audio_path=output_path,
        )

        wer_result = wer_evaluator.calculate_wer(
            reference_text=target["reference_text"],
            generated_audio_path=output_path,
        )

        rows.append(
            {
                "elder_id": target["elder_id"],
                "voice_profile_id": target["voice_profile_id"],
                "guardian_id": profile.get("guardian_id"),
                "notification_type": target["notification_type"],
                "reference_audio_path": profile["reference_audio_path"],
                "generated_audio_path": str(output_path),
                "speaker_similarity": f"{similarity_score:.4f}",
                "wer": f"{wer_result['wer']:.4f}",
                "reference_text": wer_result["reference_text"],
                "transcribed_text": wer_result["transcribed_text"],
            }
        )

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "elder_id",
                "voice_profile_id",
                "guardian_id",
                "notification_type",
                "reference_audio_path",
                "generated_audio_path",
                "speaker_similarity",
                "wer",
                "reference_text",
                "transcribed_text",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[SUCCESS] Evaluation CSV created: {csv_path}")


if __name__ == "__main__":
    main()
