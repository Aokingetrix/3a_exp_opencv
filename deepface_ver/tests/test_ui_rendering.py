from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from deepface_ver.core import assets, settings, utils
from deepface_ver.core.game_manager import GameManager
from deepface_ver.core.theme import load_theme
from deepface_ver.ui import drawing
from deepface_ver.ui.screens import gameplay as gameplay_screen
from deepface_ver.ui.ui_elements import LifeDisplay, Timer


class FloatingStub:
    def update(self):
        pass

    def draw(self, surface):
        pygame.draw.circle(surface, (20, 40, 60), (10, 10), 5)


class SilentSound:
    def play(self):
        pass


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
        for _ in range(3):
            rect = drawing.draw_title_screen(surface, background, [FloatingStub()])
        assert surface.get_size() == (1280, 480)
        assert surface.get_rect().contains(rect)
    assets.clear_asset_caches()
    pygame.quit()


def test_game_screens_render_repeatedly_with_cached_assets(monkeypatch):
    pygame.init()
    pygame.display.set_mode((1, 1))
    assets.clear_asset_caches()
    data_dir = Path(__file__).resolve().parents[1] / "data"
    settings.apply_theme(load_theme(data_dir / "theme.toml"))

    surface = pygame.Surface((1280, 480))
    background = utils.create_background_surface(1280, 480)
    sounds = {name: SilentSound() for name in ("count", "success", "fail")}
    game = GameManager(1280, 480, sounds)
    game.npc_emotions = ["ニコニコ", "シクシク", "ムカムカ"]
    game.player_emotion = "ビックリ"
    game.last_round_outcome = "success"
    game.current_round = 1
    game.timer_sec = 2.5
    game.personal_best_list = [100]

    timer = Timer(
        surface,
        (250, 10),
        settings.CLOCK_IMAGE_PATH,
        settings.FONT_PATH,
        40,
        settings.TEXT_DARK,
        settings.WII_TRANSLUCENT_BG,
        settings.WII_SHADOW_COLOR,
    )
    lives = LifeDisplay(surface, settings.HEART_IMAGE_PATH, 60, (0, 0), max_lives=3)
    monkeypatch.setattr(gameplay_screen, "render_frame", lambda *args, **kwargs: None)
    frame = object()
    result = {"box": None}

    for _ in range(3):
        drawing.draw_emotion_map_screen(surface, background, game, 1280, 480)
        drawing.draw_game_background(surface, background, frame, result, "シーン", 640)
        drawing.draw_playing_screen(surface, game, timer, 640, 480)
        drawing.draw_common_ui(surface, game, 640, 480, lives)
        drawing.draw_result_screen(surface, game, 640, 480)
        drawing.draw_finish_screen(surface, background, game, 1280, 480)
        drawing.draw_finish_highscores(surface, 1280, game)

    assert surface.get_size() == (1280, 480)
    assets.clear_asset_caches()
    pygame.quit()
