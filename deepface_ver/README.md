# あまのじゃくゲーム（fes2026-next）

Webカメラの表情認識を使い、画面のあまのじゃくとは違う表情を作るゲームです。同じコードをWindows 10/11とLinuxで実行でき、外部テーマで写真・背景・音声・表示文を差し替えられます。

## 対応環境

- 64bit版Python 3.11
- Windows 10/11 x64（CPU実行）
- x86_64 Linux（Ubuntu系を基準に検証）
- Webカメラ

TensorFlow、DeepFace、Kerasの互換性を保つため、`requirements.txt`の固定バージョンを使用してください。WindowsではMicrosoft Visual C++ Redistributable 2015–2022も必要です。

## セットアップ

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r deepface_ver\requirements.txt
python -m deepface_ver.scripts.main
```

### Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r deepface_ver/requirements.txt
python -m deepface_ver.scripts.main
```

Ubuntuで`venv`を作れない場合は、先に`sudo apt install python3.11-venv`を実行してください。

## 起動オプション

```text
--camera-index N
--camera-backend auto|dshow|msmf|v4l2|default
--window-size WIDTHxHEIGHT
--theme-dir PATH
```

通常はカメラバックエンド`auto`で構いません。WindowsではDirectShow→MSMF、LinuxではV4L2を優先します。内部UIは1280×480で描画され、指定ウィンドウへアスペクト比を保って拡大・縮小されます。

## 操作

- `S`: スタート、決定、次ラウンド
- `E`: 説明をスキップ
- `R`: 終了画面からタイトルへ戻る
- `Esc`: 前の画面へ戻る（プレイ中は無効）
- `Shift+Esc`: ゲーム終了
- ウィンドウの閉じるボタン: ゲーム終了

## 外部テーマ

テーマディレクトリには`theme.toml`を置きます。コマンドライン指定が環境変数より優先されます。

```bash
python -m deepface_ver.scripts.main --theme-dir ../amanojaku-fan-theme
```

```powershell
$env:AMANOJAKU_THEME_DIR = "..\amanojaku-fan-theme"
python -m deepface_ver.scripts.main
```

`schema_version`、`id`、`display_name`は必須です。未指定の素材・文言は通常テーマへフォールバックし、指定したファイルが存在しない場合は起動時にエラーになります。テーマで変更できるのは画像、画面別背景、BGM、SE、表示文です。得点・ライフ・制限時間・感情の内部キーは変更できません。

公開テストテーマは`deepface_ver/data/themes/test-shapes`にあります。個人写真や内輪素材は公開リポジトリへ置かず、privateリポジトリで管理してください。

## ハイスコア

ランキングはテーマIDごとに分離されます。

- Windows: `%LOCALAPPDATA%\amanojaku-game\themes\<theme-id>\highscore.json`
- Linux: `${XDG_DATA_HOME:-~/.local/share}/amanojaku-game/themes/<theme-id>/highscore.json`

旧`deepface_ver/data/highscore.json`は、通常テーマの保存先がまだない初回だけ移行されます。

## 開発

```bash
python -m pip install -r requirements-dev.txt pygame==2.6.1
pytest
ruff check deepface_ver/core deepface_ver/scripts deepface_ver/tests deepface_ver/ui
ruff format --check deepface_ver/core deepface_ver/scripts deepface_ver/tests deepface_ver/ui
```

高速CIはWindows/Linuxの両方でハードウェア非依存テストを実行します。TensorFlow・DeepFaceを含む完全な依存確認は`Full Runtime Smoke`ワークフローを手動実行してください。実機確認ではカメラ、日本語、BGM/SE、全画面遷移、スコア再読込を確認します。

## 補足

- 初回起動ではDeepFaceのモデル取得とTensorFlow初期化に時間がかかります。
- 顔検出には同梱したHaar Cascadeを使用します。
- 日本語フォントはOFLライセンスのNoto Sans JPを同梱し、OSフォントより優先します。
