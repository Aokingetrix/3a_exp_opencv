# Original content moved from deepface_ver/main.py
# (kept for reference / backup)

# compatibility shim for top-level main
from deepface_ver.scripts.main import main

if __name__ == "__main__":
    main()



# --- メイン処理 ---
def main():
    # Pygame の初期化 (font も main で行うのが確実)
    pygame.init()
    pygame.font.init() 

    # --- 1. カメラと画面の初期化 ---
    try:
        cam = CameraManager_gpt()
    except RuntimeError as e:
        print(f"カメラエラー: {e}")
        pygame.quit()
        sys.exit(1)
    except Exception as e:
        print(f"カメラ初期化中に予期せぬエラー: {e}")
        pygame.quit()
        sys.exit(1)

    frame_for_size = cam.get_frame()
    if frame_for_size is None:
        print("カメラから初期フレームを取得できません。")
        cam.release()
        pygame.quit()
        sys.exit(1)
        
    CAM_WIDTH, CAM_HEIGHT = frame_for_size.shape[1], frame_for_size.shape[0]
    
    SCREEN_WIDTH = CAM_WIDTH * 2
    SCREEN_HEIGHT = CAM_HEIGHT

    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("あまのじゃくゲーム")
    except pygame.error as e:
        print(f"画面の初期化に失敗しました: {e}")
        cam.release()
        pygame.quit()
        sys.exit(1)
        
    clock = pygame.time.Clock()

    # --- 2. リソースのセットアップ ---

    # ★追加: サウンドエフェクト(SE)の読み込み
    try:
        sounds = {
            "select": pygame.mixer.Sound(settings.SE_PATHS["select"]),
            "count": pygame.mixer.Sound(settings.SE_PATHS["count"]),
            "success": pygame.mixer.Sound(settings.SE_PATHS["success"]),
            "fail": pygame.mixer.Sound(settings.SE_PATHS["fail"]),
        }
        # (音量をお好みで調整)
        sounds["count"].set_volume(0.5)
    except Exception as e:
        print(f"SEの読み込みエラー: {e}")
        # (ゲーム続行のため、ダミーのサウンドオブジェクトを作成するなどの対応も可能)
        pygame.quit()
        sys.exit(1)
    
    # チェック模様の背景
    background_surface = utils.create_checkerboard_surface(
        SCREEN_WIDTH, SCREEN_HEIGHT, 
        settings.WII_BACKGROUND, settings.WII_BROWN, 
        settings.TILE_SIZE
    )

    # タイマーUI
    timer_display = Timer(
        screen_surface=screen,
        pos=(CAM_WIDTH // 2 - 70, 10), # 表示位置 (左半分の画面中央上部あたり)
        icon_path="data/clock.png", # このパスに画像が必要です
        font_path=settings.FONT_PATH,
        font_size=40,
        text_color=settings.TEXT_DARK,
        bg_color=settings.WII_TRANSLUCENT_BG,
        shadow_color = settings.WII_SHADOW_COLOR
    )

    #ライフUI
    life_display = LifeDisplay(
        screen_surface = screen,
        icon_path = "data/heart.png", 
        icon_size = 60,
        pos = (0, 0),
        max_lives = 3,
        spacing = 1
    )

    # --- 3. マネージャーと変数の初期化 ---
    
    recognizer = EmotionRecognizer_gpt()
    game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT, sounds)

    # 表情認識の平滑化
    emotion_history = deque(maxlen=settings.RECOGNITION_HISTORY_SIZE)
    smoothed_emotion = "探し中..."
    # result は box も含む辞書なので、初期値も合わせておく
    result = {'top_emotion': '探し中...', 'box': None} 

    # タイトル画面用の浮遊画像
    floating_images = []
    try:
        # game_manager.emotion_images が画像パスの辞書であることを期待
        image_paths = list(game_manager.emotion_images.values())
        if not image_paths:
            print("警告: game_manager から画像パスが取得できませんでした。")
            # フォールバックとしてタイマー画像を使う
            image_paths = ["data/clock.png"]
            
        for _ in range(10): # 10個の画像を浮遊させる
            path = random.choice(image_paths)
            floating_images.append(FloatingImage(path, SCREEN_WIDTH, SCREEN_HEIGHT))
    except AttributeError:
        print("エラー: game_manager に emotion_images 属性がありません。")
        # 1つだけフォールバック画像を追加
        floating_images.append(FloatingImage("data/clock.png", SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"FloatingImage の初期化エラー: {e}")

    
    frame = frame_for_size # 初期フレーム
    frame_count = 0
    running = True

    current_bgm = None

    # --- 4. メインループ ---
    while running:

        # --- 4-1. イベント処理 ---
        s_key_pressed = e_key_pressed = n_key_pressed = h_key_pressed = r_key_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    running = False
                    break
                # ゲームマネージャに渡すキー入力
                if event.key == K_s: 
                    s_key_pressed = True
                    sounds["select"].play()
                if event.key == K_e: e_key_pressed = True # (デバッグ用)
                if event.key == K_n: n_key_pressed = True # (デバッグ用)
                if event.key == K_h: h_key_pressed = True # (デバッグ用)
                if event.key == K_r: r_key_pressed = True

        if not running:
            break

        # --- 4-2. ロジック更新 ---
        
        # ゲーム状態の更新
        game_manager.update(
            smoothed_emotion, 
            s_key_pressed, 
            e_key_pressed, 
            n_key_pressed, 
            h_key_pressed,
            r_key_pressed
        )
    

        state = game_manager.state
        
        # BGMが *実際に* 再生中かどうかも確認する
        is_bgm_playing = pygame.mixer.music.get_busy()

        if state == GameState.TITLE:
            # 「タイトル曲」であるべき時に、「タイトル曲」でないか「停止」していたら再生
            if current_bgm != "title" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["title"])
                current_bgm = "title"
        
        elif state == GameState.INSTRUCTION:
            # 「タイトル曲」であるべき時に、「タイトル曲」でないか「停止」していたら再生
            if current_bgm != "title" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["title"])
                current_bgm = "title"

        elif (state == GameState.PLAYING or state == GameState.RESULT or state == GameState.ROUND_START):
            # 「プレイ曲」であるべき時に、「プレイ曲」でないか「停止」していたら再生
            if current_bgm != "play" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["play"])
                current_bgm = "play"

        elif state == GameState.GAME_FINISH:
            # 「終了曲」であるべき時に、「終了曲」でないか「停止」していたら再生
            if current_bgm != "finish" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["finish"])
                current_bgm = "finish"
        # --- 4-3. 描画 ---
        
        # 4-3-1. タイトル画面の描画
        if state == GameState.TITLE:
            drawing.draw_title_screen(screen, background_surface, floating_images)
            
            # (タイトル画面はカメラ更新や共通UI描画をスキップ)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue

        # 説明画面の描画
        elif state == GameState.INSTRUCTION:
            drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)
            drawing.draw_instruction_screen(screen, background_surface, SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # (説明画面も共通UIはスキップ)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue

        

        # 4-3-2. (ゲーム中) カメラと表情認識の更新
        
        current_frame = cam.get_frame()
        if current_frame is not None:
            frame = current_frame # 正常に取得できたらフレームを更新
        else:
            print("カメラフレームの取得に失敗しました。直前のフレームを使用します。")
            # frame は直前のフレームが維持される

        if frame_count % 5 == 0: # 5フレームに1回認識
            new_result, _ = recognizer.analyze(frame)
            
            if new_result and isinstance(new_result, dict) and 'top_emotion' in new_result: 
                result = new_result # 認識成功時 (boxも含まれる)
                emotion_history.append(result['top_emotion'])
                count = Counter(emotion_history)
                smoothed_emotion = count.most_common(1)[0][0]
            else:
                # 認識失敗時 (顔が映っていないなど)
                emotion_history.append('探し中...')
                count = Counter(emotion_history)
                smoothed_emotion = count.most_common(1)[0][0]
                # 'box' は前の結果を維持し、表情だけ更新
                result['top_emotion'] = '探し中...' 

        
        # 4-3-3. (ゲーム中) 共通の背景（カメラ映像など）を描画する
        drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)

        # 4-3-4. (ゲーム中) 状態別の描画
        if state == GameState.ROUND_START:
            drawing.draw_round_start_screen(screen, game_manager, CAM_WIDTH, CAM_HEIGHT)
            
        elif state == GameState.PLAYING:
            drawing.draw_playing_screen(screen, game_manager, timer_display, CAM_WIDTH, CAM_HEIGHT)
            
        elif state == GameState.RESULT:
            drawing.draw_result_screen(screen, game_manager, CAM_WIDTH, CAM_HEIGHT)
            
        elif state == GameState.GAME_FINISH:
            drawing.draw_finish_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)

        # 4-3-5. (ゲーム中) 共通UI（スコアなど）を描画する
        if state != GameState.GAME_FINISH:
            drawing.draw_common_ui(screen, game_manager, CAM_WIDTH, CAM_HEIGHT, life_display)

        # --- 4-4. 画面更新 ---
        pygame.display.flip()
        clock.tick(game_manager.fps)
        frame_count += 1

    # --- 5. 終了処理 ---
    print("終了します...")
    print("カメラ解放開始")
    cam.release()
    print("[デバッグ] カメラ解放完了")
    pygame.time.wait(300) # 終了処理のための待機
    print("[デバッグ] pygame終了処理開始")
    pygame.quit()
    print("[デバッグ] pygame終了処理完了")
    sys.exit(1)


if __name__ == "__main__":
    main()
