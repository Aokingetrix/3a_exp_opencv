import pygame

from . import assets, settings


def draw_text(surface, text, pos, color=settings.TEXT_DARK, size=24):
    font = settings.get_font(size)
    surface.blit(font.render(text, True, color), pos)


# rest of functions


def render_frame(surface, frame, result, x, y):
    import cv2

    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_flipped = cv2.flip(frame_rgb, 1)
        box = result.get("box") if isinstance(result, dict) else None
        if box:
            try:
                frame_width = frame.shape[1]
                bx, by, bw, bh = box["x"], box["y"], box["w"], box["h"]
                bx, by, bw, bh = int(bx), int(by), int(bw), int(bh)
                flipped_x = frame_width - bx - bw
                cv2.rectangle(
                    frame_flipped, (flipped_x, by), (flipped_x + bw, by + bh), (0, 255, 0), 2
                )
            except Exception as e:
                print(f"顔枠の描画エラー: {e} (box: {box})")
        frame_pygame = frame_flipped.swapaxes(0, 1)
        frame_surface = pygame.surfarray.make_surface(frame_pygame)
        surface.blit(frame_surface, (x, y))
    except cv2.error as e:
        print(f"OpenCVエラー (render_frame): {e}")
    except Exception as e:
        print(f"描画エラー (render_frame): {e}")


def create_checkerboard_surface(width, height, color1, color2, tile_size):
    return assets.get_checkerboard(width, height, color1, color2, tile_size).copy()


def create_background_surface(width, height, image_path=None):
    """Create a cover-scaled theme background or the classic checkerboard."""
    fallback = create_checkerboard_surface(
        width,
        height,
        settings.WII_BACKGROUND,
        settings.WII_BROWN,
        settings.TILE_SIZE,
    )
    if not image_path:
        return fallback
    try:
        scaled, x, y = assets.get_cover_image(image_path, width, height)
        fallback.blit(scaled, (x, y))
        return fallback
    except (OSError, pygame.error) as error:
        print(f"背景画像の読み込みに失敗しました: {image_path}: {error}")
        return fallback


def render_image(surface, image_path, x, y, w, h, fill_bg=True):
    try:
        scaled_surface, offset_x, offset_y = assets.get_contained_image(image_path, w, h)
        draw_x = x + offset_x
        draw_y = y + offset_y
        if fill_bg:
            surface.fill(settings.WII_BACKGROUND, (x, y, w, h))
        surface.blit(scaled_surface, (draw_x, draw_y))
    except (pygame.error, FileNotFoundError, ZeroDivisionError) as e:
        print(f"画像エラー (パス: {image_path}): {e}")
        pygame.draw.rect(surface, (0, 0, 0), (x, y, w, h))
    except Exception as e:
        print(f"予期せぬ画像エラー: {e}")
        pygame.draw.rect(surface, (255, 0, 0), (x, y, w, h))


def play_bgm(bgm_path):
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)
    except Exception as e:
        print(f"BGM再生エラー: {e} (パス: {bgm_path})")
