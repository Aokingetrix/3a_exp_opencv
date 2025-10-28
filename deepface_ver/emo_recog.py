import cv2
from deepface import DeepFace
import numpy as np


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

    def _merge_emotions(self, raw_scores):
        """
        DeepFaceの細分類を安定した5分類に統合。
        """
        merged = self._get_empty_scores()
        if not raw_scores:
            return merged
            
        for emo, score in raw_scores.items():
            mapped = self.EMOTION_MERGE_MAP.get(emo, "シーン")
            merged[mapped] = merged.get(mapped, 0) + score
        return merged

    def analyze(self, frame):
        """
        フレームを解析して安定した5分類結果を返す。
        """
        if frame is None:
            return self.last_result, None 

        adjusted_frame = self._adjust_brightness_conditionally(frame)
        

        try:
            result = DeepFace.analyze(
                adjusted_frame, 
                actions=["emotion"], 
                enforce_detection=True, # 検出失敗時に例外を発生させる
                detector_backend='opencv'
            )
            
            if isinstance(result, list):
                result = result[0]

            raw_emotions = result["emotion"]
            merged_scores = self._merge_emotions(raw_emotions)

            top_raw = result["dominant_emotion"]
            top_merged = self.EMOTION_MERGE_MAP.get(top_raw, "neutral")

            self.last_result = {
                "top_emotion": top_merged,
                "scores": merged_scores,
                "box": result.get("region", None)
            }

        except Exception:
            self.last_result = {
                "top_emotion": "探し中...",
                "scores": self._get_empty_scores(), 
                "box": None
            }

        return self.last_result, adjusted_frame