# deepface_ver — Play the game

この README は、はじめてこのリポジトリをクローンした人がゲームを実行して遊べるように、最低限のセットアップと実行手順だけを示します。

## 前提
- Python 3.11 を推奨します（仮想環境での実行を想定）
- カメラが接続されていること

## セットアップ（リポジトリのルート: `3a_exp_opencv`）

1. 仮想環境を作成

```powershell
python -m venv .venv
```

2. 仮想環境を有効化（PowerShell）

```powershell
.\.venv\Scripts\Activate.ps1
```

3. 依存ライブラリをインストール

```powershell
pip install -r deepface_ver/requirements.txt
```

## 実行

リポジトリのルートから次を実行してください（パッケージ形式での実行が正しくアセットを解決します）。

```powershell
python -m deepface_ver.scripts.main
```

## 基本操作
- `S` : スタート / 次ラウンド
- `R` : タイトルへ戻る（ゲーム終了画面）
- `Q` または `Esc` : 終了

## 補足
- 初回実行時は DeepFace のモデルダウンロードや TensorFlow の初期化に時間がかかる場合があります。
- 依存パッケージは `deepface_ver/requirements.txt` に記載されています。仮想環境内でインストールしてください。
- 実行は必ず仮想環境を有効化した状態で `python -m deepface_ver.scripts.main` を使ってください。
- 開発履歴・移行に関するメモは `MIGRATION.md` を参照してください。

## 顔検出モデル（Haar）の固定運用
- このプロジェクトは `deepface_ver/data/cascades/haarcascade_frontalface_default.xml` を固定で使用します。
- 起動時に `"[emo_recog] Haar loaded from: ..."` が表示され、この固定パスが出ていれば正常です。
- ファイルが欠けている場合は起動時にエラーを出して停止します（環境差で別Haarを自動探索しません）。
