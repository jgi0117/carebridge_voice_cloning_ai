from pathlib import Path

import librosa
import numpy as np

import torch
import torch.nn.functional as F

from speechbrain.inference.speaker import EncoderClassifier


class SpeakerSimilarityEvaluator:

    def __init__(self, device: str | None = None):

        self.device = device or (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="checkpoints/speaker_similarity_ecapa",
            run_opts={"device": self.device},
        )

    def load_audio(self, audio_path: str | Path):

        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        waveform, sample_rate = librosa.load(
            str(audio_path),
            sr=16000,
            mono=True,
        )

        waveform = np.expand_dims(
            waveform,
            axis=0,
        )

        waveform = torch.tensor(
            waveform,
            dtype=torch.float32,
        ).to(self.device)

        return waveform

    def get_embedding(
        self,
        audio_path: str | Path,
    ):

        waveform = self.load_audio(
            audio_path
        )

        with torch.no_grad():

            embedding = self.classifier.encode_batch(
                waveform
            )

        return embedding.squeeze(0)

    def calculate_similarity(
        self,
        reference_audio_path: str | Path,
        generated_audio_path: str | Path,
    ) -> float:

        reference_embedding = self.get_embedding(
            reference_audio_path
        )

        generated_embedding = self.get_embedding(
            generated_audio_path
        )

        similarity = F.cosine_similarity(
            reference_embedding,
            generated_embedding,
            dim=-1,
        ).mean()

        return float(
            similarity.detach().cpu().item()
        )