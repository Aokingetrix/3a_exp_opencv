# main moved into scripts (imports updated to package paths)
import sys
import pygame
from pygame.locals import *
from collections import deque, Counter
import random
import pygame.mixer

try:
    from ..emo.emo_recog import CameraManager_gpt, EmotionRecognizer_gpt
    from ..core.game_manager import GameManager, GameState
except ImportError as e:
    print(f"エラー: 必要なモジュールが見つかりません。({e})")
    sys.exit(1)

try:
    from ..core import settings
    from ..core import utils
    from ..ui import drawing
    from ..ui.ui_elements import FloatingImage, Timer, LifeDisplay
except ImportError as e:
    print(f"エラー: 自作モジュールが見つかりません。({e})")
    sys.exit(1)


def main():
    pygame.init()
    pygame.font.init()

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

    try:
        sounds = {
            "select": pygame.mixer.Sound(settings.SE_PATHS["select"]),
            "count": pygame.mixer.Sound(settings.SE_PATHS["count"]),
            "success": pygame.mixer.Sound(settings.SE_PATHS["success"]),
            "fail": pygame.mixer.Sound(settings.SE_PATHS["fail"]),
        }
        sounds["count"].set_volume(0.5)
    except Exception as e:
        print(f"SEの読み込みエラー: {e}")
        pygame.quit()
        sys.exit(1)

    background_surface = utils.create_checkerboard_surface(
        SCREEN_WIDTH, SCREEN_HEIGHT, 
        settings.WII_BACKGROUND, settings.WII_BROWN, 
        settings.TILE_SIZE
    )

    timer_display = Timer(
        screen_surface=screen,
        pos=(CAM_WIDTH // 2 - 70, 10),
        icon_path="data/clock.png",
        font_path=settings.FONT_PATH,
        font_size=40,
        text_color=settings.TEXT_DARK,
        bg_color=settings.WII_TRANSLUCENT_BG,
        shadow_color = settings.WII_SHADOW_COLOR
    )

    life_display = LifeDisplay(
        screen_surface = screen,
        icon_path = "data/heart.png",
        icon_size = 60,
        pos = (0, 0),
        max_lives = 3,
        spacing = 1
    )

    recognizer = EmotionRecognizer_gpt()
    game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT, sounds)

    emotion_history = deque(maxlen=settings.RECOGNITION_HISTORY_SIZE)
    smoothed_emotion = "探し中..."
    result = {'top_emotion': '探し中...', 'box': None}

    floating_images = []
    try:
        image_paths = list(game_manager.emotion_images.values())
        if not image_paths:
            image_paths = ["data/clock.png"]
        for _ in range(10):
            path = random.choice(image_paths)
            floating_images.append(FloatingImage(path, SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"FloatingImage の初期化エラー: {e}")

    frame = frame_for_size
    frame_count = 0
    running = True

    current_bgm = None

    while running:
        s_key_pressed = e_key_pressed = n_key_pressed = h_key_pressed = r_key_pressed = False
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
                    sounds["select"].play()
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
        is_bgm_playing = pygame.mixer.music.get_busy()

        if state == GameState.TITLE:
            if current_bgm != "title" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["title"])
                current_bgm = "title"
        elif state == GameState.INSTRUCTION:
            if current_bgm != "title" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["title"])
                current_bgm = "title"
        elif (state == GameState.PLAYING or state == GameState.RESULT or state == GameState.ROUND_START):
            if current_bgm != "play" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["play"])
                current_bgm = "play"
        elif state == GameState.GAME_FINISH:
            if current_bgm != "finish" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["finish"])
                current_bgm = "finish"

        if state == GameState.TITLE:
            drawing.draw_title_screen(screen, background_surface, floating_images)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue
        elif state == GameState.INSTRUCTION:
            drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)
            drawing.draw_instruction_screen(screen, background_surface, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue

        current_frame = cam.get_frame()
        if current_frame is not None:
            frame = current_frame
        else:
            print("カメラフレームの取得に失敗しました。直前のフレームを使用します。")

        if frame_count % 5 == 0:
            new_result, _ = recognizer.analyze(frame)
            if new_result and isinstance(new_result, dict) and 'top_emotion' in new_result:
                result = new_result
                emotion_history.append(result['top_emotion'])
                count = Counter(emotion_history)
                smoothed_emotion = count.most_common(1)[0][0]
            else:
                emotion_history.append('探し中...')
                count = Counter(emotion_history)
                smoothed_emotion = count.most_common(1)[0][0]
                result['top_emotion'] = '探し中...'

        drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)

        if state == GameState.ROUND_START:
            drawing.draw_round_start_screen(screen, game_manager, CAM_WIDTH, CAM_HEIGHT)
        elif state == GameState.PLAYING:
            drawing.draw_playing_screen(screen, game_manager, timer_display, CAM_WIDTH, CAM_HEIGHT)
        elif state == GameState.RESULT:
            drawing.draw_result_screen(screen, game_manager, CAM_WIDTH, CAM_HEIGHT)
        elif state == GameState.GAME_FINISH:
            drawing.draw_finish_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)

        if state != GameState.GAME_FINISH:
            drawing.draw_common_ui(screen, game_manager, CAM_WIDTH, CAM_HEIGHT, life_display)

        pygame.display.flip()
        clock.tick(game_manager.fps)
        frame_count += 1

    print("終了します...")
    cam.release()
    pygame.time.wait(300)
    pygame.quit()
    sys.exit(1)


if __name__ == "__main__":
    main()
