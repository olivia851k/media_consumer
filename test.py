import pytest

from main import *

def compare_state_sequence(sequence, iterations, start_breathing, end_breathing, space_sequence = None, escape_i = -1, quit_i = -1, should_skip=False):
    # could change to all options allowed to be lists that change over time
    state = WatchState.ESCAPED
    next_state = WatchState.PLAYING
    history = [state]
    i = 0
#    while next_state != WatchState.ESCAPED:
    max_iterations = 50
    for j in range(0, max_iterations):
        space_press = False
        if space_sequence and j < len(space_sequence):
            space_press = space_sequence[j]
        next_state, i = get_next_state(state, iterations, i, space_press, escape_i == j, quit_i == j, start_breathing, end_breathing, should_skip)
        state = next_state
        print(state, i)
        history.append(state)
        if state == WatchState.ESCAPED:
            break
        if j == max_iterations - 1:
            assert False
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
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        space_sequence = [False,
                          True,
                          True,
                          False,
                          True,
                          True,
                          False,
                          False,
                          True,
                          True,
                          False,
                          False,
                          False]
        compare_state_sequence(sequence, 1, False, False, space_sequence)

    def test_next_state_1ps(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.ESCAPED]
        space_sequence = [False,
                          True,
                          True,
                          False]
        compare_state_sequence(sequence, 1, False, False, space_sequence, should_skip=True)

    def test_next_state_4ps(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAYING,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        space_sequence = [False,
                          True,
                          True,
                          False,
                          True,
                          True,
                          False,
                          False,
                          True,
                          True,
                          False,
                          False,
                          False]
        compare_state_sequence(sequence, 4, False, False, space_sequence, should_skip=True)


