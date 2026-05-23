from pathlib import Path
import sys

# =========================================================
# Project Path Setting
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.config import OUTPUT_DIR
from app.services.cosyvoice_service import generate_tts_file
from app.services.voice_profile_service import load_voice_profile

# =========================================================
# Test Config
# =========================================================

TEST_TEXT = (
    "안녕하세요. 오늘의 건강 안내를 알려드릴게요. "
    "아침 약을 드신 뒤에는 물을 한 컵 더 마시고, 가벼운 스트레칭을 해 주세요. "
    "몸이 평소와 다르게 불편하면 혼자 참지 마시고 보호자에게 알려 주세요."
)

TEST_VOICE_PROFILE_ID = "register1"
TEST_NOTIFICATION_TYPE = "medication"

# =========================================================
# Test Clone + Evaluation Flow
# =========================================================


def main():
    print("[INFO] Voice cloning test started")
    print(f"[INFO] Project root : {PROJECT_ROOT}")

    profile = load_voice_profile(TEST_VOICE_PROFILE_ID)

    output_path = generate_tts_file(
        text=TEST_TEXT,
        voice_profile_id=TEST_VOICE_PROFILE_ID,
        notification_type=TEST_NOTIFICATION_TYPE,
    )

    print(f"[INFO] Input text       : {TEST_TEXT}")
    print(f"[INFO] Voice profile ID : {TEST_VOICE_PROFILE_ID}")
    print(f"[INFO] Output path      : {output_path}")

    if Path(output_path).exists():
        print("[SUCCESS] Output file created")
    else:
        print("[ERROR] Output file was not created")
        return

    print(f"[INFO] Output directory: {OUTPUT_DIR}")

    # =====================================================
    # Speaker Similarity Evaluation
    # =====================================================

    print("\n[INFO] Speaker similarity evaluation started")

    from evaluation.speaker_similarity import SpeakerSimilarityEvaluator

    similarity_evaluator = SpeakerSimilarityEvaluator()

    similarity_score = similarity_evaluator.calculate_similarity(
        reference_audio_path=profile["reference_audio_path"],
        generated_audio_path=output_path,
    )

    print(f"[RESULT] Speaker Similarity: {similarity_score:.4f}")

    # =====================================================
    # WER Evaluation
    # =====================================================

    print("\n[INFO] WER evaluation started")

    from evaluation.wer_evaluation import WEREvaluator

    wer_evaluator = WEREvaluator(model_name="base")

    wer_result = wer_evaluator.calculate_wer(
        reference_text=TEST_TEXT,
        generated_audio_path=output_path,
    )

    print(f"[RESULT] Reference Text   : {wer_result['reference_text']}")
    print(f"[RESULT] Transcribed Text : {wer_result['transcribed_text']}")
    print(f"[RESULT] WER              : {wer_result['wer']:.4f}")


if __name__ == "__main__":
    main()
