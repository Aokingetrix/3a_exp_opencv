# FILE: deepface_ver/ui/name_select.py


import pygame

from ..core import highscore


class NameSelector:
    def __init__(self) -> None:
        self.active: bool = False
        self.name: str = "名無し"
        self.cursor_pos: int = len(self.name)
        self.recent: list[str] = highscore.load().get("recent", ["名無し"])[:6]
        self.selected_index: int | None = None
        self.input_mode: bool = False
        self.done: bool = False
        self.cancelled: bool = False
        # 追加: 変換中の文字列を保持する変数
        self.editing_text: str = ""

    def start(self) -> None:
        self.active = True
        self.done = False
        self.cancelled = False
        self.name = "名無し"
        self.cursor_pos = len(self.name)
        self.recent = highscore.load().get("recent", ["名無し"])[:6]
        self.selected_index = 0 if self.recent else None
        self.input_mode = False
        self.editing_text = ""
        # 確実にテキスト入力をオフにしておく
        pygame.key.stop_text_input()

    def handle_event(self, event: pygame.event.EventType) -> None:
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
                self.cancelled = True
                pygame.key.stop_text_input()
                return

            if event.key == pygame.K_RETURN:
                if self.input_mode:
                    entered_name = self.name.strip()
                    if not entered_name:
                        entered_name = "名無し"
                    self.name = entered_name
                else:
                    if self.selected_index is not None and self.recent:
                        self.name = self.recent[self.selected_index]
                    elif not self.name:
                        self.name = "名無し"
                self.done = True
                pygame.key.stop_text_input()
                return

            if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                self.input_mode = not self.input_mode
                if self.input_mode:
                    self.selected_index = None
                    # 入力モードになったらIMEをオンにし、変換候補の表示位置を指定
                    pygame.key.start_text_input()
                    pygame.key.set_text_input_rect(pygame.Rect(662, 252, 200, 40))
                else:
                    self.selected_index = 0 if self.recent else None
                    # 履歴選択モードに戻ったらIMEをオフにする
                    pygame.key.stop_text_input()
                    self.editing_text = ""
                return

            if event.key == pygame.K_BACKSPACE:
                if self.input_mode and self.cursor_pos > 0:
                    self.name = self.name[: self.cursor_pos - 1] + self.name[self.cursor_pos :]
                    self.cursor_pos -= 1
                return

            if event.key == pygame.K_UP:
                if not self.input_mode and self.recent:
                    if self.selected_index is None:
                        self.selected_index = 0
                    else:
                        self.selected_index = max(0, self.selected_index - 1)
                return

            if event.key == pygame.K_DOWN:
                if not self.input_mode and self.recent:
                    if self.selected_index is None:
                        self.selected_index = 0
                    else:
                        self.selected_index = min(len(self.recent) - 1, self.selected_index + 1)
                return

        # 追加: IME変換中のイベント処理
        elif event.type == pygame.TEXTEDITING:
            if self.input_mode:
                self.editing_text = event.text

        # 追加: IME確定後、または通常の文字入力イベント処理
        elif event.type == pygame.TEXTINPUT:
            if self.input_mode:
                self.name = self.name[: self.cursor_pos] + event.text + self.name[self.cursor_pos :]
                self.cursor_pos += len(event.text)
                self.editing_text = ""

    def get_result(self) -> str | None:
        if self.done:
            return self.name
        return None
