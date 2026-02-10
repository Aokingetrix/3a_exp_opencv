# 使い方

## セットアップ (Windows)

1. **リポジトリをクローン**
   ```
   git clone https://github.com/Aokingetrix/3a_exp_opencv.git
   cd 3a_exp_opencv
   ```

2. **Windows 対応ブランチに切り替え** (必須: Ubuntu 版とは異なるため)
   ```
   git checkout feature/windows
   ```

3. **Python 3.11 の仮想環境を作成** 
   - Python 3.11 を公式サイトからダウンロード・インストール（インストーラで「Just for me」を選択）。
   - 仮想環境作成:
     ```
     C:\Users\<your_username>\AppData\Local\Programs\Python\Python311\python.exe -m venv .venv
     ```
   - 仮想環境有効化:
     ```
     .\.venv\Scripts\Activate.ps1
     ```

3. **依存ライブラリをインストール**
   ```
   pip install -r deepface_ver\requirements.txt
   ```
   ※ 初回実行時は DeepFace のモデルダウンロードが発生（ネット接続必要）。

4. **ゲームを実行**
   ```
   cd deepface_ver
   python main.py
   ```
   - カメラとマイクが必要（表情認識とゲームプレイのため）。
   - タイトル画面から S キーでスタート。

## 注意点
- 仮想環境外では動作しない（依存が仮想環境内のみ）。
- サウンドファイル（data/sounds/）が欠けている場合、SE は無効化されるがゲームは続行可能。
- Windows フォントが自動検出される（Meiryo または YuGothic が優先）。

# 記録
## 2/10 
- やったこと
  - 依存関係を更新してWindows版でも動くようにできた
  - requirements.txt を Ubuntuから Windows 向けに書き換え
  - settings.py のフォントパスを OS 判別で自動選択に変更
  - .gitignore に仮想環境を追加
  - 仮想環境作成・依存インストール・実行テスト完了
  - feature/windows ブランチを作成・プッシュ

