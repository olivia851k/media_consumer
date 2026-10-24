import pytest

from main import *

def compare_state_sequence(sequence, iterations, start_breathing, end_breathing, input_sequence = None, should_skip=False):
    # could change to all options allowed to be lists that change over time
    state = WatchState.ESCAPED
    next_state = WatchState.PLAY
    history = [state]
    i = 0
    max_iterations = 50
    for j in range(0, max_iterations):
        watch_input = WatchInput.NONE
        if input_sequence and j < len(input_sequence):
            watch_input = input_sequence[j]
        print(state, i, watch_input)
        next_state, i = get_next_state(state, iterations, i, watch_input, start_breathing, end_breathing, should_skip)
        state = next_state
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
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, False, False)

    def test_next_state_2ff(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 2, False, False)

    def test_next_state_1tf(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, True, False)

    def test_next_state_1ft(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, False, True)

    def test_next_state_1tt(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.ESCAPED]
        compare_state_sequence(sequence, 1, True, True)

    def test_next_state_1pp(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        input_sequence = [WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.NONE]
        compare_state_sequence(sequence, 1, False, False, input_sequence)

    def test_next_state_1ps(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.ESCAPED]
        input_sequence = [WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE]
        compare_state_sequence(sequence, 1, False, False, input_sequence, should_skip=True)

    def test_next_state_4ps(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.MANUAL_PAUSED,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.ESCAPED]
        input_sequence = [WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.NONE]
        compare_state_sequence(sequence, 4, False, False, input_sequence, should_skip=True)

    def test_next_state_escape(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.ESCAPED]
        input_sequence = [WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.FULLSCREEN]
        compare_state_sequence(sequence, 1, True, True, input_sequence)

    def test_next_state_manual_play(self):
        sequence = [WatchState.ESCAPED,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.LINGERING_CAPTIONS,
                    WatchState.PLAY,
                    WatchState.PRE_CAPTIONS,
                    WatchState.BREATHING,
                    WatchState.ESCAPED]
        input_sequence = [WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.NONE,
                          WatchInput.PLAY,
                          WatchInput.NONE]
        compare_state_sequence(sequence, 2, True, True, input_sequence)


