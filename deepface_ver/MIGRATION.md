# MIGRATION / 作業記録

このファイルは開発・移行の作業記録専用です。実行手順は README に記載します。

## 2026-02-10: ディレクトリ構成整理

実施内容:
- 構成を `core / emo / ui / scripts / tests` に分割。
- 実装の責務をサブパッケージへ移動。

当時の意図:
- パッケージルートを軽量化し、依存方向を明確化する。

## 2026-02-16: top-level cleanup

実施内容:
- `deepface_ver` 直下の旧実装を `deepface_ver/legacy/` に退避。
- ルート直下モジュールは ImportError スタブ化し、旧インポートを明示的に停止。

影響:
- `deepface_ver.main` などトップレベルAPIへの依存コードはそのままでは動作しない。
- 既存利用側は `deepface_ver.scripts.main` / `deepface_ver.core.*` / `deepface_ver.ui.*` / `deepface_ver.emo.*` へ移行が必要。

## 2026-02-16: パス解決・参照整合の修正

背景:
- `data/...` の相対パスが実行カレントディレクトリに依存し、クローン直後の標準実行でアセット参照が崩れる問題があった。

実施内容:
- `core/settings.py` にアセット解決責務を集約。
  - `PACKAGE_ROOT`, `DATA_DIR`, `asset_path()` を追加。
  - BGM/SE/画像パスを `deepface_ver/data` 起点で一元定義。
- `scripts/main.py`, `core/game_manager.py`, `ui/drawing.py` の直書き `data/...` を設定参照へ置換。
- 判定文字列の不一致（`Searching...` vs `探し中...`）を統一。
- 正常終了時の終了コードを 0 に修正。

狙い:
- 参照先を一箇所で管理し、将来のアセット移動時の変更範囲を限定する。
- 実行パス依存を除去して、クローン直後の再現性を上げる。

