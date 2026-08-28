from __future__ import annotations

import random
import unittest

from deepface_ver.core.game_manager import GameManager, GameState
from deepface_ver.core.models import GameCommand


class FakeSound:
    def __init__(self) -> None:
        self.play_count = 0

    def play(self) -> None:
        self.play_count += 1


class FakeClock:
    def __init__(self) -> None:
        self.value = 0

    def __call__(self) -> int:
        return self.value


class GameManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.sounds = {name: FakeSound() for name in ("count", "success", "fail")}
        self.game = GameManager(
            1280,
            480,
            self.sounds,
            now_ms=self.clock,
            random_source=random.Random(7),
        )

    def test_intro_flow_and_countdown(self) -> None:
        self.game.handle("探し中...", GameCommand(start=True))
        self.assertEqual(GameState.SKIP_SELECTION, self.game.state)
        self.game.handle("探し中...", GameCommand(start=True))
        self.assertEqual(GameState.INSTRUCTION, self.game.state)
        self.game.handle("探し中...", GameCommand(start=True))
        self.assertEqual(GameState.EMOTION_MAP, self.game.state)
        self.game.start_game()
        self.assertEqual(GameState.COUNTDOWN, self.game.state)
        self.clock.value = 3000
        self.game.handle("探し中...", GameCommand())
        self.assertEqual(GameState.ROUND_START, self.game.state)

    def test_success_increases_score_and_shortens_round(self) -> None:
        self.game.npc_emotions = ["ニコニコ"]
        self.game.player_emotion_history = ["シクシク"]
        result = self.game.judge()
        self.assertEqual("success", result.code)
        self.assertEqual(100, self.game.score)
        self.assertEqual(2850.0, self.game.round_duration_ms)
        self.assertEqual(1, self.sounds["success"].play_count)

    def test_match_failure_applies_recorded_score_change(self) -> None:
        self.game.score = 100
        self.game.npc_emotions = ["ニコニコ"]
        self.game.player_emotion_history = ["ニコニコ"]
        self.game.judge()
        self.assertEqual(-50, self.game.last_score_change)
        self.assertEqual(50, self.game.score)
        self.assertEqual(2, self.game.lives)

    def test_neutral_and_missing_failures_apply_ten_point_penalty(self) -> None:
        for history, expected_code in ((["シーン"], "fail_neutral"), ([], "fail_missing")):
            with self.subTest(expected_code=expected_code):
                self.game.score = 0
                self.game.lives = 3
                self.game.npc_emotions = ["ニコニコ"]
                self.game.player_emotion_history = history
                result = self.game.judge()
                self.assertEqual(expected_code, result.code)
                self.assertEqual(-10, self.game.score)
                self.assertEqual(2, self.game.lives)

    def test_difficulty_uses_score_thresholds(self) -> None:
        for score, expected_count in ((0, 1), (500, 2), (1500, 3)):
            self.game.score = score
            self.game._select_npc_emotions()
            self.assertEqual(expected_count, len(self.game.npc_emotions))


if __name__ == "__main__":
    unittest.main()
