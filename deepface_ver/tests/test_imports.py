def test_imports():
    import importlib
    import deepface_ver
    from deepface_ver.core import settings, utils, game_manager
    from deepface_ver.ui import drawing, ui_elements
    from deepface_ver.emo import emo_recog
    from deepface_ver.scripts import main as scripts_main
    assert hasattr(utils, 'draw_text')
    assert hasattr(drawing, 'draw_title_screen')
    assert hasattr(emo_recog, 'EmotionRecognizer_gpt')
    assert hasattr(scripts_main, 'main')
