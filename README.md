# CareBridge Voice Cloning AI

CareBridge Voice Cloning AI is the personalized voice generation module for the CareBridge senior care service. It creates Korean guidance or notification audio using a registered reference voice, so reminders can sound familiar and emotionally supportive for senior users.

This repository contains the CareBridge integration code, API layer, evaluation helpers, and project documentation. Voice recordings, generated audio, model checkpoints, external engine repositories, and local virtual environments are intentionally excluded.

## What It Does

The module manages reference voice profiles and generates notification speech from text. It currently supports a CosyVoice-based generation path and keeps an OpenVoice service implementation for compatibility and experimentation.

Core capabilities:

- register and manage local voice profiles
- store consent metadata for reference voice usage
- generate cloned Korean TTS audio from text
- expose voice generation through FastAPI
- evaluate generated audio with speaker similarity and WER helpers

## Mechanism

1. A caregiver or user registers a reference voice sample under `data/reference_voices/`.
2. Voice profile metadata is stored locally under `data/reference_voices/profiles/`.
3. A TTS request selects a voice profile and target text.
4. The service loads a local voice cloning engine such as CosyVoice.
5. The engine conditions generation on the registered reference audio.
6. Generated `.wav` files are written to `data/outputs/`.
7. Optional evaluation scripts compare generated speech against reference audio and text.

The repository does not include the external CosyVoice/OpenVoice source trees or model checkpoints. They should be installed locally when running the service.

## Project Structure

```text
app/
  main.py                         FastAPI entry point
  config.py                       Local path and runtime directory config
  api/
    voice_router.py               TTS generation endpoints
    voice_profile_router.py       Voice profile endpoints
  schemas/
    voice_schema.py               Request and response schemas
  services/
    audio_service.py              Audio file helpers
    consent_service.py            Consent metadata helpers
    cosyvoice_service.py          CosyVoice generation adapter
    openvoice_service.py          OpenVoice generation adapter
    voice_profile_service.py      Voice profile metadata logic
  utils/
    file_utils.py                 Shared file utilities
evaluation/
  speaker_similarity.py           ECAPA speaker similarity evaluator
  wer_evaluation.py               Whisper + jiwer WER evaluator
scripts/
  download_model.py               Model download helper
  preprocess_audio.py             Reference audio preprocessing
  register_demo_profiles.py       Demo profile registration
  test_clone.py                   Local generation smoke test
  export_evaluation_results.py    Evaluation export helper
docs/
  ppt_voice_cloning_summary.md
requirements.txt
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For local generation, also prepare the external engine assets:

```text
CosyVoice/                         external CosyVoice repository
checkpoints/cosyvoice/CosyVoice2-0.5B/
```

OpenVoice support expects:

```text
OpenVoice/                         external OpenVoice repository
checkpoints/openvoice/checkpoints_v2/
```

These directories are ignored by Git because they contain external code, model files, or large runtime assets.

## Run API

```powershell
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Local Usage

Register demo voice profiles:

```powershell
python scripts\register_demo_profiles.py
```

Generate a test cloned voice sample:

```powershell
python scripts\test_clone.py
```

Preprocess a reference audio file:

```powershell
python scripts\preprocess_audio.py
```

## Repository Policy

The following artifacts are intentionally not tracked:

- reference voice recordings
- generated voice outputs
- consent records and local profile data
- model checkpoints and downloaded model assets
- external engine repositories such as `CosyVoice/` and `OpenVoice/`
- cache directories and local virtual environments
- evaluation result CSV files

## Safety Notes

Voice cloning can create sensitive biometric and identity-related risks. Production use should require explicit consent, clear deletion flows, access control, audit logging, and safeguards against impersonation or abusive text generation.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
