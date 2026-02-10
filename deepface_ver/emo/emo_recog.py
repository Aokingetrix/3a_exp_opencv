import cv2
from deepface import DeepFace
import numpy as np
from typing import Any, Dict, List, Optional


def analyze_emotion_with_fallback(img, actions: Optional[List[str]] = None, backends: Optional[List[str]] = None, enforce_detection: bool = False) -> Dict[str, Any]:
    if actions is None:
        actions = ["emotion"]
    if backends is None:
        backends = ["retinaface", "mtcnn", "opencv"]
    last_exc = None
    for backend in backends:
        try:
            result = DeepFace.analyze(img, actions=actions, detector_backend=backend, enforce_detection=enforce_detection)
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            if isinstance(result, dict):
                result["detector_backend_used"] = backend
                return result
            return {"emotion": {}, "dominant_emotion": None, "region": None, "detector_backend_used": backend}
        except Exception as e:
            last_exc = e
            print(f"[emo_recog] backend {backend} failed: {e}")
    if last_exc is None:
        raise RuntimeError("No detector backends configured or no backends attempted")
    raise last_exc


class CameraManager_gpt:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            raise RuntimeError("カメラを開けません。")

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        self.cap.release()


class EmotionRecognizer_gpt:
    EMOTION_MERGE_MAP = {
        "angry": "ムカムカ",
        "disgust": "ムカムカ",
        "fear": "ビックリ",
        "surprise": "ビックリ",
        "happy": "ニコニコ",
        "sad": "シクシク",
        "neutral": "シーン"
    }

    def __init__(self):
        self.last_result = {
            "top_emotion": "探し中...",
            "scores": self._get_empty_scores(),
            "box": None
        }

    def _adjust_brightness_conditionally(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)

        if mean_brightness < 150:
            frame = cv2.convertScaleAbs(frame, alpha=1.4, beta=30)
        return frame

    def _get_empty_scores(self):
        return {
            "ムカムカ": 0,
            "ビックリ": 0,
            "ニコニコ": 0,
            "シクシク": 0,
            "シーン": 0
        }

    def _merge_emotions(self, raw_scores: Optional[Dict[str, float]]) -> Dict[str, int]:
        merged = self._get_empty_scores()
        if not raw_scores:
            return merged
        for emo, score in (raw_scores or {}).items():
            key = emo if isinstance(emo, str) else str(emo)
            try:
                val = float(score)
            except Exception:
                continue
            mapped = self.EMOTION_MERGE_MAP.get(key, "シーン") or "シーン"
            merged[mapped] = merged.get(mapped, 0) + int(val)
        return merged

    def analyze(self, frame):
        if frame is None:
            return self.last_result, None

        adjusted_frame = self._adjust_brightness_conditionally(frame)
        try:
            result = analyze_emotion_with_fallback(
                adjusted_frame,
                actions=["emotion"],
                backends=["retinaface", "mtcnn", "opencv"],
                enforce_detection=False,
            )

            raw_emotions = result.get("emotion", {})
            merged_scores = self._merge_emotions(raw_emotions)

            top_raw = result.get("dominant_emotion", None)
            if isinstance(top_raw, str):
                top_merged = self.EMOTION_MERGE_MAP.get(top_raw, "シーン")
            else:
                top_merged = "シーン"

            self.last_result = {
                "top_emotion": top_merged,
                "scores": merged_scores,
                "box": result.get("region", None)
            }

        except Exception as e:
            print(f"[emo_recog] emotion analysis failed: {e}")
            self.last_result = {
                "top_emotion": "探し中...",
                "scores": self._get_empty_scores(), 
                "box": None
            }

        return self.last_result, adjusted_frame
