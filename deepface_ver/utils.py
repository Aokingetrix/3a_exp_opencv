# utils.py
import pygame
import cv2
import settings # 自作の定数モジュール

def draw_text(surface, text, pos, color = settings.TEXT_DARK, size=24):
    """
    Pygameでテキストを描画する関数 (日本語対応)
    """
    try:
        # FONT_PATH が None の場合、pygame.font.Font はデフォルトフォントを使用する
        font = pygame.font.Font(settings.FONT_PATH, size)
    except IOError:
        # FONT_PATH が None 以外で見つからなかった場合
        print(f"警告: フォント '{settings.FONT_PATH}' が見つかりません。デフォルトフォントを使用します。")
        font = pygame.font.Font(None, size + 4) # デフォルトフォント
    except Exception as e:
        print(f"フォント読み込みエラー: {e}")
        font = pygame.font.Font(None, size + 4) # デフォルトフォント
        
    surface.blit(font.render(text, True, color), pos)

def render_frame(surface, frame, result, x, y):
    """
    OpenCVのフレーム(BGR)をPygame用に変換し、左右反転して描画する
    """
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_flipped = cv2.flip(frame_rgb, 1)
        
        # result が None や box を含まない可能性に対処
        box = result.get('box') if isinstance(result, dict) else None
        
        if box:
            try:
                frame_width = frame.shape[1]
                bx, by, bw, bh = box['x'], box['y'], box['w'], box['h']
                # 座標がintであることを保証
                bx, by, bw, bh = int(bx), int(by), int(bw), int(bh)
                
                flipped_x = frame_width - bx - bw
                cv2.rectangle(frame_flipped, (flipped_x, by), (flipped_x + bw, by + bh), (0, 255, 0), 2)
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
    """
    指定された2色でチェック模様のSurfaceを生成する関数
    """
    background_surface = pygame.Surface((width, height))
    
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            if (x // tile_size + y // tile_size) % 2 == 0:
                color = color1
            else:
                color = color2
            
            pygame.draw.rect(background_surface, color, (x, y, tile_size, tile_size))
            
    return background_surface

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
            raise pygame.error(f"画像サイズが0です: {image_path}")

        img_aspect = img_w / img_h
        area_aspect = w / h

        if img_aspect > area_aspect:
            # 幅基準でスケーリング
            new_w = int(w)
            new_h = int(new_w / img_aspect)
        else:
            # 高さ基準でスケーリング
            new_h = int(h)
            new_w = int(new_h * img_aspect)
            
        scaled_surface = pygame.transform.scale(image_surface, (new_w, new_h))

        draw_x = x + (w - new_w) // 2
        draw_y = y + (h - new_h) // 2

        if fill_bg:
            # settings.py の定数を使う
            surface.fill(settings.WII_BACKGROUND, (x, y, w, h)) 

        surface.blit(scaled_surface, (draw_x, draw_y))

    except (pygame.error, FileNotFoundError, ZeroDivisionError) as e:
        print(f"画像エラー (パス: {image_path}): {e}")
        # エラー時は黒い四角形を描画
        pygame.draw.rect(surface, (0,0,0), (x,y,w,h))
    except Exception as e:
        print(f"予期せぬ画像エラー: {e}")
        pygame.draw.rect(surface, (255,0,0), (x,y,w,h)) # 予期せぬエラーは赤

def play_bgm(bgm_path):
    """BGMをループ再生する"""
    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.play(-1) # -1 で無限ループ
        pygame.mixer.music.set_volume(0.3) # BGMは小さめに
    except Exception as e:
        print(f"BGM再生エラー: {e} (パス: {bgm_path})")