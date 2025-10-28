import sys
import pygame
from pygame.locals import *
import cv2
from collections import deque, Counter
import random 
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
        cv2.rectangle(frame_flipped, (flipped_x, by), (flipped_x + bw, by + bh), (0, 255, 0), 2)

    frame_pygame = frame_flipped.swapaxes(0, 1)
    frame_surface = pygame.surfarray.make_surface(frame_pygame)
    surface.blit(frame_surface, (x, y))

# ★修正点: fill_bg パラメータを追加
def render_image(surface, image_path, x, y, w, h, fill_bg=True):
    """
    指定されたパスから画像を読み込み、アスペクト比を維持したまま
    指定された矩形(x, y, w, h)の中央に描画する
    fill_bg=True の場合、描画エリアを背景色で塗りつぶす
    """
    try:
        image_surface = pygame.image.load(image_path)
        img_rect = image_surface.get_rect()
        img_w, img_h = img_rect.width, img_rect.height

        if img_w == 0 or img_h == 0:
            raise pygame.error("画像サイズが0です。")

        img_aspect = img_w / img_h
        area_aspect = w / h

        if img_aspect > area_aspect:
            new_w = w
            new_h = int(new_w / img_aspect)
        else:
            new_h = h
            new_w = int(new_h * img_aspect)
            
        scaled_surface = pygame.transform.scale(image_surface, (new_w, new_h))

        draw_x = x + (w - new_w) // 2
        draw_y = y + (h - new_h) // 2

        if fill_bg:
            surface.fill((20, 20, 40), (x, y, w, h)) 

        surface.blit(scaled_surface, (draw_x, draw_y))

    except (pygame.error, FileNotFoundError, ZeroDivisionError) as e:
        print(f"画像エラー (パス: {image_path}): {e}")
        pygame.draw.rect(surface, (0,0,0), (x,y,w,h))


class FloatingImage:
    def __init__(self, image_path, screen_w, screen_h):
        self.image_path = image_path
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        # 画像サイズをランダム化 (例: 画面幅の1/8～1/5)
        base_size = screen_w // 10
        size_variation = screen_w // 12
        self.size = int(base_size + random.uniform(-size_variation, size_variation))
        self.w = self.size
        self.h = self.size

        # 初期位置をランダム化 (画面内)
        self.x = random.uniform(0, screen_w - self.w)
        self.y = random.uniform(0, screen_h - self.h)
        
        # 移動速度をランダム化 (ピクセル/フレーム)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-0.5, 0.5)
        
        if -0.2 < self.vx < 0.2: self.vx = 0.5 # 遅すぎ防止
        if -0.2 < self.vy < 0.2: self.vy = 0.3 # 遅すぎ防止

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # 画面端での反射
        if self.x <= 0 or self.x + self.w >= self.screen_w:
            self.vx *= -1
            self.x = max(0, min(self.x, self.screen_w - self.w))
            
        if self.y <= 0 or self.y + self.h >= self.screen_h:
            self.vy *= -1
            self.y = max(0, min(self.y, self.screen_h - self.h))

    def draw(self, surface):
        render_image(surface, self.image_path, int(self.x), int(self.y), self.w, self.h, fill_bg=False)

# --- メイン処理 ---
def main():
    pygame.init()

    # ... (カメラ初期化、エラーハンドリングは変更なし) ...
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
    
    SCREEN_WIDTH = CAM_WIDTH * 2
    SCREEN_HEIGHT = CAM_HEIGHT

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("あまのじゃくゲーム")
    clock = pygame.time.Clock()

    recognizer = EmotionRecognizer_gpt()
    result, _ = recognizer.analyze(frame_for_size)
    
    # ★修正: 画面サイズを渡す
    game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT)

    # ... (平滑化ロジックは変更なし) ...
    RECOGNITION_HISTORY_SIZE = 3 
    emotion_history = deque(maxlen=RECOGNITION_HISTORY_SIZE)
    smoothed_emotion = "探し中..."
    result = {'top_emotion': '探し中...'}


    floating_images = []
    image_paths = list(game_manager.emotion_images.values())
    for _ in range(10): # 10個の画像を浮遊させる
        path = random.choice(image_paths)
        floating_images.append(FloatingImage(path, SCREEN_WIDTH, SCREEN_HEIGHT))
    
    frame = frame_for_size

    frame_count = 0

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
                if event.key == K_s: s_key_pressed = True
                if event.key == K_e: e_key_pressed = True
                if event.key == K_n: n_key_pressed = True
                if event.key == K_h: h_key_pressed = True
                if event.key == K_r: r_key_pressed = True

        if not running:
            break


        game_manager.update(
            smoothed_emotion, 
            s_key_pressed, 
            e_key_pressed, 
            n_key_pressed, 
            h_key_pressed,
            r_key_pressed
        )
        


        state = game_manager.state 

        if state == GameState.TITLE:
            screen.fill((245, 222, 179))
            for img in floating_images:
                img.update()
                img.draw(screen)

            draw_text(screen, "あまのじゃくゲーム", 
                      (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 100), 
                      color = (50, 50, 50), size=70)
            
            draw_text(screen, "[S]スタート!", 
                      (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50), 
                      color = (50, 50, 50), size=40)

            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue 

        # 5フレームに1回、感情を更新 (TITLE以外でのみ実行)
        screen.fill((245, 222, 179))

        frame = cam.get_frame()
        if frame is None:
            frame = frame_for_size
            print("カメラフレームの取得に失敗しました")
        if frame_count % 5 == 0:
            result, _ = recognizer.analyze(frame)
            emotion_history.append(result['top_emotion'])
            count = Counter(emotion_history)
            smoothed_emotion = count.most_common(1)[0][0]
        
        render_frame(screen, frame, result, CAM_WIDTH, 0)
        draw_text(screen, f"あなた: {smoothed_emotion}", (CAM_WIDTH + 10, 10))

        if state == GameState.SELECT_DIFFICULTY:
            draw_text(screen, "難易度をえらんでね", (100, 150), size=50)
            draw_text(screen, "[E] かんたん", (150, 250), size=40)
            draw_text(screen, "[N] ふつう", (150, 310), size=40)
            draw_text(screen, "[H] むずかしい", (150, 370), size=40)
        
        elif state == GameState.READY:
            draw_text(screen, f"難易度: {game_manager.difficulty}", (150,CAM_HEIGHT // 2 - 50), size=30)
            draw_text(screen, "[S]ゲームスタート", (150, CAM_HEIGHT // 2), size=50)
        
        elif state == GameState.ROUND_START:
            draw_text(screen, f"ラウンド {game_manager.current_round}", 
                      (120, CAM_HEIGHT // 2 - 40), size=80)

        elif state == GameState.PLAYING:
            num_npcs = len(game_manager.npc_emotions)
            base_x, base_y, base_w, base_h = 0, 0, CAM_WIDTH, CAM_HEIGHT
            if num_npcs == 1:
                # (1人: 全画面) ...
                npc_emotion = game_manager.npc_emotions[0]
                npc_image_path = game_manager.emotion_images.get(npc_emotion, "")
                render_image(screen, npc_image_path, base_x, base_y, base_w, base_h, fill_bg=False)
            elif num_npcs == 2:
                # (2人: 左右分割) ...
                half_w = base_w // 2
                npc_emotion1 = game_manager.npc_emotions[0]
                npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
                render_image(screen, npc_image_path1, base_x, base_y, half_w, base_h, fill_bg=False)
                npc_emotion2 = game_manager.npc_emotions[1]
                npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
                render_image(screen, npc_image_path2, base_x + half_w, base_y, half_w, base_h, fill_bg=False)
            elif num_npcs >= 3: # 3人以上 (3人目の実装に合わせて >= 3 に変更)
                # (3人: 4分割) ...
                half_w = base_w // 2
                half_h = base_h // 2
                npc_emotion1 = game_manager.npc_emotions[0]
                npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
                render_image(screen, npc_image_path1, base_x, base_y, half_w, half_h, fill_bg=False)
                npc_emotion2 = game_manager.npc_emotions[1]
                npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
                render_image(screen, npc_image_path2, base_x + half_w, base_y, half_w, half_h, fill_bg=False)
                npc_emotion3 = game_manager.npc_emotions[2]
                npc_image_path3 = game_manager.emotion_images.get(npc_emotion3, "")
                render_image(screen, npc_image_path3, base_x, base_y + half_h, half_w, half_h, fill_bg=False)
            # (タイマー描画)
            draw_text(screen, f"残り: {game_manager.timer_sec:.1f}", (CAM_WIDTH // 2 - 50, 10), size=40)

        elif state == GameState.RESULT:
            draw_text(screen, f"ラウンド{game_manager.current_round} ", (100, 50), size=40)
            npc_text = ",".join(game_manager.npc_emotions)
            draw_text(screen, f"相手: {npc_text}", (150, 120), size=30)
            draw_text(screen, f"あなた: {game_manager.player_emotion}", (150, 170), size=30)
            draw_text(screen, game_manager.round_result_text, (120, 250), size=30)
            if game_manager.current_round != 3:
                draw_text(screen, "[S]次のラウンドへ進む", (150, 350), size=30) 
            else:
                draw_text(screen, "[S]次へ進む", (150, 350), size=30) 

        elif state == GameState.GAME_FINISH:
            draw_text(screen, "フィニッシュ！", (150, 100), size=60)
            draw_text(screen, f"スコア: {game_manager.score}", (120, 200), size=50)
            draw_text(screen, "[S]はじめから", (150, 300), size=30)
            draw_text(screen, "[R]難易度をかえる", (150, 350), size=30)

        # 共通UI (スコア、ラウンド)
        draw_text(screen, f"スコア: {game_manager.score}", (10, CAM_HEIGHT - 40))
        #if state == GameState.RESULT or state == GameState.GAME_FINISH:
           # draw_text(screen, f"ラウンド: {game_manager.current_round}/{game_manager.total_rounds}", (CAM_WIDTH - 150, CAM_HEIGHT - 40), size = 10)

        pygame.display.flip()
        clock.tick(game_manager.fps)
        frame_count += 1

    # (終了処理は変更なし)
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