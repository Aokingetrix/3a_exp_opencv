# deepface_ver — Play the game

この README は、Linux でこのリポジトリをクローンした人がゲームを実行して遊べるように、最低限のセットアップと実行手順だけを示します。

## 前提
- Python 3.11 を推奨します（TensorFlow / DeepFace 系の依存関係が Python の版に敏感なため、まずは 3.11 系を優先してください）
- カメラが接続されていること

## 安定構成

実機での起動確認を通した、現時点の安定構成は以下です。

- Python 3.11.x
- deepface 0.0.92
- tensorflow-cpu 2.15.1
- tf-keras 2.15.0
- opencv-python 4.9.0.80

DeepFace は内部で legacy Keras を前提にするため、TensorFlow 2.15 系と tf-keras をそろえておくと起動が安定しました。TensorFlow 2.21 系 + Keras 3 の組み合わせでは、`free(): invalid pointer` や retinaface の `tf_keras` 関連エラーが出ていました。

## セットアップ（リポジトリのルート: `3a_exp_opencv`）

1. 仮想環境を作成

```bash
python3.11 -m venv .venv
```

`ensurepip is not available` と出る場合は、Debian/Ubuntu では同じ Python 系列の venv パッケージを入れてから再実行してください。


```bash
sudo apt install python3.11-venv
```

2. 仮想環境を有効化

```bash
source .venv/bin/activate
```

3. 依存ライブラリをインストール

```bash
pip install -r deepface_ver/requirements.txt
```


## 実行

リポジトリのルートから次を実行してください（パッケージ形式での実行が正しくアセットを解決します）。

```bash
python -m deepface_ver.scripts.main
```

## 基本操作
- `S` : スタート / 次ラウンド
- `R` : タイトルへ戻る（ゲーム終了画面）
- `Esc` : 前の画面に戻る
- `Shift + Esc` : 終了

## 補足
- 初回実行時は DeepFace のモデルダウンロードや TensorFlow の初期化に時間がかかる場合があります。
- 依存パッケージは `deepface_ver/requirements.txt` に記載されています。仮想環境内でインストールしてください。
- 実行は必ず仮想環境を有効化した状態で `python -m deepface_ver.scripts.main` を使ってください。
- 顔認識まわりの既知の再現手順は、`deepface_ver/requirements.txt` をそのまま使うことです。個別に `tensorflow` や `deepface` を上書きすると、Keras 互換性が崩れることがあります。

## 顔検出モデル（Haar）の固定運用
- このプロジェクトは `deepface_ver/data/cascades/haarcascade_frontalface_default.xml` を固定で使用します。
- 起動時に `"[emo_recog] Haar loaded from: ..."` が表示され、この固定パスが出ていれば正常です。
- ファイルが欠けている場合は起動時にエラーを出して停止します
