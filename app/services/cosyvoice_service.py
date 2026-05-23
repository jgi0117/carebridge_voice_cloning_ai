from datetime import datetime
import logging
import os
from pathlib import Path
import sys

import librosa
import soundfile as sf
import torch

from app.config import (
    BASE_DIR,
    COSYVOICE_MODEL_DIR,
    COSYVOICE_REPO_DIR,
    OUTPUT_DIR,
    REFERENCE_VOICE_DIR,
)
from app.services.voice_profile_service import load_voice_profile


os.environ.setdefault("HF_HOME", str(BASE_DIR / ".cache" / "huggingface"))
os.environ.setdefault("MODELSCOPE_CACHE", str(BASE_DIR / ".cache" / "modelscope"))
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".cache" / "matplotlib"))
logging.getLogger("numba").setLevel(logging.WARNING)

if COSYVOICE_REPO_DIR.exists():
    sys.path.append(str(COSYVOICE_REPO_DIR))
    sys.path.append(str(COSYVOICE_REPO_DIR / "third_party" / "Matcha-TTS"))


def _load_cosyvoice_model():
    if not COSYVOICE_REPO_DIR.exists():
        raise FileNotFoundError(
            "CosyVoice repo not found. Clone it to "
            f"{COSYVOICE_REPO_DIR}"
        )

    if not COSYVOICE_MODEL_DIR.exists() or not any(COSYVOICE_MODEL_DIR.iterdir()):
        raise FileNotFoundError(
            "CosyVoice model checkpoint not found. Download it to "
            f"{COSYVOICE_MODEL_DIR}"
        )

    try:
        from cosyvoice.cli.cosyvoice import CosyVoice2
        import cosyvoice.cli.frontend as frontend_module
        import cosyvoice.utils.file_utils as file_utils_module
    except ImportError as exc:
        raise ImportError(
            "CosyVoice is not importable. Install the CosyVoice requirements "
            "or run this service in the CosyVoice environment."
        ) from exc

    file_utils_module.load_wav = _load_wav_compat
    frontend_module.load_wav = _load_wav_compat
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("numba").setLevel(logging.WARNING)

    return CosyVoice2(
        str(COSYVOICE_MODEL_DIR),
        load_jit=False,
        load_trt=False,
        fp16=torch.cuda.is_available(),
    )


def _load_wav_compat(wav, target_sr, min_sr=16000):
    audio, sample_rate = librosa.load(
        str(wav),
        sr=None,
        mono=True,
    )

    if sample_rate != target_sr:
        if sample_rate < min_sr:
            raise ValueError(
                f"wav sample rate {sample_rate} must be greater than {min_sr}"
            )
        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=target_sr,
        )

    return torch.tensor(audio, dtype=torch.float32).unsqueeze(0)


def _pick_first_audio(result_generator):
    for result in result_generator:
        if "tts_speech" not in result:
            continue
        return result["tts_speech"]

    raise RuntimeError("CosyVoice did not return any tts_speech output.")


def generate_tts_file(
    text: str,
    voice_profile_id: str | None = None,
    speaker_id: str | None = None,
    prompt_text: str | None = None,
    notification_type: str | None = None,
) -> Path:
    """
    Generate cloned speech with CosyVoice.

    CosyVoice zero-shot works best when prompt_text is the transcript of the
    reference audio. If prompt_text is omitted, this falls back to cross-lingual
    inference, which only conditions on the prompt speech.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if voice_profile_id:
        profile = load_voice_profile(voice_profile_id)
        speaker_name = profile["voice_profile_id"]
        reference_audio_path = Path(profile["reference_audio_path"])
        prompt_text = prompt_text or profile.get("prompt_text")
        output_base_dir = OUTPUT_DIR / profile.get("elder_id", "unassigned")
    else:
        speaker_name = speaker_id or "sample_reference"
        reference_audio_path = REFERENCE_VOICE_DIR / f"{speaker_name}.wav"
        output_base_dir = OUTPUT_DIR

    if notification_type:
        output_base_dir = output_base_dir / notification_type

    output_base_dir.mkdir(parents=True, exist_ok=True)

    if not reference_audio_path.exists():
        raise FileNotFoundError(
            f"Reference voice not found: {reference_audio_path}"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_base_dir / f"{speaker_name}_{timestamp}.wav"

    cosyvoice = _load_cosyvoice_model()
    if prompt_text:
        result_generator = cosyvoice.inference_zero_shot(
            tts_text=text,
            prompt_text=prompt_text,
            prompt_wav=str(reference_audio_path),
            stream=False,
        )
    else:
        result_generator = cosyvoice.inference_cross_lingual(
            tts_text=text,
            prompt_wav=str(reference_audio_path),
            stream=False,
        )

    audio = _pick_first_audio(result_generator)

    sf.write(
        str(output_path),
        audio.squeeze(0).detach().cpu().numpy(),
        cosyvoice.sample_rate,
    )

    if not output_path.exists():
        raise FileNotFoundError(
            f"Output audio was not created: {output_path}"
        )

    return output_path
