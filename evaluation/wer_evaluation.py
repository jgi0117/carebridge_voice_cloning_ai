from pathlib import Path
import whisper
from jiwer import wer


class WEREvaluator:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = whisper.load_model(model_name)

    def transcribe_audio(self, audio_path: str | Path) -> str:
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = self.model.transcribe(
            str(audio_path),
            language="ko",
        )

        return result["text"].strip()

    def calculate_wer(
        self,
        reference_text: str,
        generated_audio_path: str | Path,
    ) -> dict:
        transcribed_text = self.transcribe_audio(generated_audio_path)

        score = wer(
            reference_text,
            transcribed_text,
        )

        return {
            "reference_text": reference_text,
            "transcribed_text": transcribed_text,
            "wer": float(score),
        }