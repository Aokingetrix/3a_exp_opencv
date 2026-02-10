import cv2
from deepface import DeepFace
import numpy as np
from typing import Any, Dict, List, Optional


def analyze_emotion_with_fallback(img, actions: Optional[List[str]] = None, backends: Optional[List[str]] = None, enforce_detection: bool = False) -> Dict[str, Any]:
    """
    DeepFace.analyze を複数の detector backend で順に試すユーティリティ。
    成功時は DeepFace の戻り値に 'detector_backend_used' を追加して返す。
    backends が None の場合は ['retinaface','mtcnn','opencv'] の順で試す。
    """
    if actions is None:
        actions = ["emotion"]
    if backends is None:
        backends = ["retinaface", "mtcnn", "opencv"]
    last_exc = None
    for backend in backends:
        try:
            result = DeepFace.analyze(img, actions=actions, detector_backend=backend, enforce_detection=enforce_detection)
            # DeepFace はバージョンにより dict または list を返す
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            # ここで辞書に統一する
            if isinstance(result, dict):
                result["detector_backend_used"] = backend
                return result
            # もし dict 以外が返ったら辞書化して返す（保険）
            return {"emotion": {}, "dominant_emotion": None, "region": None, "detector_backend_used": backend}
        except Exception as e:
            last_exc = e
            print(f"[emo_recog] backend {backend} failed: {e}")
    # last_exc が None の場合 raise None になるので避ける
    if last_exc is None:
        raise RuntimeError("No detector backends configured or no backends attempted")
    raise last_exc


class CameraManager_gpt:
    """カメラ映像取得担当"""
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
    """
    表情認識担当
    - 明るさが一定以下のときのみ補正
    - DeepFaceが苦手な感情を統合（安定化目的）
    """
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
        # 常に5カテゴリのキーが存在するように初期化
        self.last_result = {
            "top_emotion": "探し中...",
            "scores": self._get_empty_scores(),
            "box": None
        }

    def _adjust_brightness_conditionally(self, frame):
        """
        明るすぎる映像は補正しない。
        一定以下の明るさのみ補正することで白飛びを防止。
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)

        if mean_brightness < 150:
            frame = cv2.convertScaleAbs(frame, alpha=1.4, beta=30)
        return frame

    def _get_empty_scores(self):
        """ 5分類の空スコア辞書を返すヘルパー """
        return {
            "ムカムカ": 0,
            "ビックリ": 0,
            "ニコニコ": 0,
            "シクシク": 0,
            "シーン": 0
        }

    def _merge_emotions(self, raw_scores: Optional[Dict[str, float]]) -> Dict[str, int]:
        """
        DeepFaceの細分類を安定した5分類に統合。
        """
        merged = self._get_empty_scores()
        if not raw_scores:
            return merged

        # raw_scores のキーは文字列、値は数値であるはずだが、静的解析のため安全にキャストする
        for emo, score in (raw_scores or {}).items():
            key = emo if isinstance(emo, str) else str(emo)
            try:
                val = float(score)
            except Exception:
                # 数値に変換できなければ無視
                continue
            mapped = self.EMOTION_MERGE_MAP.get(key, "シーン") or "シーン"
            merged[mapped] = merged.get(mapped, 0) + int(val)
        return merged

    def analyze(self, frame):
        """
        フレームを解析して安定した5分類結果を返す。
        """
        if frame is None:
            return self.last_result, None 

        adjusted_frame = self._adjust_brightness_conditionally(frame)
        

        try:
            # フォールバックで検出器を順に試す（retinaface→mtcnn→opencv）
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