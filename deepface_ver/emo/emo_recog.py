import cv2
import os
from deepface import DeepFace
import numpy as np
import threading
import time
from typing import Any, Dict, List, Optional


def analyze_emotion_with_fallback(img, actions: Optional[List[str]] = None, backends: Optional[List[str]] = None, enforce_detection: bool = False) -> Dict[str, Any]:
    if actions is None:
        actions = ["emotion"]
    if backends is None:
        backends = ["opencv"]
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
    """感情認識を別スレッドで非同期実行するクラス。

    ゲームループ側は submit_frame() でフレームを渡し、
    get_latest_result() で最新の認識結果を即座に（ブロックせずに）取得する。
    バックグラウンドスレッドが DeepFace.analyze を実行するため、
    ゲームループの FPS に影響しない。
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

    def __init__(self, scale_factor: float = 0.75, backend: str = "opencv"):
        """初期化。

        Args:
            scale_factor: 分析前にフレームを縮小する倍率 (0.25〜1.0)。
                          小さいほど高速だが精度が下がる。
            backend: DeepFace の detector_backend ("opencv", "mtcnn", "retinaface" 等)。
        """
        self._scale_factor = max(0.1, min(scale_factor, 1.0))
        self._backend = backend

        cv2_data = getattr(cv2, "data", None)
        cascade_base = getattr(cv2_data, "haarcascades", "") if cv2_data is not None else ""
        cascade_path = os.path.join(cascade_base, "haarcascade_frontalface_default.xml") if cascade_base else ""
        if not cascade_path or not os.path.exists(cascade_path):
            cascade_path = cv2.samples.findFile("haarcascade_frontalface_default.xml", required=False)
        self._face_cascade = cv2.CascadeClassifier(cascade_path)
        if self._face_cascade.empty():
            raise RuntimeError(f"顔検出モデルの読み込みに失敗: {cascade_path}")

        self._lock = threading.Lock()
        self._last_result = {
            "top_emotion": "探し中...",
            "scores": self._get_empty_scores(),
            "box": None
        }
        self._result_generation: int = 0  # 新しい結果が出るたびにインクリメント

        # ワーカースレッド用
        self._pending_frame = None  # メインスレッドから渡される最新フレーム
        self._new_frame_event = threading.Event()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ─── public API ───────────────────────────────────────

    def start(self):
        """バックグラウンドスレッドを開始する。"""
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        print("[emo_recog] 感情認識スレッド開始")

    def stop(self):
        """バックグラウンドスレッドを停止する。"""
        self._running = False
        self._new_frame_event.set()  # スレッドを起こして終了させる
        if self._thread:
            self._thread.join(timeout=3)
        print("[emo_recog] 感情認識スレッド停止")

    def submit_frame(self, frame):
        """分析対象のフレームを渡す（即座に返る）。

        前のフレームがまだ処理中なら上書きされる（最新1枚だけ保持）。
        """
        if frame is None:
            return
        with self._lock:
            self._pending_frame = frame.copy()
        self._new_frame_event.set()

    def get_latest_result(self):
        """最新の認識結果と世代番号を返す（即座に返る）。

        Returns:
            (result_dict, generation_int)
        """
        with self._lock:
            return self._last_result.copy(), self._result_generation

    # ─── 後方互換: 同期版 analyze (スレッド未使用時のフォールバック) ──

    def analyze(self, frame):
        """同期的に感情分析する (後方互換用)。スレッド利用時は使わない。"""
        if frame is None:
            with self._lock:
                return self._last_result.copy(), None
        self._process_frame(frame)
        with self._lock:
            return self._last_result.copy(), None

    # ─── internal ─────────────────────────────────────────

    def _worker_loop(self):
        """バックグラウンドで動くワーカー。新しいフレームが来たら処理する。"""
        while self._running:
            # 新しいフレームが来るまで待機（最大1秒でタイムアウト→ループ継続判定）
            self._new_frame_event.wait(timeout=1.0)
            self._new_frame_event.clear()

            if not self._running:
                break

            # 最新のフレームを取り出す
            with self._lock:
                frame = self._pending_frame
                self._pending_frame = None

            if frame is None:
                continue

            t0 = time.perf_counter()
            self._process_frame(frame)
            elapsed = time.perf_counter() - t0
            print(f"[emo_recog] 分析完了 {elapsed:.3f}秒 (backend={self._backend}, scale={self._scale_factor})")

    def _detect_face_region(self, frame):
        """OpenCV Haar Cascade で顔を検出し、最大の顔領域を返す。"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]
        min_side = min(h, w)
        min_size = max(24, int(min_side * 0.12))

        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(min_size, min_size),
        )

        if faces is None or len(faces) == 0:
            return None

        x, y, fw, fh = max(faces, key=lambda rect: int(rect[2]) * int(rect[3]))
        return {"x": int(x), "y": int(y), "w": int(fw), "h": int(fh)}

    def _process_frame(self, frame):
        """1枚のフレームを分析して last_result を更新する。"""
        adjusted = self._adjust_brightness_conditionally(frame)
        small = self._downscale(adjusted)
        small_h, small_w = small.shape[:2]
        detected_region = self._detect_face_region(small)

        if detected_region is None:
            new_result = {
                "top_emotion": "探し中...",
                "scores": self._get_empty_scores(),
                "box": None
            }
            with self._lock:
                self._last_result = new_result
                self._result_generation += 1
            return

        try:
            x = detected_region["x"]
            y = detected_region["y"]
            w = detected_region["w"]
            h = detected_region["h"]

            # 顔領域のみを切り出して感情分類（顔検出はskip）
            face_roi = small[y:y + h, x:x + w]
            if face_roi.size == 0:
                raise ValueError("empty face roi")

            result = DeepFace.analyze(
                face_roi,
                actions=["emotion"],
                detector_backend="skip",
                enforce_detection=False,
            )
            if isinstance(result, list) and len(result) > 0:
                result = result[0]

            if not isinstance(result, dict):
                raise ValueError("unexpected result from DeepFace.analyze")

            raw_emotions = result.get("emotion", {})
            merged_scores = self._merge_emotions(raw_emotions)

            top_raw = result.get("dominant_emotion", None)
            if isinstance(top_raw, str):
                top_merged = self.EMOTION_MERGE_MAP.get(top_raw, "シーン")
            else:
                top_merged = "シーン"

            region = detected_region
            if self._scale_factor < 1.0:
                inv = 1.0 / self._scale_factor
                region = {
                    "x": int(region["x"] * inv),
                    "y": int(region["y"] * inv),
                    "w": int(region["w"] * inv),
                    "h": int(region["h"] * inv),
                }

            # 枠が画面外にはみ出さないように丸める
            region["x"] = max(0, min(region["x"], frame.shape[1] - 1))
            region["y"] = max(0, min(region["y"], frame.shape[0] - 1))
            region["w"] = max(1, min(region["w"], frame.shape[1] - region["x"]))
            region["h"] = max(1, min(region["h"], frame.shape[0] - region["y"]))

            new_result = {
                "top_emotion": top_merged,
                "scores": merged_scores,
                "box": region
            }

        except Exception as e:
            print(f"[emo_recog] emotion analysis failed: {e}")
            new_result = {
                "top_emotion": "探し中...",
                "scores": self._get_empty_scores(),
                "box": None
            }

        with self._lock:
            self._last_result = new_result
            self._result_generation += 1

    def _downscale(self, frame):
        """フレームを scale_factor 倍に縮小する。"""
        if self._scale_factor >= 1.0:
            return frame
        h, w = frame.shape[:2]
        new_w = max(1, int(w * self._scale_factor))
        new_h = max(1, int(h * self._scale_factor))
        return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

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
