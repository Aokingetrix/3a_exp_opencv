"""Stable command-line entry point for the game."""

from __future__ import annotations

import sys


def main() -> int:
    from ..application import main as run_application

    return run_application()


if __name__ == "__main__":
    sys.exit(main())
