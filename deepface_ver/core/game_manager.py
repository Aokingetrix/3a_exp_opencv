# game_manager moved into core (use relative import for settings)
import random
import pygame
from collections import Counter
from typing import Any, Dict, List, Optional
from . import settings

class GameState:
    TITLE = "title"
    SKIP_SELECTION = "skip_selection"  # 説明スキップ選択画面
    INSTRUCTION = "instruction"
    EMOTION_MAP = "emotion_map"  # 感情対応関係明示画面
    READY = "ready"
    COUNTDOWN = "countdown"  # 3-2-1 カウントダウン画面
    ROUND_START = "round_start"
    PLAYING = "playing"
    JUDGE = "judge"
    RESULT = "result"
    GAME_FINISH = "game_finish"

# 固定遷移テーブル: 各state で キャンセル（戻る）操作が遷移する先
BACK_TRANSITIONS = {
    GameState.SKIP_SELECTION: GameState.TITLE,
    GameState.INSTRUCTION: GameState.SKIP_SELECTION,
    GameState.EMOTION_MAP: GameState.INSTRUCTION,
    GameState.READY: GameState.TITLE,
    GameState.GAME_FINISH: GameState.TITLE,
}

class GameManager:
    def __init__(self, screen_width: int, screen_height: int, sounds: Dict[str, Any]) -> None:
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.sounds: Dict[str, Any] = sounds

        self.lives: int = 3

        self.round_duration_ms: float = 3000.0
        self.judge_start_offset_ms: int = 1000
        self.round_timeout_ms: int = 5000

        self.round_start_screen_duration_ms: int = 1500

        self.fps: int = 30

        self.emotions: List[str] = ["ニコニコ", "シクシク", "ムカムカ", "ビックリ", "シーン"]
        self.emotion_images: Dict[str, str] = dict(settings.EMOTION_IMAGE_PATHS)

        self.emotions_for_npc: List[str] = [e for e in self.emotions if e != "シーン"]

        self.state: str = GameState.TITLE
        self.score: int = 0
        self.current_round: int = 0

        self.player_name: str = "名無し"
        self.new_personal_best: bool = False
        self.personal_best_score: int = 0

        self.npc_emotions: List[str] = []

        self.player_emotion: Optional[str] = None
        self.round_result_text: str = ""

        self.player_emotion_history: List[str] = []
        self.round_start_time: int = 0
        self.timer_sec: float = 0.0

        self.last_round_outcome: Optional[str] = None
        self.last_score_change: int = 0
        self.last_life_change: int = 0

        self.skip_instruction: bool = False
        self.countdown_start_time: int = 0
        self.countdown_duration_ms: int = 3000

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.state = GameState.READY

    def start_game(self):
        """プレイヤー名確定後に呼ばれ、カウントダウンへ遷移する"""
        if self.state in [GameState.EMOTION_MAP, GameState.SKIP_SELECTION, GameState.GAME_FINISH]:
            self.score = 0
            self.current_round = 0
            self.lives = 3
            self.round_duration_ms = 3000
            # カウントダウン画面へ
            self.state = GameState.COUNTDOWN
            self.countdown_start_time = pygame.time.get_ticks()
            return

    def start_new_round(self):
        if self.lives <= 0:
            self.state = GameState.GAME_FINISH
            return
        self.current_round += 1
        
        self.state = GameState.ROUND_START
        self.player_emotion_history = []
        
        self.round_start_time = pygame.time.get_ticks()
        self.timer_sec = self.round_duration_ms / 1000.0

        self.npc_emotions = []
        self._select_npc_emotions()

        self.countdown_se_played = False

    def _select_npc_emotions(self) -> None:
        if self.score < 500:
            self.npc_emotions = [random.choice(self.emotions_for_npc)]
        elif self.score < 1500:
            self.npc_emotions = random.sample(self.emotions_for_npc, 2)
        else:
            self.npc_emotions = random.sample(self.emotions_for_npc, 3)
        
    def update(self, current_player_emotion: str, key_pressed_s: bool, key_pressed_cancel: bool, key_pressed_e: bool, key_pressed_n: bool, key_pressed_h: bool, key_pressed_r: bool) -> None:
        """メイン更新ロジック。画面遷移・ゲーム進行を制御する。"""
        if key_pressed_cancel:
            back_state = BACK_TRANSITIONS.get(self.state)
            if back_state:
                self.state = back_state
                return
        
        if self.state == GameState.TITLE:
            if key_pressed_s:
                self.state = GameState.SKIP_SELECTION
                return
        
        if self.state == GameState.SKIP_SELECTION:
            if key_pressed_s:
                self.skip_instruction = False
                self.state = GameState.INSTRUCTION
                return
        
        if self.state == GameState.INSTRUCTION:
            if key_pressed_s:
                self.state = GameState.EMOTION_MAP
                return
        
        if self.state == GameState.EMOTION_MAP:
            if key_pressed_s:
                pass
        
        if self.state == GameState.COUNTDOWN:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.countdown_start_time
            if elapsed >= self.countdown_duration_ms:
                self.start_new_round()
                return
        
        if key_pressed_r:
            if self.state == GameState.GAME_FINISH:
                self.state = GameState.TITLE
                return
        
        if key_pressed_s:
            if self.state == GameState.RESULT:
                if self.lives <= 0:
                    self.state = GameState.GAME_FINISH
                    return
                self.start_new_round()
                return
            elif self.state == GameState.GAME_FINISH:
                self.state = GameState.SKIP_SELECTION
                return
        
        if self.state == GameState.ROUND_START:
            self._transition_from_round_start()
        
        if self.state == GameState.PLAYING:
            self._update_playing(current_player_emotion)
        
        elif self.state == GameState.JUDGE:
            self.judge()

    def _transition_from_round_start(self) -> None:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.round_start_time
        if elapsed_time >= self.round_start_screen_duration_ms:
            self.state = GameState.PLAYING
            self.round_start_time = pygame.time.get_ticks()

    def _update_playing(self, current_player_emotion: str) -> None:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.round_start_time
        remaining_ms = self.round_duration_ms - elapsed_time
        self.timer_sec = max(0, remaining_ms / 1000.0)
        
        # ゲーム中の残り時間警告効果音
        if self.timer_sec < 2.0 and not getattr(self, 'countdown_se_played', False):
            self.sounds["count"].play()
            self.countdown_se_played = True

        judge_start_time_ms = self.round_duration_ms - self.judge_start_offset_ms
        if elapsed_time >= judge_start_time_ms:
            if current_player_emotion != "探し中...":
                self.player_emotion_history.append(current_player_emotion)

        is_time_over = elapsed_time >= self.round_duration_ms
        is_history_ready = bool(self.player_emotion_history)
        is_timeout = elapsed_time >= self.round_timeout_ms

        if (is_time_over and is_history_ready) or is_timeout:
            self.state = GameState.JUDGE

    def judge(self):
        if not self.player_emotion_history:
            self.player_emotion = "探し中..."
        else:
            self.player_emotion = Counter(self.player_emotion_history).most_common(1)[0][0]
        
        self.last_round_outcome = "success"
        self.last_score_change = 0
        self.last_life_change = 0
        
        if self.player_emotion == "探し中...":
            self.last_round_outcome = "fail_missing"
            self.last_score_change = -10
            self.last_life_change = -1
            self.score -= 10
            self.lives -= 1
            self.round_result_text = "顔がみつからない..."
            self.round_duration_ms = 3000
            self.sounds["fail"].play()

        elif self.player_emotion in self.npc_emotions:
            self.last_round_outcome = "fail_match"
            self.last_score_change = -50
            self.last_life_change = -1
            self.lives -= 1 
            self.round_result_text = "失敗！"
            self.round_duration_ms = 3000
            self.sounds["fail"].play()

        elif self.player_emotion == "シーン":
            self.last_round_outcome = "fail_neutral"
            self.last_score_change = -10
            self.last_life_change = -1
            self.lives -= 1
            self.round_result_text = "能面顔..."
            self.round_duration_ms = 3000
            self.sounds["fail"].play()

        else:
            self.last_round_outcome = "success"
            
            if self.score < 300:
                points = 100
            elif self.score < 700:
                points = 200
            else:
                points = 300
                
            self.last_score_change = points
            self.last_life_change = 0
            self.score += points
            self.round_duration_ms *= 0.95
            self.round_result_text = "成功!"
            self.sounds["success"].play()

        self.new_personal_best = self.score > self.personal_best_score
        
        self.state = GameState.RESULT