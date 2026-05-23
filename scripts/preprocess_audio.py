from pathlib import Path
import sys
import librosa
import soundfile as sf

# =========================================================
# Project Path Setting
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.config import REFERENCE_VOICE_DIR, DEFAULT_SAMPLE_RATE


# =========================================================
# Config
# =========================================================

INPUT_AUDIO_PATH = Path("data/raw_voice/sample_voice.mp3")
OUTPUT_AUDIO_PATH = REFERENCE_VOICE_DIR / "sample_reference.wav"

TARGET_SAMPLE_RATE = DEFAULT_SAMPLE_RATE


# =========================================================
# Audio Preprocessing
# =========================================================

def preprocess_audio(
    input_path: Path,
    output_path: Path,
    target_sample_rate: int = 24000,
):
    if not input_path.exists():
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio, sr = librosa.load(
        input_path,
        sr=target_sample_rate,
        mono=True,
    )

    sf.write(
        output_path,
        audio,
        target_sample_rate,
    )

    print("[SUCCESS] Audio preprocessing completed")
    print(f"[INFO] Input path : {input_path}")
    print(f"[INFO] Output path: {output_path}")
    print(f"[INFO] Sample rate: {target_sample_rate}")
    print("[INFO] Channel    : mono")

    return output_path


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":
    preprocess_audio(
        input_path=INPUT_AUDIO_PATH,
        output_path=OUTPUT_AUDIO_PATH,
        target_sample_rate=TARGET_SAMPLE_RATE,
    )