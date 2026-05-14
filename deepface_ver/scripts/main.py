# main moved into scripts (imports updated to package paths)
import sys
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, K_q, K_s, K_b, K_e, K_n, K_h, K_r
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
    from ..core import highscore
    from ..ui import drawing
    from ..ui.ui_elements import FloatingImage, Timer, LifeDisplay
    from ..ui.name_select import NameSelector
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
        icon_path=settings.CLOCK_IMAGE_PATH,
        font_path=settings.FONT_PATH,
        font_size=40,
        text_color=settings.TEXT_DARK,
        bg_color=settings.WII_TRANSLUCENT_BG,
        shadow_color = settings.WII_SHADOW_COLOR
    )

    life_display = LifeDisplay(
        screen_surface = screen,
        icon_path = settings.HEART_IMAGE_PATH,
        icon_size = 60,
        pos = (0, 0),
        max_lives = 3,
        spacing = 1
    )

    recognizer = EmotionRecognizer_gpt(scale_factor=0.75, backend="opencv")
    recognizer.start()
    game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT, sounds)
    selector = NameSelector()
    current_player_name = "名無し"
    game_manager.player_name = current_player_name
    game_manager.new_personal_best = False

    emotion_history = deque(maxlen=settings.RECOGNITION_HISTORY_SIZE)
    smoothed_emotion = "探し中..."
    result = {
        'top_emotion': '探し中...',
        'box': None,
        'status': 'init',
        'reason': '初期化中',
        'face_detected': False,
        'emotion_success': False,
        'latency_ms': 0.0,
        'detector': 'opencv_haar',
        'classifier': 'deepface_emotion_skip',
    }
    last_result_gen = -1
    developer_mode = False
    dev_code_buffer = deque(maxlen=3)

    floating_images = []
    try:
        image_paths = list(game_manager.emotion_images.values())
        if not image_paths:
            image_paths = [settings.CLOCK_IMAGE_PATH]
        for _ in range(10):
            path = random.choice(image_paths)
            floating_images.append(FloatingImage(path, SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"FloatingImage の初期化エラー: {e}")

    frame = frame_for_size
    frame_count = 0
    running = True

    current_bgm = None
    prev_state = None

    while running:
        # 変数を初期化。物理キー依存の変数を廃止し、意味（cancel）で統一。
        s_key_pressed = cancel_key_pressed = e_key_pressed = n_key_pressed = h_key_pressed = r_key_pressed = False
        
        for event in pygame.event.get():
            # if event.type == pygame.QUIT:
            #     running = False
            #     break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        # Shift + ESC でゲーム終了
                        running = False
                        break
                    else:
                        # 単独の ESC はキャンセル操作
                        cancel_key_pressed = True
                        
                        # 名前選択画面が出ておらず、かつキャンセル可能な画面でのみSEを鳴らす
                        in_game_states = [GameState.COUNTDOWN, GameState.ROUND_START, GameState.PLAYING, GameState.JUDGE, GameState.RESULT]
                        if not selector.active and game_manager.state not in in_game_states:
                            sounds["select"].play()

                if event.key == K_s:
                    s_key_pressed = True
                    if not selector.active:
                        sounds["select"].play()
                
                # K_b および K_q は文字入力の邪魔になるため、システム操作からは完全に削除
                if event.key == K_e: e_key_pressed = True
                if event.key == K_n: n_key_pressed = True
                if event.key == K_h: h_key_pressed = True
                if event.key == K_r: r_key_pressed = True
            
            # NameSelectorがアクティブならイベントを流す（ESCキャンセル等の処理はNameSelector内で行う）
            if selector.active:
                selector.handle_event(event)
        
        if not running:
            break

        state = game_manager.state

        if state == GameState.EMOTION_MAP and s_key_pressed and not selector.active:
            selector.start()
        if state == GameState.SKIP_SELECTION and e_key_pressed and not selector.active:
            game_manager.skip_instruction = True
            selector.start()

        if selector.done:
            name = selector.get_result() or "名無し"
            current_player_name = name
            game_manager.player_name = current_player_name
            current_best = highscore.get_best_for_name(current_player_name, n=1)
            game_manager.personal_best_score = current_best[0] if current_best else 0
            game_manager.new_personal_best = False
            highscore.add_recent(current_player_name)
            game_manager.start_game()
            selector.done = False
            selector.active = False

        if selector.cancelled:
            selector.cancelled = False
            selector.active = False

        if prev_state != state and state == GameState.GAME_FINISH:
            try:
                is_new = highscore.update_if_better(game_manager.player_name if hasattr(game_manager, 'player_name') else "名無し", game_manager.score)
                game_manager.new_personal_best = bool(is_new)
            except Exception:
                game_manager.new_personal_best = False
        prev_state = state

        if not developer_mode and state == GameState.TITLE:
            if e_key_pressed: dev_code_buffer.append("E")
            if n_key_pressed: dev_code_buffer.append("N")
            if h_key_pressed: dev_code_buffer.append("H")

            if list(dev_code_buffer) == ["E", "N", "H"]:
                developer_mode = True
                dev_code_buffer.clear()
                emotion_history.clear()
                smoothed_emotion = "探し中..."

        if developer_mode and r_key_pressed:
            developer_mode = False
            dev_code_buffer.clear()
            game_manager.state = GameState.TITLE
            emotion_history.clear()
            smoothed_emotion = "探し中..."

        skip_emotion_states = [
            GameState.TITLE, GameState.SKIP_SELECTION, GameState.INSTRUCTION,
            GameState.EMOTION_MAP, GameState.COUNTDOWN
        ]
        if developer_mode or (state not in skip_emotion_states and not selector.active):
            current_frame = cam.get_frame()
            if current_frame is not None:
                frame = current_frame
                recognizer.submit_frame(frame)

            new_result, gen = recognizer.get_latest_result()
            if gen != last_result_gen:
                last_result_gen = gen
                result = new_result
                if developer_mode:
                    smoothed_emotion = result.get('top_emotion', '探し中...')
                else:
                    emotion_history.append(result['top_emotion'])
                    count = Counter(emotion_history)
                    smoothed_emotion = count.most_common(1)[0][0]

        if not developer_mode and not selector.active:
            # 物理キー依存の変数を渡しやめ、意味的なフラグ (cancel_key_pressed) を渡す
            game_manager.update(
                smoothed_emotion,
                s_key_pressed,
                cancel_key_pressed, 
                e_key_pressed,
                n_key_pressed,
                h_key_pressed,
                r_key_pressed
            )

        state = game_manager.state
        is_bgm_playing = pygame.mixer.music.get_busy()

        if developer_mode:
            if current_bgm != "title" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["title"])
                current_bgm = "title"
        elif state in (GameState.TITLE, GameState.SKIP_SELECTION, GameState.INSTRUCTION, GameState.EMOTION_MAP):
            if current_bgm != "title" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["title"])
                current_bgm = "title"
        elif state in (GameState.COUNTDOWN, GameState.PLAYING, GameState.RESULT, GameState.ROUND_START):
            if current_bgm != "play" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["play"])
                current_bgm = "play"
        elif state == GameState.GAME_FINISH:
            if current_bgm != "finish" or not is_bgm_playing:
                utils.play_bgm(settings.BGM_PATHS["finish"])
                current_bgm = "finish"

        if developer_mode:
            drawing.draw_developer_screen(screen, background_surface, frame, result, CAM_WIDTH)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue

        if selector.active:
            drawing.draw_name_select_screen(screen, background_surface, selector, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue

        if state == GameState.TITLE:
            title_rect = drawing.draw_title_screen(screen, background_surface, floating_images)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue
        elif state == GameState.SKIP_SELECTION:
            drawing.draw_skip_selection_screen(screen, background_surface, SCREEN_WIDTH, SCREEN_HEIGHT)
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
        elif state == GameState.EMOTION_MAP:
            drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)
            drawing.draw_emotion_map_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue
        elif state == GameState.COUNTDOWN:
            drawing.draw_countdown_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.display.flip()
            clock.tick(game_manager.fps)
            frame_count += 1
            continue

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

    recognizer.stop()
    cam.release()
    pygame.time.wait(300)
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())



# # main moved into scripts (imports updated to package paths)
# import sys
# import pygame
# from pygame.locals import KEYDOWN, K_ESCAPE, K_q, K_s, K_b, K_e, K_n, K_h, K_r
# from collections import deque, Counter
# import random
# import pygame.mixer

# try:
#     from ..emo.emo_recog import CameraManager_gpt, EmotionRecognizer_gpt
#     from ..core.game_manager import GameManager, GameState
# except ImportError as e:
#     print(f"エラー: 必要なモジュールが見つかりません。({e})")
#     sys.exit(1)

# try:
#     from ..core import settings
#     from ..core import utils
#     from ..core import highscore
#     from ..ui import drawing
#     from ..ui.ui_elements import FloatingImage, Timer, LifeDisplay
#     from ..ui.name_select import NameSelector
# except ImportError as e:
#     print(f"エラー: 自作モジュールが見つかりません。({e})")
#     sys.exit(1)


# def main():
#     pygame.init()
#     pygame.font.init()

#     try:
#         cam = CameraManager_gpt()
#     except RuntimeError as e:
#         print(f"カメラエラー: {e}")
#         pygame.quit()
#         sys.exit(1)
#     except Exception as e:
#         print(f"カメラ初期化中に予期せぬエラー: {e}")
#         pygame.quit()
#         sys.exit(1)

#     frame_for_size = cam.get_frame()
#     if frame_for_size is None:
#         print("カメラから初期フレームを取得できません。")
#         cam.release()
#         pygame.quit()
#         sys.exit(1)

#     CAM_WIDTH, CAM_HEIGHT = frame_for_size.shape[1], frame_for_size.shape[0]
#     SCREEN_WIDTH = CAM_WIDTH * 2
#     SCREEN_HEIGHT = CAM_HEIGHT

#     try:
#         screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#         pygame.display.set_caption("あまのじゃくゲーム")
#     except pygame.error as e:
#         print(f"画面の初期化に失敗しました: {e}")
#         cam.release()
#         pygame.quit()
#         sys.exit(1)

#     clock = pygame.time.Clock()

#     try:
#         sounds = {
#             "select": pygame.mixer.Sound(settings.SE_PATHS["select"]),
#             "count": pygame.mixer.Sound(settings.SE_PATHS["count"]),
#             "success": pygame.mixer.Sound(settings.SE_PATHS["success"]),
#             "fail": pygame.mixer.Sound(settings.SE_PATHS["fail"]),
#         }
#         sounds["count"].set_volume(0.5)
#     except Exception as e:
#         print(f"SEの読み込みエラー: {e}")
#         pygame.quit()
#         sys.exit(1)

#     background_surface = utils.create_checkerboard_surface(
#         SCREEN_WIDTH, SCREEN_HEIGHT, 
#         settings.WII_BACKGROUND, settings.WII_BROWN, 
#         settings.TILE_SIZE
#     )

#     timer_display = Timer(
#         screen_surface=screen,
#         pos=(CAM_WIDTH // 2 - 70, 10),
#         icon_path=settings.CLOCK_IMAGE_PATH,
#         font_path=settings.FONT_PATH,
#         font_size=40,
#         text_color=settings.TEXT_DARK,
#         bg_color=settings.WII_TRANSLUCENT_BG,
#         shadow_color = settings.WII_SHADOW_COLOR
#     )

#     life_display = LifeDisplay(
#         screen_surface = screen,
#         icon_path = settings.HEART_IMAGE_PATH,
#         icon_size = 60,
#         pos = (0, 0),
#         max_lives = 3,
#         spacing = 1
#     )

#     recognizer = EmotionRecognizer_gpt(scale_factor=0.75, backend="opencv")
#     recognizer.start()  # バックグラウンドスレッドで感情認識を開始
#     game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT, sounds)
#     selector = NameSelector()
#     current_player_name = "名無し"
#     game_manager.player_name = current_player_name
#     game_manager.new_personal_best = False

#     emotion_history = deque(maxlen=settings.RECOGNITION_HISTORY_SIZE)
#     smoothed_emotion = "探し中..."
#     result = {
#         'top_emotion': '探し中...',
#         'box': None,
#         'status': 'init',
#         'reason': '初期化中',
#         'face_detected': False,
#         'emotion_success': False,
#         'latency_ms': 0.0,
#         'detector': 'opencv_haar',
#         'classifier': 'deepface_emotion_skip',
#     }
#     last_result_gen = -1  # 結果の世代番号を追跡
#     developer_mode = False
#     dev_code_buffer = deque(maxlen=3)

#     floating_images = []
#     try:
#         image_paths = list(game_manager.emotion_images.values())
#         if not image_paths:
#             image_paths = [settings.CLOCK_IMAGE_PATH]
#         for _ in range(10):
#             path = random.choice(image_paths)
#             floating_images.append(FloatingImage(path, SCREEN_WIDTH, SCREEN_HEIGHT))
#     except Exception as e:
#         print(f"FloatingImage の初期化エラー: {e}")

#     frame = frame_for_size
#     frame_count = 0
#     running = True

#     current_bgm = None

#     prev_state = None
#     while running:
#         s_key_pressed = b_key_pressed = e_key_pressed = n_key_pressed = h_key_pressed = r_key_pressed = False
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#                 break
#             if event.type == KEYDOWN:
#                 if event.key == K_ESCAPE or event.key == K_q:
#                     running = False
#                     break
#                 if event.key == K_s:
#                     s_key_pressed = True
#                     if not selector.active:#名前選択時はセレクタに渡すだけで効果音は鳴らさない
#                         sounds["select"].play()
#                 if event.key == K_b:
#                     b_key_pressed = True
#                     if not selector.active: #名前選択時はセレクタに渡すだけで効果音は鳴らさない
#                         sounds["select"].play()
#                 if event.key == K_e: e_key_pressed = True
#                 if event.key == K_n: n_key_pressed = True
#                 if event.key == K_h: h_key_pressed = True
#                 if event.key == K_r: r_key_pressed = True
#             # pass event to selector if active
#             if selector.active:
#                 selector.handle_event(event)
#         if not running:
#             break

#         if selector.active and b_key_pressed:
#             selector.cancelled = True
#             selector.active = False

#         state = game_manager.state
#         # handle name selector activation on emotion_map or skip selection + E key
#         if state == GameState.EMOTION_MAP and s_key_pressed and not selector.active:
#             selector.start()
#         if state == GameState.SKIP_SELECTION and e_key_pressed and not selector.active:
#             # スキップ選択: 説明なしで名前選択へ
#             game_manager.skip_instruction = True
#             selector.start()

#         # consume selector result regardless of active flag
#         if selector.done:
#             name = selector.get_result() or "名無し"
#             current_player_name = name
#             game_manager.player_name = current_player_name
#             current_best = highscore.get_best_for_name(current_player_name, n=1)
#             game_manager.personal_best_score = current_best[0] if current_best else 0
#             game_manager.new_personal_best = False
#             highscore.add_recent(current_player_name)
#             game_manager.start_game()
#             selector.done = False
#             selector.active = False

#         if selector.cancelled:
#             selector.cancelled = False
#             selector.active = False

#         # detect state transitions for highscore update
#         if prev_state != state and state == GameState.GAME_FINISH:
#             try:
#                 is_new = highscore.update_if_better(game_manager.player_name if hasattr(game_manager, 'player_name') else "名無し", game_manager.score)
#                 game_manager.new_personal_best = bool(is_new)
#             except Exception:
#                 game_manager.new_personal_best = False
#         prev_state = state

#         if not developer_mode and state == GameState.TITLE:
#             if e_key_pressed:
#                 dev_code_buffer.append("E")
#             if n_key_pressed:
#                 dev_code_buffer.append("N")
#             if h_key_pressed:
#                 dev_code_buffer.append("H")

#             if list(dev_code_buffer) == ["E", "N", "H"]:
#                 developer_mode = True
#                 dev_code_buffer.clear()
#                 emotion_history.clear()
#                 smoothed_emotion = "探し中..."

#         if developer_mode and r_key_pressed:
#             developer_mode = False
#             dev_code_buffer.clear()
#             game_manager.state = GameState.TITLE
#             emotion_history.clear()
#             smoothed_emotion = "探し中..."

#         # ─── カメラ取得 + 感情認識結果を更新（game_manager.update の前に！） ───
#         #  新規状態では名前選択含むまで感情認識不要
#         state = game_manager.state
        
#         # ROUND_START 以降ならカメラ＋感情を更新
#         skip_emotion_states = [
#             GameState.TITLE, GameState.SKIP_SELECTION, GameState.INSTRUCTION,
#             GameState.EMOTION_MAP, GameState.COUNTDOWN
#         ]
#         if developer_mode or (state not in skip_emotion_states and not selector.active):
#             current_frame = cam.get_frame()
#             if current_frame is not None:
#                 frame = current_frame
#                 recognizer.submit_frame(frame)

#             # 最新の感情認識結果を取得（即座に返る、ブロックしない）
#             new_result, gen = recognizer.get_latest_result()
#             if gen != last_result_gen:
#                 last_result_gen = gen
#                 result = new_result
#                 if developer_mode:
#                     smoothed_emotion = result.get('top_emotion', '探し中...')
#                 else:
#                     emotion_history.append(result['top_emotion'])
#                     count = Counter(emotion_history)
#                     smoothed_emotion = count.most_common(1)[0][0]

#         if not developer_mode and not selector.active:
#             game_manager.update(
#                 smoothed_emotion,
#                 s_key_pressed,
#                 b_key_pressed,
#                 e_key_pressed,
#                 n_key_pressed,
#                 h_key_pressed,
#                 r_key_pressed
#             )

#         state = game_manager.state
#         is_bgm_playing = pygame.mixer.music.get_busy()

#         # BGM 切り替え
#         if developer_mode:
#             if current_bgm != "title" or not is_bgm_playing:
#                 utils.play_bgm(settings.BGM_PATHS["title"])
#                 current_bgm = "title"
#         elif state in (GameState.TITLE, GameState.SKIP_SELECTION, GameState.INSTRUCTION, GameState.EMOTION_MAP):
#             if current_bgm != "title" or not is_bgm_playing:
#                 utils.play_bgm(settings.BGM_PATHS["title"])
#                 current_bgm = "title"
#         elif state in (GameState.COUNTDOWN, GameState.PLAYING, GameState.RESULT, GameState.ROUND_START):
#             if current_bgm != "play" or not is_bgm_playing:
#                 utils.play_bgm(settings.BGM_PATHS["play"])
#                 current_bgm = "play"
#         elif state == GameState.GAME_FINISH:
#             if current_bgm != "finish" or not is_bgm_playing:
#                 utils.play_bgm(settings.BGM_PATHS["finish"])
#                 current_bgm = "finish"

#         if developer_mode:
#             drawing.draw_developer_screen(screen, background_surface, frame, result, CAM_WIDTH)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue

#         if selector.active:
#             # draw name selection screen
#             drawing.draw_name_select_screen(screen, background_surface, selector, SCREEN_WIDTH, SCREEN_HEIGHT)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue

#         if state == GameState.TITLE:
#             title_rect = drawing.draw_title_screen(screen, background_surface, floating_images)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue
#         elif state == GameState.SKIP_SELECTION:
#             drawing.draw_skip_selection_screen(screen, background_surface, SCREEN_WIDTH, SCREEN_HEIGHT)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue
#         elif state == GameState.INSTRUCTION:
#             drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)
#             drawing.draw_instruction_screen(screen, background_surface, SCREEN_WIDTH, SCREEN_HEIGHT)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue
#         elif state == GameState.EMOTION_MAP:
#             drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)
#             drawing.draw_emotion_map_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue
#         elif state == GameState.COUNTDOWN:
#             drawing.draw_countdown_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)
#             pygame.display.flip()
#             clock.tick(game_manager.fps)
#             frame_count += 1
#             continue

#         drawing.draw_game_background(screen, background_surface, frame, result, smoothed_emotion, CAM_WIDTH)

#         if state == GameState.ROUND_START:
#             drawing.draw_round_start_screen(screen, game_manager, CAM_WIDTH, CAM_HEIGHT)
#         elif state == GameState.PLAYING:
#             drawing.draw_playing_screen(screen, game_manager, timer_display, CAM_WIDTH, CAM_HEIGHT)
#         elif state == GameState.RESULT:
#             drawing.draw_result_screen(screen, game_manager, CAM_WIDTH, CAM_HEIGHT)
#         elif state == GameState.GAME_FINISH:
#             drawing.draw_finish_screen(screen, background_surface, game_manager, SCREEN_WIDTH, SCREEN_HEIGHT)

#         if state != GameState.GAME_FINISH:
#             drawing.draw_common_ui(screen, game_manager, CAM_WIDTH, CAM_HEIGHT, life_display)

#         pygame.display.flip()
#         clock.tick(game_manager.fps)
#         frame_count += 1

#     recognizer.stop()  # 感情認識スレッドを停止
#     cam.release()
#     pygame.time.wait(300)
#     pygame.quit()
#     return 0


# if __name__ == "__main__":
#     sys.exit(main())
