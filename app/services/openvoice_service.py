from datetime import datetime
from pathlib import Path
import sys

import torch

from app.config import (
    OUTPUT_DIR,
    REFERENCE_VOICE_DIR,
    OPENVOICE_REPO_DIR,
    OPENVOICE_CHECKPOINT_V2_DIR,
)

# =========================================================
# OpenVoice Import Path
# =========================================================

sys.path.append(str(OPENVOICE_REPO_DIR))

from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS

# =========================================================
# OpenVoice Service
# =========================================================

def generate_tts_file(
    text: str,
    speaker_id: str | None = None,
    language: str = "KR",
    speaker_key: str = "KR",
) -> Path:
    """
    OpenVoice V2 기반 Voice Cloning 생성 함수

    필요 조건:
    1. 프로젝트 루트에 OpenVoice repo clone
    2. checkpoints/openvoice/checkpoints_v2 다운로드 완료
    3. data/reference_voices/{speaker_id}.wav 존재
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    speaker_name = speaker_id or "sample_reference"
    reference_audio_path = REFERENCE_VOICE_DIR / f"{speaker_name}.wav"

    if not OPENVOICE_REPO_DIR.exists():
        raise FileNotFoundError(
            f"OpenVoice repo not found: {OPENVOICE_REPO_DIR}"
        )

    if not OPENVOICE_CHECKPOINT_V2_DIR.exists():
        raise FileNotFoundError(
            f"OpenVoice checkpoint not found: {OPENVOICE_CHECKPOINT_V2_DIR}"
        )

    if not reference_audio_path.exists():
        raise FileNotFoundError(
            f"Reference voice not found: {reference_audio_path}"
        )

    converter_config = OPENVOICE_CHECKPOINT_V2_DIR / "converter" / "config.json"
    converter_checkpoint = OPENVOICE_CHECKPOINT_V2_DIR / "converter" / "checkpoint.pth"

    if not converter_config.exists():
        raise FileNotFoundError(f"Converter config not found: {converter_config}")

    if not converter_checkpoint.exists():
        raise FileNotFoundError(f"Converter checkpoint not found: {converter_checkpoint}")

    source_se_path = (
        OPENVOICE_CHECKPOINT_V2_DIR
        / "base_speakers"
        / "ses"
        / f"{speaker_key}.pth"
    )

    if not source_se_path.exists():
        raise FileNotFoundError(
            f"Source speaker embedding not found: {source_se_path}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = OUTPUT_DIR / f"{speaker_name}_{timestamp}.wav"
    temp_path = OUTPUT_DIR / f"tmp_{speaker_name}_{timestamp}.wav"
    processed_dir = OUTPUT_DIR / "processed"

    processed_dir.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # 1. Load Tone Color Converter
    # =====================================================

    tone_color_converter = ToneColorConverter(
        str(converter_config),
        device=device,
    )

    tone_color_converter.load_ckpt(
        str(converter_checkpoint)
    )

    # =====================================================
    # 2. Load Base TTS Model
    # =====================================================

    tts_model = TTS(
        language=language,
        device=device,
    )

    speaker_ids = tts_model.hps.data.spk2id

    if speaker_key not in speaker_ids:
        raise ValueError(
            f"speaker_key '{speaker_key}' not found. Available keys: {list(speaker_ids.keys())}"
        )

    # =====================================================
    # 3. Extract Target Speaker Embedding
    # =====================================================

    target_se, _ = se_extractor.get_se(
        str(reference_audio_path),
        tone_color_converter,
        target_dir=str(processed_dir),
        vad=True,
    )

    # =====================================================
    # 4. Load Source Speaker Embedding
    # =====================================================

    source_se = torch.load(
        source_se_path,
        map_location=device,
    )

    # =====================================================
    # 5. Generate Base TTS Audio
    # =====================================================

    tts_model.tts_to_file(
        text,
        speaker_ids[speaker_key],
        str(temp_path),
        speed=1.0,
    )

    # =====================================================
    # 6. Convert Tone Color
    # =====================================================

    tone_color_converter.convert(
        audio_src_path=str(temp_path),
        src_se=source_se,
        tgt_se=target_se,
        output_path=str(output_path),
        message="@FamilyVoiceGuide",
    )

    if not output_path.exists():
        raise FileNotFoundError(
            f"Output audio was not created: {output_path}"
        )

    return output_path