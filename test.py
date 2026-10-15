import pytest

from main import *

class TestWatch:
    def test_generate_state_list(self):
        result = generate_state_list(1, False, False)
        assert result == [WatchState.ESCAPED,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.ESCAPED]
        result = generate_state_list(2, False, False)
        assert result == [WatchState.ESCAPED,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.BREATHING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.ESCAPED]
        result = generate_state_list(1, True, False)
        assert result == [WatchState.ESCAPED,
                          WatchState.BREATHING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.ESCAPED]
        result = generate_state_list(1, False, True)
        assert result == [WatchState.ESCAPED,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PLAYING_CAPTIONS,
                          WatchState.BREATHING,
                          WatchState.ESCAPED]

    def test_generate_next_state_times(self):
        result = generate_next_state_times(generate_state_list(1, True, False), 5, 10, 2, 1)
        assert result == [0, 5, 7, 14, 15, 15]

