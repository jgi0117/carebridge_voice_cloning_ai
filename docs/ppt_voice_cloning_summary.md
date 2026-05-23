# Voice Cloning 기반 사회복지 음성 안내 서비스

## 1. 문제 제기와 해결 방안

### 문제 제기

고령자와 요양보호 대상자는 복약, 식사, 병원 방문, 건강 확인 등 반복적인 안내가 필요하다. 하지만 일반적인 앱 알림음이나 기계적인 TTS 음성은 정서적 친밀감이 낮고, 어르신이 알림을 무심코 지나치거나 부담스럽게 느낄 수 있다.

특히 복약 안내처럼 꾸준한 행동 유도가 필요한 상황에서는 단순 정보 전달뿐 아니라 신뢰감과 정서적 안정감이 중요하다. 보호자나 가족의 목소리로 안내가 제공된다면 어르신은 더 익숙하고 편안하게 알림을 받아들일 수 있다.

### 해결 방안

본 프로젝트는 보호자 음성을 등록하고, 해당 음성 특성을 기반으로 복약 안내 문장을 생성하는 Voice Cloning 기반 음성 안내 구조를 제안한다.

서비스 흐름은 다음과 같다.

1. 보호자 음성 파일과 실제 발화 transcript를 등록한다.
2. 서버는 이를 voice profile로 저장한다.
3. 복약 시간, 식사 후 안내, 건강 확인 등 필요한 안내 문장을 생성 요청한다.
4. CosyVoice 모델이 보호자 음성 특성을 반영한 안내 음성을 생성한다.
5. 앱은 생성된 음성 파일을 알림 시간에 재생한다.

이 방식은 모든 알림을 실시간으로 합성하지 않고, 복약 일정 등록 시점이나 알림 전에 미리 음성을 생성해 저장할 수 있어 실제 서비스 적용 가능성이 높다.

---

## 2. 활용 모델과 음성 제작 Flow

### 활용 모델: CosyVoice

본 프로젝트에서는 다국어 음성 생성 및 zero-shot voice cloning이 가능한 CosyVoice 기반 구조를 활용하였다. CosyVoice는 reference 음성과 해당 음성의 transcript를 prompt로 사용해, 새로운 문장을 특정 화자 스타일로 생성하는 방식의 TTS(Text-to-Speech) 모델이다. 이를 통해 화자의 음색, 말투, 억양 등의 특징을 비교적 자연스럽게 반영할 수 있다.

또한 CosyVoice는 Apache License 2.0 기반의 오픈소스 프로젝트로 공개되어 있어, 연구 및 상업적 활용이 비교적 자유로운 편이다. 다만 라이선스 고지 및 저작권 표기 유지 등의 조건을 준수해야 한다.

### 음성 제작 Flow

```text
보호자 음성 등록
  reference.wav
  prompt_text
  guardian_id
  elder_id
        |
        v
Voice Profile 저장
  data/reference_voices/profiles/{voice_profile_id}/
    reference.wav
    metadata.json
        |
        v
복약 안내 생성 요청
  voice_profile_id
  text
  notification_type
        |
        v
CosyVoice inference_zero_shot()
        |
        v
생성 음성 저장
  data/outputs/{elder_id}/{notification_type}/...
        |
        v
앱에서 알림 음성 재생
```

---

## 3. Register 3명을 통한 실제 예

### Voice Profile 구조

PPT 데모를 위해 `register1`, `register2`, `register3` 세 개의 voice profile을 구성했다.

```text
data/reference_voices/profiles/
  register1/
    reference.wav
    metadata.json
  register2/
    reference.wav
    metadata.json
  register3/
    reference.wav
    metadata.json
```

각 `metadata.json`에는 다음 정보가 포함된다.

```json
{
  "voice_profile_id": "register1",
  "guardian_id": "guardian_001",
  "elder_id": "elder_001",
  "reference_audio_path": ".../reference.wav",
  "prompt_text": "보호자가 reference.wav에서 실제로 말한 문장",
  "consent": true
}
```

### 실제 생성 예시

복약 안내 문장 예시는 다음과 같다.

```text
어머님, 점심 식사는 잘 하셨나요.
이제 식후 약을 챙겨 드실 시간이에요.
약을 드신 뒤에는 잠시 앉아서 쉬시고, 복용을 마치면 앱에서 확인 버튼을 눌러 주세요.
```

생성된 음성은 다음 경로 구조로 저장된다.

```text
data/outputs/elder_001/medication/register1_*.wav
data/outputs/elder_002/medication/register2_*.wav
data/outputs/elder_003/medication/register3_*.wav
```

### 평가 결과

현재 세 voice profile에 대한 평가 결과는 다음과 같다.

| elder_id | voice_profile_id | speaker similarity | WER |
|---|---|---:|---:|
| elder_001 | register1 | 0.6827 | 0.8000 |
| elder_002 | register2 | 0.8713 | 0.4583 |
| elder_003 | register3 | 0.8738 | 0.3333 |

Speaker similarity는 기준 음성과 생성 음성의 화자 유사도를 cosine similarity로 측정한 값이다. OpenVoice 기반 실험에서 약 0.2387 수준이었던 것에 비해, CosyVoice 전환 후 register2, register3에서는 0.87 수준까지 향상되었다.

WER은 Whisper 기반 자동 음성 인식 결과와 원문을 비교한 값이다. 한국어의 띄어쓰기, 복합명사, Whisper 인식 오류에 민감하기 때문에 음성 품질 자체를 단독으로 판단하기보다는 참고 지표로 보는 것이 적절하다.

---

## 4. 한계점과 실시간 대화형 발전 방향

### 현재 한계점

현재 구조는 복약 알림처럼 미리 정해진 안내 문장을 생성하는 용도에는 적합하지만, 완전한 실시간 대화형 음성 서비스에는 한계가 있다.

주요 한계는 다음과 같다.

1. 생성 시간이 길다.
   CPU 환경에서는 몇 초 길이의 음성을 생성하는 데 1분 이상 걸릴 수 있다.

2. 요청마다 reference 음성과 prompt text를 조건으로 사용한다.
   voice profile은 저장되어 있지만, 음성을 만들 때마다 모델 inference가 필요하다.

3. 실시간 스트리밍 구조가 아니다.
   현재는 전체 wav 파일을 생성한 뒤 저장하고, 이후 앱에서 재생하는 방식이다.

4. WER 평가가 한국어 음성 품질을 완벽하게 반영하지 못한다.
   짧은 문장에서는 일부 단어 오류만으로 WER이 크게 상승할 수 있다.

### 현재 서비스에 적합한 운영 방식

복약 알림 서비스에서는 실시간 합성보다 사전 생성 방식이 더 현실적이다.

```text
복약 일정 등록 또는 수정
        |
        v
필요한 안내 문장 미리 생성
        |
        v
wav/mp3 파일 저장
        |
        v
알림 시간에 저장된 음성 재생
```

이 구조는 생성 시간이 길어도 사용자 경험에 영향을 덜 주며, 자주 쓰는 문장을 캐싱할 수 있다.

### 실시간 대화형으로 발전하기 위해 필요한 것

실시간 대화형 보호자 음성 AI로 발전하려면 다음 요소가 필요하다.

1. GPU 기반 inference 서버
   CPU 환경에서는 실시간 응답이 어렵기 때문에 GPU 서버가 필요하다.

2. 모델 상시 로딩
   현재처럼 요청마다 모델을 로드하지 않고, FastAPI 서버 시작 시 모델을 한 번만 로드한 뒤 재사용해야 한다.

3. 스트리밍 TTS 지원
   전체 음성을 만든 뒤 반환하는 방식이 아니라, 생성되는 음성을 chunk 단위로 앱에 전달해야 한다.

4. 짧은 문장 단위 응답
   긴 문장을 한 번에 생성하지 않고 문장 단위로 나눠 먼저 재생해야 체감 지연을 줄일 수 있다.

5. 캐싱 전략
   “약 드실 시간이에요”, “확인 버튼을 눌러 주세요”처럼 자주 쓰는 문장은 미리 생성해 저장하는 방식이 필요하다.

6. 모델 교체 또는 최적화 검토
   완전한 실시간 대화형 서비스를 목표로 한다면 CosyVoice를 최적화하거나, 스트리밍에 더 적합한 TTS 모델 또는 상용 API를 검토해야 한다.

### 결론

현재 단계에서는 CosyVoice 기반 voice cloning을 통해 보호자 음성 복약 안내를 구현할 수 있음을 확인했다. 실시간 대화형 서비스보다는, 사회복지 앱에서 필요한 복약/식사/건강 안내 음성을 사전에 생성해 제공하는 방식이 현실적인 1차 적용 방향이다.

향후에는 GPU 기반 inference, 모델 상시 로딩, 스트리밍 TTS, 캐싱 구조를 추가해 반실시간 또는 실시간 대화형 음성 서비스로 확장할 수 있다.
