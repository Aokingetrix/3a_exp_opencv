from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from deepface_ver.core import settings, utils
from deepface_ver.core.theme import load_theme
from deepface_ver.ui import drawing


class FloatingStub:
    def update(self):
        pass

    def draw(self, surface):
        pygame.draw.circle(surface, (20, 40, 60), (10, 10), 5)


def test_default_and_external_title_render():
    pygame.init()
    pygame.display.set_mode((1, 1))
    data_dir = Path(__file__).resolve().parents[1] / "data"
    for theme_dir in (None, data_dir / "themes" / "test-shapes"):
        theme = load_theme(data_dir / "theme.toml", theme_dir)
        settings.apply_theme(theme)
        surface = pygame.Surface((1280, 480))
        background = utils.create_background_surface(
            1280,
            480,
            settings.BACKGROUND_PATHS.get("title", settings.BACKGROUND_PATHS.get("default")),
        )
        rect = drawing.draw_title_screen(surface, background, [FloatingStub()])
        assert surface.get_size() == (1280, 480)
        assert surface.get_rect().contains(rect)
    pygame.quit()
