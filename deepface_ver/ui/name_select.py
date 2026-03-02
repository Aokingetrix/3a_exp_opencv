import pygame
from typing import List, Optional
from ..core import highscore


class NameSelector:
    def __init__(self) -> None:
        self.active: bool = False
        self.name: str = "名無し"
        self.cursor_pos: int = len(self.name)
        self.recent: List[str] = highscore.load().get("recent", ["名無し"])[:]
        self.selected_index: Optional[int] = None
        self.input_mode: bool = False
        self.done: bool = False
        self.cancelled: bool = False

    def start(self) -> None:
        self.active = True
        self.done = False
        self.cancelled = False
        self.name = ""
        self.cursor_pos = 0
        self.recent = highscore.load().get("recent", ["名無し"])[:]
        self.selected_index = 0 if self.recent else None
        self.input_mode = False

    def handle_event(self, event: pygame.event.EventType) -> None:
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # confirm
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
                self.active = False
                return
            if event.key == pygame.K_ESCAPE:
                self.cancelled = True
                self.active = False
                return
            if event.key == pygame.K_RIGHT:
                self.input_mode = True
                self.selected_index = None
                return
            if event.key == pygame.K_LEFT:
                self.input_mode = False
                self.name = ""
                self.cursor_pos = 0
                if self.recent:
                    self.selected_index = 0 if self.selected_index is None else self.selected_index
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
                    self.name = ""
                    self.cursor_pos = 0
                return
            if event.key == pygame.K_DOWN:
                if not self.input_mode and self.recent:
                    if self.selected_index is None:
                        self.selected_index = 0
                    else:
                        self.selected_index = min(len(self.recent) - 1, self.selected_index + 1)
                    self.name = ""
                    self.cursor_pos = 0
                return
            # text input (basic)
            if self.input_mode and event.unicode and event.unicode.isprintable():
                self.name = self.name[: self.cursor_pos] + event.unicode + self.name[self.cursor_pos :]
                self.cursor_pos += len(event.unicode)

    def get_result(self) -> Optional[str]:
        if self.done:
            return self.name
        return None
