"""Camera, round, result, and finish screens."""

from ...core import settings
from ...core.utils import draw_text, render_frame, render_image
from ..ui_elements import LifeDisplay
from .common import draw_back_hint as _draw_back_hint
from .common import draw_text_chip as _draw_text_chip


def draw_game_background(surface, background_surface, frame, result, smoothed_emotion, cam_width):
    surface.blit(background_surface, (0, 0))
    render_frame(surface, frame, result, cam_width, 0)
    right_edge = surface.get_width() - 20

    _draw_text_chip(
        surface,
        f"あなた: {smoothed_emotion}",
        right=right_edge,
        top=64,
        size=24,
        chip_width=300,
        chip_height=44,
    )


def draw_developer_screen(
    surface,
    background_surface,
    frame,
    result,
    cam_width,
    display_fps=0.0,
    frame_time_ms=0,
):
    screen_h = surface.get_height()

    surface.blit(background_surface, (0, 0))
    render_frame(surface, frame, result, cam_width, 0)
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, screen_h))

    status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"
    reason = result.get("reason", "") if isinstance(result, dict) else ""
    top_emotion = (
        result.get("top_emotion", "探し中...") if isinstance(result, dict) else "探し中..."
    )
    latency_ms = result.get("latency_ms", 0.0) if isinstance(result, dict) else 0.0
    face_detected = result.get("face_detected", False) if isinstance(result, dict) else False
    emotion_success = result.get("emotion_success", False) if isinstance(result, dict) else False
    detector = result.get("detector", "-") if isinstance(result, dict) else "-"
    classifier = result.get("classifier", "-") if isinstance(result, dict) else "-"
    box = result.get("box") if isinstance(result, dict) else None

    if status == "ok":
        status_text = "OK"
        status_color = settings.ACCENT_GREEN
    elif status == "no_face":
        status_text = "顔検出失敗"
        status_color = settings.ACCENT_RED
    elif status == "emotion_error":
        status_text = "感情分類失敗"
        status_color = settings.ACCENT_RED
    else:
        status_text = status
        status_color = settings.TEXT_DARK

    y = 20
    draw_text(surface, "開発者モード", (20, y), size=36)
    y += 52
    draw_text(surface, f"状態: {status_text}", (20, y), color=status_color, size=30)
    y += 44
    draw_text(surface, f"感情: {top_emotion}", (20, y), size=28)
    y += 40
    draw_text(surface, f"顔検出: {'成功' if face_detected else '失敗'}", (20, y), size=24)
    y += 34
    draw_text(surface, f"感情分類: {'成功' if emotion_success else '失敗'}", (20, y), size=24)
    y += 34
    draw_text(surface, f"遅延: {latency_ms} ms", (20, y), size=24)
    y += 34
    draw_text(surface, f"detector: {detector}", (20, y), size=20)
    y += 30
    draw_text(surface, f"classifier: {classifier}", (20, y), size=20)
    y += 30
    draw_text(surface, f"display: {display_fps:.1f} FPS / {frame_time_ms} ms", (20, y), size=20)
    y += 30

    if box and isinstance(box, dict):
        draw_text(
            surface,
            f"box: x={box.get('x')} y={box.get('y')} w={box.get('w')} h={box.get('h')}",
            (20, y),
            size=20,
        )
        y += 30
    else:
        draw_text(surface, "box: None", (20, y), size=20)
        y += 30

    if reason:
        draw_text(surface, f"reason: {reason[:52]}", (20, y), size=20)

    draw_text(surface, "[R] タイトルへ戻る", (20, screen_h - 40), size=24)


def draw_round_start_screen(surface, game_manager, cam_width, cam_height):
    font = settings.get_font(80)

    panel_center_x = cam_width // 2
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, cam_height))

    text = f"ラウンド {game_manager.current_round}"
    text_surf = font.render(text, True, settings.TEXT_DARK)
    text_rect = text_surf.get_rect(center=(panel_center_x, cam_height // 2))
    surface.blit(text_surf, text_rect)


def draw_playing_screen(surface, game_manager, timer_display, cam_width, cam_height):
    num_npcs = len(game_manager.npc_emotions)
    base_x, base_y, base_w, base_h = 0, 0, cam_width, cam_height
    surface.fill(settings.WII_BACKGROUND, (base_x, base_y, base_w, base_h))

    if num_npcs == 1:
        npc_emotion = game_manager.npc_emotions[0]
        npc_image_path = game_manager.emotion_images.get(npc_emotion, "")
        render_image(surface, npc_image_path, base_x, base_y, base_w, base_h, fill_bg=False)

    elif num_npcs == 2:
        half_w = base_w // 2
        npc_emotion1 = game_manager.npc_emotions[0]
        npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
        render_image(surface, npc_image_path1, base_x, base_y, half_w, base_h, fill_bg=False)

        npc_emotion2 = game_manager.npc_emotions[1]
        npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
        render_image(
            surface, npc_image_path2, base_x + half_w, base_y, half_w, base_h, fill_bg=False
        )

    elif num_npcs >= 3:
        half_w = base_w // 2
        half_h = base_h // 2
        npc_emotion1 = game_manager.npc_emotions[0]
        npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
        render_image(surface, npc_image_path1, base_x, base_y, half_w, half_h, fill_bg=False)

        npc_emotion2 = game_manager.npc_emotions[1]
        npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
        render_image(
            surface, npc_image_path2, base_x + half_w, base_y, half_w, half_h, fill_bg=False
        )

        npc_emotion3 = game_manager.npc_emotions[2]
        npc_image_path3 = game_manager.emotion_images.get(npc_emotion3, "")
        render_image(
            surface, npc_image_path3, base_x, base_y + half_h, half_w, half_h, fill_bg=False
        )

        if num_npcs >= 4:
            npc_emotion4 = game_manager.npc_emotions[3]
            npc_image_path4 = game_manager.emotion_images.get(npc_emotion4, "")
            render_image(
                surface,
                npc_image_path4,
                base_x + half_w,
                base_y + half_h,
                half_w,
                half_h,
                fill_bg=False,
            )

    timer_display.update(game_manager.timer_sec)
    timer_display.draw()


def draw_result_screen(surface, game_manager, cam_width, cam_height):
    font_m = settings.get_font(28)
    font_l = settings.get_font(70)

    panel_center_x = cam_width // 2
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, cam_height))

    text_surf = font_m.render(f"ラウンド {game_manager.current_round}", True, settings.TEXT_DARK)
    text_rect = text_surf.get_rect(centerx=panel_center_x, top=40)
    surface.blit(text_surf, text_rect)

    npc_area_x = 0
    npc_area_y = 120
    npc_area_w = panel_center_x - 40
    npc_area_h = 200

    num_npcs = len(game_manager.npc_emotions)

    if num_npcs == 1:
        npc_img_path = game_manager.emotion_images.get(
            game_manager.npc_emotions[0], settings.QUESTION_IMAGE_PATH
        )
        render_image(
            surface, npc_img_path, npc_area_x, npc_area_y, npc_area_w, npc_area_h, fill_bg=False
        )

    elif num_npcs == 2:
        half_w = npc_area_w // 2
        npc_img_path1 = game_manager.emotion_images.get(
            game_manager.npc_emotions[0], settings.QUESTION_IMAGE_PATH
        )
        render_image(
            surface, npc_img_path1, npc_area_x, npc_area_y, half_w, npc_area_h, fill_bg=False
        )

        npc_img_path2 = game_manager.emotion_images.get(
            game_manager.npc_emotions[1], settings.QUESTION_IMAGE_PATH
        )
        render_image(
            surface,
            npc_img_path2,
            npc_area_x + half_w,
            npc_area_y,
            half_w,
            npc_area_h,
            fill_bg=False,
        )

    elif num_npcs >= 3:
        half_w = npc_area_w // 2
        half_h = npc_area_h // 2
        npc_img_path1 = game_manager.emotion_images.get(
            game_manager.npc_emotions[0], settings.QUESTION_IMAGE_PATH
        )
        render_image(surface, npc_img_path1, npc_area_x, npc_area_y, half_w, half_h, fill_bg=False)

        npc_img_path2 = game_manager.emotion_images.get(
            game_manager.npc_emotions[1], settings.QUESTION_IMAGE_PATH
        )
        render_image(
            surface, npc_img_path2, npc_area_x + half_w, npc_area_y, half_w, half_h, fill_bg=False
        )

        npc_img_path3 = game_manager.emotion_images.get(
            game_manager.npc_emotions[2], settings.QUESTION_IMAGE_PATH
        )
        render_image(
            surface, npc_img_path3, npc_area_x, npc_area_y + half_h, half_w, half_h, fill_bg=False
        )

        if num_npcs >= 4:
            npc_img_path4 = game_manager.emotion_images.get(
                game_manager.npc_emotions[3], settings.QUESTION_IMAGE_PATH
            )
            render_image(
                surface,
                npc_img_path4,
                npc_area_x + half_w,
                npc_area_y + half_h,
                half_w,
                half_h,
                fill_bg=False,
            )

    player_area_x = panel_center_x + 40
    player_area_y = 120
    player_area_w = panel_center_x - 40
    player_area_h = 200

    player_img_path = game_manager.emotion_images.get(
        game_manager.player_emotion, settings.QUESTION_IMAGE_PATH
    )
    render_image(
        surface,
        player_img_path,
        player_area_x,
        player_area_y,
        player_area_w,
        player_area_h,
        fill_bg=False,
    )

    vs_surf = font_m.render("VS", True, settings.TEXT_DARK)
    vs_rect = vs_surf.get_rect(centerx=panel_center_x, centery=npc_area_y + npc_area_h // 2)
    surface.blit(vs_surf, vs_rect)

    outcome = game_manager.last_round_outcome
    if outcome == "success":
        result_text = "成功！"
        result_color = settings.ACCENT_GREEN
    else:
        result_text = "失敗..."
        result_color = settings.ACCENT_RED

    result_surf = font_l.render(result_text, True, result_color)
    result_rect = result_surf.get_rect(centerx=panel_center_x, top=320)
    surface.blit(result_surf, result_rect)

    if game_manager.lives <= 0:
        nav_text = "[S] 最終結果へ"
    else:
        nav_text = "[S] 次のラウンドへ"

    nav_font = font_m
    nav_max_width = panel_center_x - 36
    nav_size = 28
    while nav_size >= 22:
        nav_font_try = settings.get_font(nav_size)
        nav_surf_try = nav_font_try.render(nav_text, True, settings.TEXT_DARK)
        if nav_surf_try.get_width() <= nav_max_width:
            nav_font = nav_font_try
            nav_surf = nav_surf_try
            break
        nav_size -= 1
    else:
        nav_surf = nav_font.render(nav_text, True, settings.TEXT_DARK)

    nav_rect = nav_surf.get_rect()
    nav_rect.right = cam_width - 20
    nav_rect.bottom = cam_height - 18
    surface.blit(nav_surf, nav_rect)

    _draw_back_hint(surface, text="[ESC] 戻る", left=20, bottom=18, size=22)


def draw_finish_screen(surface, background_surface, game_manager, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))

    font_l = settings.get_font(80)
    font_m = settings.get_font(40)

    title = settings.theme_text("finish_title", "ゲーム終了")
    score_text = f"スコア: {game_manager.score}"
    restart_text = "[R] タイトルへ戻る  /  [S] もう一度遊ぶ"

    title_surf = font_l.render(title, True, settings.TEXT_DARK)
    score_surf = font_m.render(score_text, True, settings.TEXT_DARK)
    restart_surf = font_m.render(restart_text, True, settings.TEXT_DARK)

    cx = screen_w // 2
    surface.blit(title_surf, title_surf.get_rect(center=(cx, screen_h // 2 - 80)))
    surface.blit(score_surf, score_surf.get_rect(center=(cx, screen_h // 2)))
    surface.blit(restart_surf, restart_surf.get_rect(center=(cx, screen_h // 2 + 80)))

    if getattr(game_manager, "new_personal_best", False):
        font_flag = settings.get_font(28)
        flag_surf = font_flag.render("ハイスコア更新！", True, settings.ACCENT_GREEN)
        surface.blit(flag_surf, flag_surf.get_rect(center=(cx, screen_h // 2 + 160)))


def draw_common_ui(surface, game_manager, cam_width, cam_height, life_display: LifeDisplay):
    screen_w = surface.get_width()
    screen_h = surface.get_height()

    try:
        life_display.draw(game_manager.lives)
    except Exception:
        pass

    right_edge = screen_w - 20
    chip_width = 300
    chip_height = 44
    player_name = getattr(game_manager, "player_name", "名無し")

    _draw_text_chip(
        surface,
        f"名前: {player_name}",
        right=right_edge,
        top=12,
        size=24,
        chip_width=chip_width,
        chip_height=chip_height,
    )

    if getattr(game_manager, "new_personal_best", False):
        _draw_text_chip(
            surface,
            "スコア更新中！",
            right=right_edge,
            top=116,
            size=22,
            text_color=settings.ACCENT_GREEN,
            chip_width=200,
            chip_height=40,
        )

    score_color, use_spine = settings.get_score_style(game_manager.score)
    score_y = screen_h - 64

    _draw_text_chip(
        surface,
        f"Score: {game_manager.score}",
        left=20,
        top=score_y,
        size=28,
        text_color=score_color,
        use_spine_font=use_spine,
        chip_width=240,
        chip_height=50,
    )
