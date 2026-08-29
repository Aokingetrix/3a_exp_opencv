"""Shared value objects used by the game core and adapters."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GameCommand:
    """Semantic input for one game-loop tick."""

    start: bool = False
    cancel: bool = False
    skip: bool = False
    restart: bool = False
    debug_easy: bool = False
    debug_normal: bool = False
    debug_hard: bool = False


@dataclass(frozen=True)
class RoundOutcome:
    """Immutable result of judging one round."""

    code: str
    score_change: int
    life_change: int
    message: str


@dataclass(frozen=True)
class RecognitionResult:
    """Normalized result returned by the asynchronous recognizer."""

    top_emotion: str = "探し中..."
    scores: Mapping[str, int] = field(default_factory=dict)
    box: Mapping[str, int] | None = None
    status: str = "init"
    reason: str = "初期化中"
    face_detected: bool = False
    emotion_success: bool = False
    latency_ms: float = 0.0
    detector: str = "opencv_haar"
    classifier: str = "deepface_emotion_skip"

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> RecognitionResult:
        return cls(
            top_emotion=str(value.get("top_emotion", "探し中...")),
            scores=dict(value.get("scores", {})),
            box=value.get("box"),
            status=str(value.get("status", "init")),
            reason=str(value.get("reason", "")),
            face_detected=bool(value.get("face_detected", False)),
            emotion_success=bool(value.get("emotion_success", False)),
            latency_ms=float(value.get("latency_ms", 0.0)),
            detector=str(value.get("detector", "opencv_haar")),
            classifier=str(value.get("classifier", "deepface_emotion_skip")),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "top_emotion": self.top_emotion,
            "scores": dict(self.scores),
            "box": self.box,
            "status": self.status,
            "reason": self.reason,
            "face_detected": self.face_detected,
            "emotion_success": self.emotion_success,
            "latency_ms": self.latency_ms,
            "detector": self.detector,
            "classifier": self.classifier,
        }
