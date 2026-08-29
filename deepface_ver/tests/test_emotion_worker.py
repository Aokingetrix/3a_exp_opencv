from __future__ import annotations

import threading
import time

import pytest

pytest.importorskip("deepface")
np = pytest.importorskip("numpy")
emotion_module = pytest.importorskip("deepface_ver.emo.emo_recog")
EmotionRecognizer_gpt = emotion_module.EmotionRecognizer_gpt


def test_worker_processes_latest_pending_frame_without_throttling(monkeypatch):
    first_started = threading.Event()
    release_first = threading.Event()
    second_finished = threading.Event()
    processed = []

    def fake_process(self, frame):
        processed.append(int(frame[0, 0, 0]))
        if len(processed) == 1:
            first_started.set()
            assert release_first.wait(timeout=2)
        elif len(processed) == 2:
            second_finished.set()

    monkeypatch.setattr(EmotionRecognizer_gpt, "_process_frame", fake_process)
    recognizer = EmotionRecognizer_gpt()
    recognizer.start()
    try:
        recognizer.submit_frame(np.full((4, 4, 3), 1, dtype=np.uint8))
        assert first_started.wait(timeout=2)
        recognizer.submit_frame(np.full((4, 4, 3), 2, dtype=np.uint8))
        recognizer.submit_frame(np.full((4, 4, 3), 3, dtype=np.uint8))
        release_first.set()
        assert second_finished.wait(timeout=2)
        time.sleep(0.05)
    finally:
        release_first.set()
        recognizer.stop()

    assert processed == [1, 3]
