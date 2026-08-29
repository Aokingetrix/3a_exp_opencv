"""Compatibility facade for screen drawing functions."""

from .screens.gameplay import (
    draw_common_ui,
    draw_developer_screen,
    draw_finish_screen,
    draw_game_background,
    draw_playing_screen,
    draw_result_screen,
    draw_round_start_screen,
)
from .screens.intro import (
    draw_countdown_screen,
    draw_emotion_map_screen,
    draw_instruction_screen,
    draw_name_select_screen,
    draw_skip_selection_screen,
    draw_title_screen,
)
from .screens.rankings import draw_finish_highscores, draw_title_highscores

__all__ = [
    "draw_common_ui",
    "draw_countdown_screen",
    "draw_developer_screen",
    "draw_emotion_map_screen",
    "draw_finish_highscores",
    "draw_finish_screen",
    "draw_game_background",
    "draw_instruction_screen",
    "draw_name_select_screen",
    "draw_playing_screen",
    "draw_result_screen",
    "draw_round_start_screen",
    "draw_skip_selection_screen",
    "draw_title_highscores",
    "draw_title_screen",
]
