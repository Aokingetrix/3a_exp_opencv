import sys
import pygame
from pygame.locals import *
import cv2
from collections import deque, Counter
from emo_recog import CameraManager_gpt, EmotionRecognizer_gpt
from game_manager import GameManager, GameState 

# --- ヘルパー関数 ---

def draw_text(surface, text, pos, color=(255, 255, 255), size=24):
    """
    Pygameでテキストを描画する関数 (日本語対応)
    """
    try:
        font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        font = pygame.font.Font(font_path, size)
    except IOError:
        print(f"警告: フォント '{font_path}' が見つかりません。デフォルトフォントを使用します。")
        font = pygame.font.Font(None, size + 4)
        
    surface.blit(font.render(text, True, color), pos)

def render_frame(surface, frame, result, x, y):
    """
    OpenCVのフレーム(BGR)をPygame用に変換し、左右反転して描画する
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_flipped = cv2.flip(frame_rgb, 1)
    
    box = result.get('box') 
    if box:
        frame_width = frame.shape[1]
        bx, by, bw, bh = box['x'], box['y'], box['w'], box['h']
        flipped_x = frame_width - bx - bw
        # 顔の枠を描画 (BGR形式の色指定)
        cv2.rectangle(frame_flipped, (flipped_x, by), (flipped_x + bw, by + bh), (0, 255, 0), 2)

    frame_pygame = frame_flipped.swapaxes(0, 1)
    frame_surface = pygame.surfarray.make_surface(frame_pygame)
    surface.blit(frame_surface, (x, y))

def render_image(surface, image_path, x, y, w, h):
    """
    指定されたパスから画像を読み込み、アスペクト比を維持したまま
    指定された矩形(x, y, w, h)の中央に描画する
    """
    try:
        image_surface = pygame.image.load(image_path)
        img_rect = image_surface.get_rect()
        img_w, img_h = img_rect.width, img_rect.height

        if img_w == 0 or img_h == 0:
            raise pygame.error("画像サイズが0です。")

        # 1. アスペクト比の計算
        img_aspect = img_w / img_h  # 画像のアスペクト比 (幅 / 高さ)
        area_aspect = w / h         # 描画エリアのアスペクト比 (幅 / 高さ)

        # 2. 描画サイズの計算
        if img_aspect > area_aspect:
            # 画像がエリアよりも横長 -> 幅をエリアに合わせる
            new_w = w
            new_h = int(new_w / img_aspect)
        else:
            # 画像がエリアよりも縦長 (または同じ) -> 高さをエリアに合わせる
            new_h = h
            new_w = int(new_h * img_aspect)
            
        scaled_surface = pygame.transform.scale(image_surface, (new_w, new_h))

        # 3. 中央揃えのための座標計算
        draw_x = x + (w - new_w) // 2
        draw_y = y + (h - new_h) // 2

        # 4. エリアを背景色で塗りつぶす (画像の余白部分)
        surface.fill((20, 20, 40), (x, y, w, h)) 

        # 5. 描画
        surface.blit(scaled_surface, (draw_x, draw_y))

    except (pygame.error, FileNotFoundError, ZeroDivisionError) as e:
        print(f"画像エラー (パス: {image_path}): {e}")
        # エラー時もゲームが止まらないよう、代わりに黒い四角を描画
        pygame.draw.rect(surface, (0,0,0), (x,y,w,h))

# --- メイン処理 ---

def main():
    pygame.init()

    try:
        cam = CameraManager_gpt()
    except RuntimeError as e:
        print(f"カメラエラー: {e}")
        pygame.quit()
        sys.exit(1)

    frame_for_size = cam.get_frame()
    if frame_for_size is None:
        print("カメラから初期フレームを取得できません。")
        cam.release()
        pygame.quit()
        sys.exit(1)
        
    CAM_WIDTH, CAM_HEIGHT = frame_for_size.shape[1], frame_for_size.shape[0]

    screen = pygame.display.set_mode((CAM_WIDTH * 2, CAM_HEIGHT))
    pygame.display.set_caption("あまのじゃくゲーム")
    clock = pygame.time.Clock()

    recognizer = EmotionRecognizer_gpt()
    result, _ = recognizer.analyze(frame_for_size)
    
    game_manager = GameManager(CAM_WIDTH, CAM_HEIGHT)

    RECOGNITION_HISTORY_SIZE = 3  # 認識結果を平滑化する回数 
    emotion_history = deque(maxlen=RECOGNITION_HISTORY_SIZE)
    smoothed_emotion = "Searching..." # 平滑化された感情の初期値

    result = {'top_emotion': '顔探し中...'}

    running = True
    while running:
        s_key_pressed = False
        e_key_pressed = False
        n_key_pressed = False
        h_key_pressed = False
        r_key_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    running = False
                    break

                if event.key == K_s:
                    s_key_pressed = True
                if event.key == K_e:
                    e_key_pressed = True
                if event.key == K_n:
                    n_key_pressed = True
                if event.key == K_h:
                    h_key_pressed = True
                if event.key == K_r:
                    r_key_pressed = True

        if not running:
            break

        frame = cam.get_frame()
        if frame is None: continue
        
        if pygame.time.get_ticks() % 5 == 0:
            result, _ = recognizer.analyze(frame)

            emotion_history.append(result['top_emotion'])
            
            count = Counter(emotion_history)
            smoothed_emotion = count.most_common(1)[0][0]
        
        game_manager.update(smoothed_emotion, s_key_pressed, e_key_pressed, n_key_pressed, h_key_pressed, r_key_pressed)
        
        screen.fill((20, 20, 40))

        render_frame(screen, frame, result, CAM_WIDTH, 0)
        draw_text(screen, f"You: {smoothed_emotion}", (CAM_WIDTH + 10, 10))

        state = game_manager.state 

        if state == GameState.SELECT_DIFFICULTY:
            draw_text(screen, "難易度をえらんでね", (100, 150), size=50)
            draw_text(screen, "[E] かんたん", (150, 250), size=40)
            draw_text(screen, "[N] ふつう", (150, 310), size=40)
            draw_text(screen, "[H] むずかしい", (150, 370), size=40)
        
        if state == GameState.READY:
            draw_text(screen, f"むずかしさ: {game_manager.difficulty}", (150,CAM_HEIGHT // 2 - 50), size=30)
            draw_text(screen, "「S」ボタンでスタート", (150, CAM_HEIGHT // 2), size=50)

        elif state == GameState.ROUND_START:
            draw_text(screen, f"ラウンド{game_manager.current_round}", (120, CAM_HEIGHT // 2 - 40), size = 80)
        
        elif state == GameState.PLAYING:
            # --- 描画ロジックの変更 (アスペクト比維持 + グリッドレイアウト) ---
            num_npcs = len(game_manager.npc_emotions)
            
            # 描画基準エリア (画面の左半分)
            base_x = 0
            base_y = 0
            base_w = CAM_WIDTH
            base_h = CAM_HEIGHT

            if num_npcs == 1:
                # 1人: 全画面に中央配置
                npc_emotion = game_manager.npc_emotions[0]
                npc_image_path = game_manager.emotion_images.get(npc_emotion, "")
                render_image(screen, npc_image_path, base_x, base_y, base_w, base_h)
            
            elif num_npcs == 2:
                # 2人: 左右分割
                half_w = base_w // 2
                
                # NPC 1 (左)
                npc_emotion1 = game_manager.npc_emotions[0]
                npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
                render_image(screen, npc_image_path1, base_x, base_y, half_w, base_h)
                
                # NPC 2 (右)
                npc_emotion2 = game_manager.npc_emotions[1]
                npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
                render_image(screen, npc_image_path2, base_x + half_w, base_y, half_w, base_h)

            elif num_npcs == 3:
                # 3人: 4分割 (2x2 グリッド) のうち3つを使用
                half_w = base_w // 2
                half_h = base_h // 2
                
                # NPC 1 (左上)
                npc_emotion1 = game_manager.npc_emotions[0]
                npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
                render_image(screen, npc_image_path1, base_x, base_y, half_w, half_h)
                
                # NPC 2 (右上)
                npc_emotion2 = game_manager.npc_emotions[1]
                npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
                render_image(screen, npc_image_path2, base_x + half_w, base_y, half_w, half_h)
                
                # NPC 3 (左下)
                npc_emotion3 = game_manager.npc_emotions[2]
                npc_image_path3 = game_manager.emotion_images.get(npc_emotion3, "")
                render_image(screen, npc_image_path3, base_x, base_y + half_h, half_w, half_h)
                
                # (右下は自動的に背景色で塗りつぶされます)
            
            # タイマーの描画 (変更なし)
            draw_text(screen, f"Time: {game_manager.timer_sec:.1f}", (CAM_WIDTH // 2 , 10), size=40)

        elif state == GameState.RESULT:
            draw_text(screen, f"ラウンド {game_manager.current_round}", (100, 150), size=40)
            npc_text = ",".join(game_manager.npc_emotions)
            draw_text(screen, f"NPC: {npc_text}", (150, 220), size=30)
            draw_text(screen, f"あなた: {game_manager.player_emotion}", (150, 270), size=30)
            draw_text(screen, game_manager.round_result_text, (120, 350), size=50)
            draw_text(screen, "「S」で次のラウンドへ", (150, 450), size=30) 

        elif state == GameState.GAME_FINISH:
            draw_text(screen, "Finish", (150, 200), size=60)
            draw_text(screen, f"スコア: {game_manager.score}", (120, 300), size=50)
            draw_text(screen, "「S」：再挑戦", (150, 400), size=30)
            draw_text(screen, "「R」：難易度をえらびなおす", (150, 500), size=30)

        draw_text(screen, f"Score: {game_manager.score}", (10, CAM_HEIGHT - 40))
        if state == GameState.RESULT or state == GameState.GAME_FINISH:
            draw_text(screen, f"ラウンド: {game_manager.current_round}/{game_manager.total_rounds}", (CAM_WIDTH - 150, CAM_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(game_manager.fps)

    # 終了処理 (デバッグプリント付き)
    print("終了します...")
    print("[デバッグ] カメラ解放開始")
    cam.release()
    print("[デバッグ] カメラ解放完了")
    pygame.time.wait(300)
    print("[デバッグ] pygame終了処理開始")
    pygame.quit()
    print("[デバッグ] pygame終了処理完了")
    sys.exit()

if __name__ == "__main__":
    main()