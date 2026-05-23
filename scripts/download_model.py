from pathlib import Path
import sys

# =========================================================
# Project Path Setting
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.config import COSYVOICE_MODEL_DIR


MODEL_ID = "FunAudioLLM/CosyVoice2-0.5B"


def main():
    """
    Download CosyVoice2 model files from Hugging Face.

    This requires:
      pip install huggingface_hub

    The CosyVoice repository itself must still be cloned separately to:
      ./CosyVoice
    """

    if COSYVOICE_MODEL_DIR.exists() and any(COSYVOICE_MODEL_DIR.iterdir()):
        print("[INFO] CosyVoice checkpoint already exists")
        print(f"[INFO] path: {COSYVOICE_MODEL_DIR}")
        return

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise ImportError(
            "huggingface_hub is required to download CosyVoice checkpoints."
        ) from exc

    print("[INFO] CosyVoice model download started")
    print(f"[INFO] model: {MODEL_ID}")
    print(f"[INFO] path : {COSYVOICE_MODEL_DIR}")

    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=str(COSYVOICE_MODEL_DIR),
        local_dir_use_symlinks=False,
    )

    print("[SUCCESS] CosyVoice model ready")
    print(f"[INFO] checkpoint path: {COSYVOICE_MODEL_DIR}")


if __name__ == "__main__":
    main()
