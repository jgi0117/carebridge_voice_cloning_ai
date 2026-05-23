# CareBridge Voice Cloning AI

CareBridge Voice Cloning AI는 시니어 케어 서비스 CareBridge의 개인화 음성 생성 모듈입니다. 등록된 기준 음성을 바탕으로 한국어 안내 및 알림 음성을 생성해, 복약 알림이나 생활 안내가 사용자에게 더 익숙하고 정서적으로 편안하게 전달되도록 돕습니다.

이 저장소에는 CareBridge 연동 코드, API 계층, 평가 도구, 프로젝트 문서만 포함합니다. 음성 녹음 파일, 생성 음성, 모델 체크포인트, 외부 음성 합성 엔진 저장소, 로컬 가상환경은 저장소에 포함하지 않습니다.

## 주요 기능

이 모듈은 기준 음성 프로필을 관리하고, 텍스트를 입력받아 알림 음성을 생성합니다. 현재 CosyVoice 기반 생성 경로를 중심으로 사용하며, 실험 및 호환성을 위해 OpenVoice 서비스 구현도 함께 유지합니다.

핵심 기능은 다음과 같습니다.

- 로컬 음성 프로필 등록 및 관리
- 기준 음성 사용 동의 메타데이터 저장
- 한국어 텍스트 기반 cloned TTS 음성 생성
- FastAPI 기반 음성 생성 API 제공
- speaker similarity 및 WER 기반 생성 음성 평가

## 동작 방식

1. 보호자 또는 사용자의 기준 음성 샘플을 `data/reference_voices/` 아래에 등록합니다.
2. 음성 프로필 메타데이터를 `data/reference_voices/profiles/` 아래에 저장합니다.
3. TTS 요청에서 사용할 음성 프로필과 생성할 텍스트를 선택합니다.
4. 서비스가 CosyVoice 등 로컬 voice cloning 엔진을 로드합니다.
5. 엔진이 등록된 기준 음성을 조건으로 음성을 생성합니다.
6. 생성된 `.wav` 파일을 `data/outputs/` 아래에 저장합니다.
7. 선택적으로 평가 스크립트가 기준 음성 및 원문 텍스트와 생성 음성을 비교합니다.

이 저장소에는 외부 CosyVoice/OpenVoice 소스 트리와 모델 체크포인트가 포함되지 않습니다. 실제 실행 시에는 로컬 환경에 별도로 준비해야 합니다.

## 프로젝트 구조

```text
app/
  main.py                         FastAPI 진입점
  config.py                       로컬 경로 및 실행 디렉터리 설정
  api/
    voice_router.py               TTS 생성 endpoint
    voice_profile_router.py       음성 프로필 endpoint
  schemas/
    voice_schema.py               요청 및 응답 schema
  services/
    audio_service.py              오디오 파일 유틸리티
    consent_service.py            동의 메타데이터 관리
    cosyvoice_service.py          CosyVoice 생성 adapter
    openvoice_service.py          OpenVoice 생성 adapter
    voice_profile_service.py      음성 프로필 메타데이터 로직
  utils/
    file_utils.py                 공통 파일 유틸리티
evaluation/
  speaker_similarity.py           ECAPA speaker similarity 평가
  wer_evaluation.py               Whisper + jiwer 기반 WER 평가
scripts/
  download_model.py               모델 다운로드 보조 스크립트
  preprocess_audio.py             기준 음성 전처리
  register_demo_profiles.py       데모 프로필 등록
  test_clone.py                   로컬 생성 테스트
  export_evaluation_results.py    평가 결과 export
docs/
  ppt_voice_cloning_summary.md
requirements.txt
```

## 환경 설정

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

로컬 음성 생성을 위해서는 외부 엔진 자산도 준비해야 합니다.

```text
CosyVoice/                         외부 CosyVoice 저장소
checkpoints/cosyvoice/CosyVoice2-0.5B/
```

OpenVoice 지원을 사용하려면 다음 경로가 필요합니다.

```text
OpenVoice/                         외부 OpenVoice 저장소
checkpoints/openvoice/checkpoints_v2/
```

위 디렉터리들은 외부 코드, 모델 파일, 대형 실행 자산을 포함하므로 Git에서 제외합니다.

## API 실행

```powershell
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 로컬 사용 예시

데모 음성 프로필 등록:

```powershell
python scripts\register_demo_profiles.py
```

테스트 음성 생성:

```powershell
python scripts\test_clone.py
```

기준 음성 전처리:

```powershell
python scripts\preprocess_audio.py
```

## 저장소 정책

다음 항목은 의도적으로 Git에 포함하지 않습니다.

- 기준 음성 녹음 파일
- 생성된 음성 출력 파일
- 동의 기록 및 로컬 프로필 데이터
- 모델 체크포인트 및 다운로드된 모델 자산
- `CosyVoice/`, `OpenVoice/` 등 외부 엔진 저장소
- 캐시 디렉터리와 로컬 가상환경
- 평가 결과 CSV 파일

## 안전 및 개인정보 유의사항

Voice cloning은 음성 생체정보와 신원 오용 위험을 동반할 수 있습니다. 실제 서비스 적용 시에는 명시적 동의, 삭제 요청 처리, 접근 제어, 감사 로그, 사칭 및 악의적 문장 생성을 막기 위한 안전장치가 필요합니다.

## 라이선스

이 프로젝트는 Apache License 2.0을 따릅니다. 자세한 내용은 `LICENSE`와 `NOTICE`를 참고하세요.
