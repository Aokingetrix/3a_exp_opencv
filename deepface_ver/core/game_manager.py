# game_manager moved into core (use relative import for settings)
import random
import pygame
from collections import Counter
from . import settings

class GameState:
    TITLE = "title"
    INSTRUCTION = "instruction"
    READY = "ready"
    ROUND_START = "round_start"
    PLAYING = "playing"
    JUDGE = "judge"
    RESULT = "result"
    GAME_FINISH = "game_finish"

class GameManager:
    def __init__(self, screen_width, screen_height, sounds):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sounds = sounds
        
        self.lives = 3
        
        self.round_duration_ms = 3000
        self.judge_start_offset_ms = 1000
        self.round_timeout_ms = 5000

        self.round_start_screen_duration_ms = 1500
        
        self.fps = 30

        self.emotions = ["ニコニコ", "シクシク", "ムカムカ", "ビックリ", "シーン"]
        self.emotion_images = dict(settings.EMOTION_IMAGE_PATHS)

        self.emotions_for_npc = [e for e in self.emotions if e != "シーン"]

        self.state = GameState.TITLE
        self.score = 0
        self.current_round = 0

        self.npc_emotions = []

        self.player_emotion = None
        self.round_result_text = ""

        self.player_emotion_history = []
        self.round_start_time = 0
        self.timer_sec = 0.0

        self.last_round_outcome = None
        self.last_score_change = 0
        self.last_life_change = 0

    # ... keep all methods unchanged (omitted here for brevity) ...

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.state =GameState.READY

    def start_game(self):
        if self.state in [GameState.INSTRUCTION, GameState.GAME_FINISH]:
            self.score = 0
            self.current_round = 0
            self.lives = 3
            self.start_new_round()
            self.round_duration_ms = 3000

    # rest of methods unchanged
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
        if self.score < 500:
            self.npc_emotions.append(random.choice(self.emotions_for_npc))

        elif self.score < 1500:
            self.npc_emotions = random.sample(self.emotions_for_npc, 2)

        else:
            self.npc_emotions = random.sample(self.emotions_for_npc, 3)

        self.countdown_se_played = False

    def update(self, current_player_emotion, key_pressed_s, key_pressed_e, key_pressed_n, key_pressed_h, key_pressed_r):

        if self.state == GameState.TITLE:
            if key_pressed_s:
                self.state = GameState.INSTRUCTION
                return
        if self.state == GameState.INSTRUCTION:
            if key_pressed_s:
                self.start_game()
                return
        
        if key_pressed_s:
            if self.state == GameState.RESULT:
                self.start_new_round()
                return

            elif self.state == GameState.GAME_FINISH:
                self.start_game() 
                return

        if key_pressed_r:
            if self.state == GameState.GAME_FINISH:
                self.state = GameState.TITLE
                return
        
        if self.state == GameState.ROUND_START:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.round_start_time
            if elapsed_time >= self.round_start_screen_duration_ms:
                self.state = GameState.PLAYING
                self.round_start_time = pygame.time.get_ticks()
        
        if self.state == GameState.PLAYING:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.round_start_time
            remaining_ms = self.round_duration_ms - elapsed_time
            self.timer_sec = max(0, remaining_ms / 1000.0)
            if self.timer_sec < 2.0 and not self.countdown_se_played:
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
        
        elif self.state == GameState.JUDGE:
            self.judge()

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
        
        self.state = GameState.RESULT
