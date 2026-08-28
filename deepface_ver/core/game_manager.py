"""Game state machine independent from Pygame's event and clock APIs."""

from __future__ import annotations

import random
import time
from collections import Counter
from collections.abc import Callable, Mapping
from typing import Any

from . import settings
from .models import GameCommand, RoundOutcome


class GameState:
    TITLE = "title"
    SKIP_SELECTION = "skip_selection"
    INSTRUCTION = "instruction"
    EMOTION_MAP = "emotion_map"
    READY = "ready"
    COUNTDOWN = "countdown"
    ROUND_START = "round_start"
    PLAYING = "playing"
    JUDGE = "judge"
    RESULT = "result"
    GAME_FINISH = "game_finish"


BACK_TRANSITIONS = {
    GameState.SKIP_SELECTION: GameState.TITLE,
    GameState.INSTRUCTION: GameState.SKIP_SELECTION,
    GameState.EMOTION_MAP: GameState.INSTRUCTION,
    GameState.READY: GameState.TITLE,
    GameState.GAME_FINISH: GameState.TITLE,
}


def _monotonic_ms() -> int:
    return int(time.monotonic() * 1000)


class GameManager:
    """Owns game rules and state transitions."""

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        sounds: Mapping[str, Any],
        *,
        now_ms: Callable[[], int] | None = None,
        random_source: random.Random | None = None,
    ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sounds = sounds
        self._now_ms = now_ms or _monotonic_ms
        self._random = random_source or random.Random()

        self.lives = 3
        self.round_duration_ms = 3000.0
        self.judge_start_offset_ms = 1000
        self.round_timeout_ms = 5000
        self.round_start_screen_duration_ms = 1500
        self.fps = 30

        self.emotions = ["ニコニコ", "シクシク", "ムカムカ", "ビックリ", "シーン"]
        self.emotion_images = dict(settings.EMOTION_IMAGE_PATHS)
        self.emotions_for_npc = [emotion for emotion in self.emotions if emotion != "シーン"]

        self.state = GameState.TITLE
        self.score = 0
        self.current_round = 0
        self.player_name = "名無し"
        self.new_personal_best = False
        self.personal_best_score = 0
        self.npc_emotions: list[str] = []
        self.player_emotion: str | None = None
        self.round_result_text = ""
        self.player_emotion_history: list[str] = []
        self.round_start_time = 0
        self.timer_sec = 0.0
        self.last_round_outcome: str | None = None
        self.last_score_change = 0
        self.last_life_change = 0
        self.skip_instruction = False
        self.countdown_start_time = 0
        self.countdown_duration_ms = 3000
        self.countdown_se_played = False
        self.all_time_rank = 0
        self.todays_rank = 0
        self.personal_best_list: list[int] = []

    def set_difficulty(self, difficulty: str) -> None:
        self.difficulty = difficulty
        self.state = GameState.READY

    def start_game(self) -> None:
        if self.state not in {
            GameState.EMOTION_MAP,
            GameState.SKIP_SELECTION,
            GameState.GAME_FINISH,
        }:
            return
        self.score = 0
        self.current_round = 0
        self.lives = 3
        self.round_duration_ms = 3000.0
        self.state = GameState.COUNTDOWN
        self.countdown_start_time = self._now_ms()

    def start_new_round(self) -> None:
        if self.lives <= 0:
            self.state = GameState.GAME_FINISH
            return
        self.current_round += 1
        self.state = GameState.ROUND_START
        self.player_emotion_history = []
        self.round_start_time = self._now_ms()
        self.timer_sec = self.round_duration_ms / 1000.0
        self._select_npc_emotions()
        self.countdown_se_played = False

    def _select_npc_emotions(self) -> None:
        if self.score < 500:
            self.npc_emotions = [self._random.choice(self.emotions_for_npc)]
        elif self.score < 1500:
            self.npc_emotions = self._random.sample(self.emotions_for_npc, 2)
        else:
            self.npc_emotions = self._random.sample(self.emotions_for_npc, 3)

    def handle(self, current_player_emotion: str, command: GameCommand) -> None:
        if command.cancel:
            back_state = BACK_TRANSITIONS.get(self.state)
            if back_state:
                self.state = back_state
                return

        if self.state == GameState.TITLE and command.start:
            self.state = GameState.SKIP_SELECTION
            return
        if self.state == GameState.SKIP_SELECTION and command.start:
            self.skip_instruction = False
            self.state = GameState.INSTRUCTION
            return
        if self.state == GameState.INSTRUCTION and command.start:
            self.state = GameState.EMOTION_MAP
            return
        if self.state == GameState.COUNTDOWN:
            if self._now_ms() - self.countdown_start_time >= self.countdown_duration_ms:
                self.start_new_round()
                return
        if command.restart and self.state == GameState.GAME_FINISH:
            self.state = GameState.TITLE
            return
        if command.start:
            if self.state == GameState.RESULT:
                if self.lives <= 0:
                    self.state = GameState.GAME_FINISH
                else:
                    self.start_new_round()
                return
            if self.state == GameState.GAME_FINISH:
                self.state = GameState.SKIP_SELECTION
                return
        if self.state == GameState.ROUND_START:
            self._transition_from_round_start()
        if self.state == GameState.PLAYING:
            self._update_playing(current_player_emotion)
        elif self.state == GameState.JUDGE:
            self.judge()

    def update(
        self,
        current_player_emotion: str,
        key_pressed_s: bool,
        key_pressed_cancel: bool,
        key_pressed_e: bool,
        key_pressed_n: bool,
        key_pressed_h: bool,
        key_pressed_r: bool,
    ) -> None:
        """Compatibility adapter for the original fes2026 call site."""
        self.handle(
            current_player_emotion,
            GameCommand(
                start=key_pressed_s,
                cancel=key_pressed_cancel,
                skip=key_pressed_e,
                restart=key_pressed_r,
                debug_easy=key_pressed_e,
                debug_normal=key_pressed_n,
                debug_hard=key_pressed_h,
            ),
        )

    def _transition_from_round_start(self) -> None:
        if self._now_ms() - self.round_start_time >= self.round_start_screen_duration_ms:
            self.state = GameState.PLAYING
            self.round_start_time = self._now_ms()

    def _update_playing(self, current_player_emotion: str) -> None:
        elapsed_time = self._now_ms() - self.round_start_time
        remaining_ms = self.round_duration_ms - elapsed_time
        self.timer_sec = max(0.0, remaining_ms / 1000.0)
        if self.timer_sec < 2.0 and not self.countdown_se_played:
            self.sounds["count"].play()
            self.countdown_se_played = True
        judge_start_time_ms = self.round_duration_ms - self.judge_start_offset_ms
        if elapsed_time >= judge_start_time_ms and current_player_emotion != "探し中...":
            self.player_emotion_history.append(current_player_emotion)
        is_time_over = elapsed_time >= self.round_duration_ms
        is_history_ready = bool(self.player_emotion_history)
        is_timeout = elapsed_time >= self.round_timeout_ms
        if (is_time_over and is_history_ready) or is_timeout:
            self.state = GameState.JUDGE

    def judge(self) -> RoundOutcome:
        self.player_emotion = (
            Counter(self.player_emotion_history).most_common(1)[0][0]
            if self.player_emotion_history
            else "探し中..."
        )
        if self.player_emotion == "探し中...":
            outcome = RoundOutcome("fail_missing", -10, -1, "顔がみつからない...")
        elif self.player_emotion in self.npc_emotions:
            outcome = RoundOutcome("fail_match", -50, -1, "失敗！")
        elif self.player_emotion == "シーン":
            outcome = RoundOutcome("fail_neutral", -10, -1, "能面顔...")
        else:
            if self.score < 300:
                points = 100
            elif self.score < 700:
                points = 200
            else:
                points = 300
            outcome = RoundOutcome("success", points, 0, "成功!")
        self._apply_outcome(outcome)
        return outcome

    def _apply_outcome(self, outcome: RoundOutcome) -> None:
        self.last_round_outcome = outcome.code
        self.last_score_change = outcome.score_change
        self.last_life_change = outcome.life_change
        self.round_result_text = outcome.message
        self.score += outcome.score_change
        self.lives += outcome.life_change
        if outcome.code == "success":
            self.round_duration_ms *= 0.95
            self.sounds["success"].play()
        else:
            self.round_duration_ms = 3000.0
            self.sounds["fail"].play()
        self.new_personal_best = self.score > self.personal_best_score
        self.state = GameState.RESULT
