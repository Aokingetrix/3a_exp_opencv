"""Versioned theme manifests for public and private asset packs."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
ASSET_SECTIONS = ("images", "backgrounds", "bgm", "se")


class ThemeError(ValueError):
    pass


@dataclass(frozen=True)
class ThemeManifest:
    theme_id: str
    display_name: str
    text: dict[str, Any]
    images: dict[str, str]
    backgrounds: dict[str, str]
    bgm: dict[str, str]
    se: dict[str, str]

    def text_value(self, key: str, default: Any) -> Any:
        return self.text.get(key, default)


def load_theme(default_manifest: Path, external_dir: Path | None = None) -> ThemeManifest:
    base = _read_manifest(default_manifest)
    if external_dir is None:
        return _to_theme(base)
    external_manifest = Path(external_dir).expanduser().resolve() / "theme.toml"
    override = _read_manifest(external_manifest)
    merged = dict(base)
    merged["id"] = override["id"]
    merged["display_name"] = override["display_name"]
    for section in ("text", *ASSET_SECTIONS):
        values = dict(base.get(section, {}))
        values.update(override.get(section, {}))
        merged[section] = values
    return _to_theme(merged)


def _read_manifest(path: Path) -> dict[str, Any]:
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ThemeError(f"テーママニフェストが見つかりません: {path}")
    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
    except tomllib.TOMLDecodeError as error:
        raise ThemeError(f"theme.tomlの構文が不正です: {path}: {error}") from error
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ThemeError(f"未対応のschema_versionです: {data.get('schema_version')}")
    for key in ("id", "display_name"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ThemeError(f"theme.tomlに必須文字列 `{key}` がありません: {path}")
    root = path.parent
    for section in ASSET_SECTIONS:
        resolved: dict[str, str] = {}
        values = data.get(section, {})
        if not isinstance(values, dict):
            raise ThemeError(f"`{section}` はテーブルで指定してください: {path}")
        for key, relative in values.items():
            if not isinstance(relative, str):
                raise ThemeError(f"`{section}.{key}` はパス文字列で指定してください")
            candidate = (root / relative).resolve()
            if not candidate.is_file():
                raise ThemeError(f"テーマ素材が見つかりません: {section}.{key} -> {candidate}")
            resolved[str(key)] = str(candidate)
        data[section] = resolved
    if not isinstance(data.get("text", {}), dict):
        raise ThemeError("`text` はテーブルで指定してください")
    return data


def _to_theme(data: dict[str, Any]) -> ThemeManifest:
    return ThemeManifest(
        theme_id=str(data["id"]),
        display_name=str(data["display_name"]),
        text=dict(data.get("text", {})),
        images=dict(data.get("images", {})),
        backgrounds=dict(data.get("backgrounds", {})),
        bgm=dict(data.get("bgm", {})),
        se=dict(data.get("se", {})),
    )
