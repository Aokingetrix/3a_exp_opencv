"""Core package.

Submodules are intentionally not imported eagerly so rule and persistence tests
do not require the optional Pygame runtime.
"""

__all__ = ["assets", "game_manager", "highscore", "models", "settings", "utils"]
