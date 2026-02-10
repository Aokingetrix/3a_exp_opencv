# compatibility alias: ensure this module name refers to the canonical module object
import importlib, sys
sys.modules[__name__] = importlib.import_module("deepface_ver.emo.emo_recog")