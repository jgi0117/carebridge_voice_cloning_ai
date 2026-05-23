from pathlib import Path

# =========================================================
# Base Directory
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# Data Directories
# =========================================================

DATA_DIR = BASE_DIR / "data"

REFERENCE_VOICE_DIR = DATA_DIR / "reference_voices"
VOICE_PROFILE_DIR = REFERENCE_VOICE_DIR / "profiles"
OUTPUT_DIR = DATA_DIR / "outputs"
CONSENT_DIR = DATA_DIR / "consent"

# =========================================================
# Model / Checkpoint Directories
# =========================================================

CHECKPOINT_DIR = BASE_DIR / "checkpoints"

OPENVOICE_REPO_DIR = BASE_DIR / "OpenVoice"
OPENVOICE_CHECKPOINT_DIR = CHECKPOINT_DIR / "openvoice"
OPENVOICE_CHECKPOINT_V2_DIR = OPENVOICE_CHECKPOINT_DIR / "checkpoints_v2"

COSYVOICE_REPO_DIR = BASE_DIR / "CosyVoice"
COSYVOICE_CHECKPOINT_DIR = CHECKPOINT_DIR / "cosyvoice"
COSYVOICE_MODEL_DIR = COSYVOICE_CHECKPOINT_DIR / "CosyVoice2-0.5B"

# =========================================================
# Evaluation Directories
# =========================================================

EVALUATION_DIR = BASE_DIR / "evaluation"
EVALUATION_RESULT_DIR = EVALUATION_DIR / "results"

# =========================================================
# Default Settings
# =========================================================

DEFAULT_LANGUAGE = "ko"
DEFAULT_OUTPUT_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 24000

# =========================================================
# Directory Initialization
# =========================================================

def create_directories():
    directories = [
        DATA_DIR,
        REFERENCE_VOICE_DIR,
        VOICE_PROFILE_DIR,
        OUTPUT_DIR,
        CONSENT_DIR,
        CHECKPOINT_DIR,
        OPENVOICE_CHECKPOINT_DIR,
        OPENVOICE_CHECKPOINT_V2_DIR,
        COSYVOICE_CHECKPOINT_DIR,
        EVALUATION_DIR,
        EVALUATION_RESULT_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


create_directories()
