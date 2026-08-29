"""Cached Pygame assets shared by all screens.

Assets are immutable after the theme is selected at startup. Keeping decoded
images, scaled variants, and fonts here prevents disk I/O in the frame loop.
"""

from __future__ import annotations

from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

import pygame


def _normalized_path(path: str | Path) -> str:
    return str(Path(path).resolve())


@lru_cache(maxsize=32)
def _load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()


@lru_cache(maxsize=64)
def _contain_image(path: str, width: int, height: int) -> tuple[pygame.Surface, int, int]:
    image = _load_image(path)
    image_width, image_height = image.get_size()
    if image_width <= 0 or image_height <= 0:
        raise pygame.error(f"画像サイズが0です: {path}")

    image_aspect = image_width / image_height
    area_aspect = width / height
    if image_aspect > area_aspect:
        scaled_width = width
        scaled_height = max(1, int(scaled_width / image_aspect))
    else:
        scaled_height = height
        scaled_width = max(1, int(scaled_height * image_aspect))

    scaled = pygame.transform.scale(image, (scaled_width, scaled_height))
    return scaled, (width - scaled_width) // 2, (height - scaled_height) // 2


@lru_cache(maxsize=64)
def _cover_image(path: str, width: int, height: int) -> tuple[pygame.Surface, int, int]:
    image = _load_image(path)
    image_width, image_height = image.get_size()
    if image_width <= 0 or image_height <= 0:
        raise pygame.error(f"画像サイズが0です: {path}")

    scale = max(width / image_width, height / image_height)
    scaled_size = (max(1, int(image_width * scale)), max(1, int(image_height * scale)))
    scaled = pygame.transform.smoothscale(image, scaled_size)
    return scaled, (width - scaled_size[0]) // 2, (height - scaled_size[1]) // 2


@lru_cache(maxsize=64)
def _load_font(path: str | None, size: int) -> pygame.font.Font:
    return pygame.font.Font(path, size)


@lru_cache(maxsize=16)
def _checkerboard(
    width: int,
    height: int,
    color1: tuple[int, ...],
    color2: tuple[int, ...],
    tile_size: int,
) -> pygame.Surface:
    surface = pygame.Surface((width, height))
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            color = color1 if (x // tile_size + y // tile_size) % 2 == 0 else color2
            pygame.draw.rect(surface, color, (x, y, tile_size, tile_size))
    return surface


def get_image(path: str | Path) -> pygame.Surface:
    return _load_image(_normalized_path(path))


def get_contained_image(
    path: str | Path, width: int, height: int
) -> tuple[pygame.Surface, int, int]:
    return _contain_image(_normalized_path(path), int(width), int(height))


def get_cover_image(path: str | Path, width: int, height: int) -> tuple[pygame.Surface, int, int]:
    return _cover_image(_normalized_path(path), int(width), int(height))


def get_font(path: str | Path | None, size: int) -> pygame.font.Font:
    normalized = _normalized_path(path) if path is not None else None
    return _load_font(normalized, int(size))


def get_checkerboard(
    width: int,
    height: int,
    color1: tuple[int, ...],
    color2: tuple[int, ...],
    tile_size: int,
) -> pygame.Surface:
    return _checkerboard(width, height, color1, color2, tile_size)


def preload_images(paths: Iterable[str | Path]) -> None:
    for path in dict.fromkeys(_normalized_path(path) for path in paths):
        _load_image(path)


def clear_asset_caches() -> None:
    """Release cached Pygame resources, primarily for lifecycle tests."""
    _contain_image.cache_clear()
    _cover_image.cache_clear()
    _load_image.cache_clear()
    _load_font.cache_clear()
    _checkerboard.cache_clear()
