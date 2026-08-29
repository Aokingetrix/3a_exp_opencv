from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from deepface_ver.core import assets, settings, utils


@pytest.fixture(autouse=True)
def pygame_assets():
    pygame.init()
    pygame.display.set_mode((1, 1))
    assets.clear_asset_caches()
    yield
    assets.clear_asset_caches()
    pygame.quit()


def test_font_factory_runs_once_for_same_font(monkeypatch):
    original_font = pygame.font.Font
    calls = []

    def load_font(path, size):
        calls.append((path, size))
        return original_font(path, size)

    monkeypatch.setattr(pygame.font, "Font", load_font)

    fonts = [settings.get_font(24) for _ in range(100)]

    assert len(calls) == 1
    assert all(font is fonts[0] for font in fonts)


def test_contain_cache_separates_sizes_and_can_be_cleared(monkeypatch):
    image_path = Path(settings.EMOTION_IMAGE_PATHS["ニコニコ"])
    original_load = pygame.image.load
    original_scale = pygame.transform.scale
    load_calls = []
    scale_calls = []

    def load_image(path):
        load_calls.append(path)
        return original_load(path)

    def scale_image(surface, size):
        scale_calls.append(size)
        return original_scale(surface, size)

    monkeypatch.setattr(pygame.image, "load", load_image)
    monkeypatch.setattr(pygame.transform, "scale", scale_image)
    surface = pygame.Surface((320, 240))

    for _ in range(5):
        utils.render_image(surface, image_path, 0, 0, 100, 100)
    utils.render_image(surface, image_path, 0, 0, 120, 100)

    assert len(load_calls) == 1
    assert len(scale_calls) == 2

    assets.clear_asset_caches()
    utils.render_image(surface, image_path, 0, 0, 100, 100)
    assert len(load_calls) == 2
    assert len(scale_calls) == 3


def test_cover_cache_separates_sizes(monkeypatch):
    image_path = Path(settings.EMOTION_IMAGE_PATHS["ニコニコ"])
    original_load = pygame.image.load
    original_smoothscale = pygame.transform.smoothscale
    load_calls = []
    scale_calls = []

    def load_image(path):
        load_calls.append(path)
        return original_load(path)

    def scale_image(surface, size):
        scale_calls.append(size)
        return original_smoothscale(surface, size)

    monkeypatch.setattr(pygame.image, "load", load_image)
    monkeypatch.setattr(pygame.transform, "smoothscale", scale_image)

    for _ in range(5):
        utils.create_background_surface(320, 240, image_path)
    utils.create_background_surface(640, 480, image_path)

    assert len(load_calls) == 1
    assert len(scale_calls) == 2
