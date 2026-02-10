## Refactor: ディレクトリ構成の整理 (2026-02-10)

変更点（要点）:
- 新しい構成:
  - `deepface_ver/core/` : `settings.py`, `utils.py`, `game_manager.py`
  - `deepface_ver/emo/`  : `emo_recog.py`
  - `deepface_ver/ui/`   : `drawing.py`, `ui_elements.py`
  - `deepface_ver/scripts/` : `main.py` (実行コード)
  - `deepface_ver/tests/` : 簡単なインポートテスト

互換性:
- 既存のトップレベルファイル（例: `utils.py`, `settings.py`, `main.py` 等）は **互換シム** に置き換えました。
  - そのため従来通り `python deepface_ver/main.py` や `python main.py` で実行できます。
  - ただし推奨はパッケージ実行: `python -m deepface_ver.scripts.main`

テスト:
- `deepface_ver/tests/test_imports.py` を追加。環境に `pytest` があれば実行してください（今回は pytest 未インストールのため実行せず）。

備考:
- 実行時に TensorFlow のログや Pygame の初期化メッセージが出ますが、インポートチェックは成功しました。
- 変更点の微調整や追加のファイル移動（例: assets を `data/` の下に分離等）は要望があれば対応します。
