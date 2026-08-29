def test_imports():
    import pytest

    from deepface_ver.core import utils
    from deepface_ver.scripts import main as scripts_main
    from deepface_ver.ui import drawing

    assert hasattr(utils, "draw_text")
    assert hasattr(drawing, "draw_title_screen")
    assert hasattr(scripts_main, "main")

    pytest.importorskip("cv2")
    pytest.importorskip("deepface")
    from deepface_ver.emo import emo_recog

    assert hasattr(emo_recog, "EmotionRecognizer_gpt")
