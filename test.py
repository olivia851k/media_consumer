import pytest

from main import *

def compare_state_sequence(sequence, iterations, start_breathing, end_breathing):
    # could change to all options allowed to be lists that change over time
    state = WatchState.ESCAPED
    next_state = WatchState.PLAYING
    history = [state]
    i = 0
#    while next_state != WatchState.ESCAPED:
    for j in range(0, 40):
        next_state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        state = next_state
        history.append(state)
        if state == WatchState.ESCAPED:
            break
    assert history == sequence
    assert i == iterations


class TestWatch:
    def test_next_state_1ff(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, False, False)

    def test_next_state_2ff(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 2, False, False)

    def test_next_state_1tf(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, True, False)

    def test_next_state_1ft(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, False, True)

    def test_next_state_1tt(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, True, True)

    def test_next_state_1pp(self):
        state = WatchState.ESCAPED
        start_breathing = False
        end_breathing = False
        iterations = 1
        i = 0
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.LINGERING_CAPTIONS
        state, i = get_next_state(state, iterations, i, True, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.MANUAL_PAUSED
        state, i = get_next_state(state, iterations, i, True, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.LINGERING_CAPTIONS
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.PLAYING
        state, i = get_next_state(state, iterations, i, True, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.MANUAL_PAUSED
        state, i = get_next_state(state, iterations, i, True, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.LINGERING_CAPTIONS
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.PLAYING
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.PRE_CAPTIONS
        state, i = get_next_state(state, iterations, i, True, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.MANUAL_PAUSED
        state, i = get_next_state(state, iterations, i, True, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.LINGERING_CAPTIONS
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.PLAYING
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.PRE_CAPTIONS
        state, i = get_next_state(state, iterations, i, False, False, False, start_breathing, end_breathing, False)
        assert state == WatchState.ESCAPED
        assert i == iterations


