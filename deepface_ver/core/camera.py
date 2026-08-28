"""OpenCV camera backend selection without importing OpenCV at module load."""

from __future__ import annotations

import sys
from typing import Any


def backend_candidates(cv2: Any, requested: str) -> list[tuple[str, int | None]]:
    values = {
        "default": None,
        "dshow": getattr(cv2, "CAP_DSHOW", None),
        "msmf": getattr(cv2, "CAP_MSMF", None),
        "v4l2": getattr(cv2, "CAP_V4L2", None),
    }
    if requested != "auto":
        if requested not in values:
            raise ValueError(f"未対応のカメラバックエンドです: {requested}")
        return [(requested, values[requested])]
    order = ["dshow", "msmf", "default"] if sys.platform.startswith("win") else ["v4l2", "default"]
    result = []
    for name in order:
        api = values[name]
        if name == "default" or api is not None:
            result.append((name, api))
    return result
