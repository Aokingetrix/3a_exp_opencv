"""Stable command-line entry point for the game."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ..core.runtime import RuntimeOptions, parse_size


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Webカメラ表情認識 あまのじゃくゲーム")
    parser.add_argument("--camera-index", type=int, default=0, help="使用するカメラ番号")
    parser.add_argument(
        "--camera-backend",
        choices=("auto", "dshow", "msmf", "v4l2", "default"),
        default="auto",
        help="OpenCVのカメラバックエンド",
    )
    parser.add_argument(
        "--window-size",
        default="1280x480",
        metavar="WIDTHxHEIGHT",
        help="物理ウィンドウサイズ（論理解像度は1280x480）",
    )
    parser.add_argument(
        "--theme-dir",
        type=Path,
        default=None,
        help="theme.tomlを含む外部テーマディレクトリ",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        window_size = parse_size(args.window_size)
    except ValueError as error:
        parser.error(str(error))
    theme_dir = args.theme_dir
    if theme_dir is None and os.environ.get("AMANOJAKU_THEME_DIR"):
        theme_dir = Path(os.environ["AMANOJAKU_THEME_DIR"])

    from ..application import main as run_application

    return run_application(
        RuntimeOptions(
            camera_index=args.camera_index,
            camera_backend=args.camera_backend,
            window_size=window_size,
            theme_dir=theme_dir,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
