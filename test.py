import pytest

from main import *

class TestWatch:
    def test_generate_state_list(self):
        result = generate_state_list(1, False, False)
        assert result == [WatchState.ESCAPED,
                          WatchState.LINGERING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PRE_CAPTIONS,
                          WatchState.ESCAPED]
        result = generate_state_list(2, False, False)
        assert result == [WatchState.ESCAPED,
                          WatchState.LINGERING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PRE_CAPTIONS,
                          WatchState.BREATHING,
                          WatchState.LINGERING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PRE_CAPTIONS,
                          WatchState.ESCAPED]
        result = generate_state_list(1, True, False)
        assert result == [WatchState.ESCAPED,
                          WatchState.BREATHING,
                          WatchState.LINGERING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PRE_CAPTIONS,
                          WatchState.ESCAPED]
        result = generate_state_list(1, False, True)
        assert result == [WatchState.ESCAPED,
                          WatchState.LINGERING_CAPTIONS,
                          WatchState.PLAYING,
                          WatchState.PRE_CAPTIONS,
                          WatchState.BREATHING,
                          WatchState.ESCAPED]

    def test_consumer(self):
        pass


