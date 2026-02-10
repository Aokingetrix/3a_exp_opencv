# compatibility alias: ensure this module name refers to the canonical module object
import importlib, sys
sys.modules[__name__] = importlib.import_module("deepface_ver.ui.ui_elements")
        
        # 移動速度をランダム化 (ピクセル/フレーム)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-0.5, 0.5)
        
        # 遅すぎ防止
        if -0.2 < self.vx < 0.2: self.vx = 0.5 * random.choice([-1, 1])
        if -0.2 < self.vy < 0.2: self.vy = 0.3 * random.choice([-1, 1])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        # 画面端での反射 (壁にめり込まないように調整)
        if self.x <= 0:
            self.vx = abs(self.vx)
            self.x = 0
        elif self.x + self.w >= self.screen_w:
            self.vx = -abs(self.vx)
            self.x = self.screen_w - self.w
            
        if self.y <= 0:
            self.vy = abs(self.vy)
            self.y = 0
        elif self.y + self.h >= self.screen_h:
            self.vy = -abs(self.vy)
            self.y = self.screen_h - self.h

    def draw(self, surface):
        # 汎用関数 (utils.py) を使う
        render_image(surface, self.image_path, int(self.x), int(self.y), self.w, self.h, fill_bg=False)


class Timer:
    """
    タイマーのアイコンと残り秒数を描画するオブジェクト
    """
    def __init__(self, screen_surface, pos, icon_path, font_path, font_size, text_color, bg_color, shadow_color):
        self.screen = screen_surface
        self.pos = pos
        self.text_color = text_color
        self.bg_color = bg_color
        self.shadow_color = shadow_color
        self.padding = 8
        self.icon_gap = 10
        self.shadow_offset = 3
        self.icon_height = font_size # アイコンの高さをフォントサイズに合わせる
        
        # 1. アイコン画像の読み込み
        try:
            icon_surf_raw = pygame.image.load(icon_path)
            aspect_ratio = icon_surf_raw.get_width() / icon_surf_raw.get_height()
            self.icon_width = int(self.icon_height * aspect_ratio)
            self.icon_surface = pygame.transform.scale(icon_surf_raw, (self.icon_width, self.icon_height))
        except Exception as e:
            print(f"タイマーアイコンの読み込みエラー: {e} (パス: {icon_path})")
            self.icon_surface = None
            self.icon_width = 0

        # 2. フォントの準備
        try:
            self.font = pygame.font.Font(font_path, font_size)
        except IOError:
            print(f"警告: タイマー用フォント '{font_path}' が見つかりません。デフォルトフォントを使用します。")
            self.font = pygame.font.Font(None, font_size + 4) # デフォルトフォント
        except Exception as e:
            print(f"タイマーフォントエラー: {e}")
            self.font = pygame.font.Font(None, font_size + 4)

        # 3. 描画用サーフェスの初期化 (仮)
        self.text_surface = self.font.render("0.0", True, self.text_color)
        
    def update(self, remaining_seconds):
        """
        表示する残り秒数を更新する
        """
        text = f"{remaining_seconds:.1f}"
        self.text_surface = self.font.render(text, True, self.text_color)

    def draw(self):
        """
        ドロップシャドウ付きの半透明の角丸背景を含むタイマー全体を描画する
        """
        # 1. 描画する要素のサイズを計算
        text_width = self.text_surface.get_width()
        text_height = self.text_surface.get_height()
        
        # 2. 背景本体のサイズを計算
        total_width = self.padding + self.icon_width + self.icon_gap + text_width + self.padding
        total_height = max(self.icon_height, text_height) + (self.padding * 2)
        
        # 3. ★変更: Surface全体のサイズを計算 (影のオフセット分だけ大きくする)
        surface_width = total_width + self.shadow_offset
        surface_height = total_height + self.shadow_offset

        try:
            bg_surface = pygame.Surface((surface_width, surface_height), flags=pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 0)) # 完全に透明で初期化
        except ValueError as e:
            print(f"Pygameエラー: Surface作成失敗。 {e}")
            return 

        # 4. ★変更: 2段階で描画
        border_radius = total_height // 2 # 角丸の半径は本体の高さ基準

        # 4-1. 影の描画 (オフセットした位置に)
        shadow_rect = pygame.Rect(
            self.shadow_offset, self.shadow_offset, # 右下にずらす
            total_width, total_height
        )
        try:
            pygame.draw.rect(bg_surface, self.shadow_color, shadow_rect, border_radius=border_radius)
        except TypeError:
            pygame.draw.rect(bg_surface, self.shadow_color, shadow_rect) # フォールバック

        # 4-2. 背景本体の描画 (左上の(0, 0)の位置に)
        main_rect = pygame.Rect(0, 0, total_width, total_height)
        try:
            pygame.draw.rect(bg_surface, self.bg_color, main_rect, border_radius=border_radius)
        except TypeError:
            pygame.draw.rect(bg_surface, self.bg_color, main_rect) # フォールバック

        # 5. アイコンとテキストを、Surface上の「本体」部分に描画
        
        # (描画位置の計算は変更なし、(0,0)基準でOK)
        icon_x = self.padding
        icon_y = (total_height - self.icon_height) // 2
        if self.icon_surface:
            bg_surface.blit(self.icon_surface, (icon_x, icon_y))
            
        text_x = self.padding + self.icon_width + self.icon_gap
        text_y = (total_height - text_height) // 2
        bg_surface.blit(self.text_surface, (text_x, text_y))

        # 6. 完成したタイマーSurfaceを、画面の指定位置に一度で描画
        self.screen.blit(bg_surface, self.pos)

# (ui_elements.py の末尾に追加)

class LifeDisplay:
    """
    ライフ（ハート）を描画するオブジェクト
    """
    def __init__(self, screen_surface, icon_path, icon_size, pos, max_lives=3, spacing=5):
        self.screen = screen_surface
        self.pos = pos
        self.spacing = spacing # ハートとハートの隙間
        self.icon_size = icon_size
        
        # 1. アイコン画像の読み込み
        try:
            icon_surf_raw = pygame.image.load(icon_path)
            # 指定されたサイズにスケーリング
            self.icon_surface = pygame.transform.scale(icon_surf_raw, (icon_size, icon_size))
        except Exception as e:
            print(f"ライフアイコンの読み込みエラー: {e} (パス: {icon_path})")
            # エラー時はフォールバック（赤い四角形）
            self.icon_surface = pygame.Surface((icon_size, icon_size))
            self.icon_surface.fill((255, 0, 0))

        # 2. （おまけ）空のハート（ダメージ後）の画像も作っておく
        #     ここでは単純にアイコンを暗くします
        self.empty_icon_surface = self.icon_surface.copy()
        self.empty_icon_surface.fill((50, 50, 50), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.max_lives = max_lives

    def draw(self, current_lives):
        """
        現在のライフに応じてハートを描画する
        """
        draw_x = self.pos[0]
        draw_y = self.pos[1]
        
        for i in range(self.max_lives):
            if i < current_lives:
                # ライフがある場合は、通常のハート
                self.screen.blit(self.icon_surface, (draw_x, draw_y))
            else:
                # ライフがない場合は、暗いハート
                self.screen.blit(self.empty_icon_surface, (draw_x, draw_y))
            
            # 次のハートの描画位置をずらす
            draw_x += self.icon_size + self.spacing