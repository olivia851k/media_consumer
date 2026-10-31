from enum import Enum


class WatchState(Enum):
    START = 0
    ESCAPED = 1
    BREATHING = 2
    LINGERING_CAPTIONS = 3
    PLAY = 4
    PRE_CAPTIONS = 5
    MANUAL_PAUSED = 6
    QUITTING = 7

class WatchAction(Enum):
    FOCUS_PLAYER = 0
    FOCUS_SELF = 1
    PLAY = 2
    ENABLE_CAPTIONS = 3
    DISABLE_CAPTIONS = 4
    FULLSCREEN = 5

class WatchInput(Enum):
    # in order of importance
    NONE = 1000 # must be a higher number than the rest
    FULLSCREEN = 1
    QUIT = 2
    PLAY = 3
    PLAY_AFTER_BREATH = 4


def invalid_state_transition(state, new_state):
    raise Exception(f'Invalid transition from {state.name} to {new_state.name}')

# question as to whether to add in a breathing state after a manual pause if start_breathing == True
def get_next_state(state, iterations, i, watch_input, start_breathing, end_breathing, should_skip):
    next_state = WatchState.ESCAPED
    if watch_input == WatchInput.FULLSCREEN:
        next_state = WatchState.ESCAPED
    elif state == WatchState.START:
        if start_breathing:
            next_state = WatchState.BREATHING
        else:
            next_state = WatchState.LINGERING_CAPTIONS
            i += 1
    elif state == WatchState.BREATHING:
        if i == iterations:
            next_state = WatchState.ESCAPED
        else:
            next_state = WatchState.LINGERING_CAPTIONS
            i += 1
    elif state == WatchState.LINGERING_CAPTIONS:
        if watch_input == WatchInput.PLAY:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.PLAY
    elif state == WatchState.PLAY:
        if watch_input == WatchInput.PLAY:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.PRE_CAPTIONS
    elif state == WatchState.PRE_CAPTIONS:
        if watch_input == WatchInput.PLAY:
            next_state = WatchState.MANUAL_PAUSED
        else:
            if i == iterations:
                if end_breathing:
                    next_state = WatchState.BREATHING
                else:
                    next_state = WatchState.ESCAPED
            else:
                next_state = WatchState.BREATHING
    elif state == WatchState.MANUAL_PAUSED:
        # might skip an iteration depending on the timestamp of the last lingering captions
        if watch_input == WatchInput.PLAY:
            if i == iterations and should_skip:
                if end_breathing:
                    next_state = WatchState.BREATHING
                else:
                    next_state = WatchState.ESCAPED
            else:
                if should_skip:
                    i += 1
                next_state = WatchState.LINGERING_CAPTIONS
        elif watch_input == WatchInput.PLAY_AFTER_BREATH:
            next_state = WatchState.BREATHING
            if should_skip:
                i += 1
        elif watch_input == WatchInput.NONE:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.ESCAPED
    return next_state, i


def change_state(state, new_state, watch_input):
    action_sequence = []
    if state == WatchState.START:
        if new_state == WatchState.BREATHING:
            action_sequence.extend([WatchAction.FOCUS_PLAYER,
                                    WatchAction.FULLSCREEN])
        elif new_state == WatchState.LINGERING_CAPTIONS:
            action_sequence.extend([WatchAction.FOCUS_PLAYER,
                                    WatchAction.FULLSCREEN,
                                    WatchAction.PLAY])
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.BREATHING:
        if new_state == WatchState.LINGERING_CAPTIONS:
            action_sequence.append(WatchAction.PLAY)
        elif new_state == WatchState.ESCAPED:
            if watch_input == WatchInput.PLAY:
                action_sequence.append(WatchAction.PLAY)
            elif watch_input == WatchInput.NONE:
                action_sequence.append(WatchAction.FULLSCREEN)
            action_sequence.append(WatchAction.FOCUS_SELF)
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.LINGERING_CAPTIONS:
        if new_state == WatchState.PLAY:
            action_sequence.append(WatchAction.DISABLE_CAPTIONS)
        elif new_state == WatchState.MANUAL_PAUSED:
            pass
        elif new_state == WatchState.ESCAPED:
            action_sequence.extend([WatchAction.PLAY,
                                    WatchAction.FOCUS_SELF])
        elif new_state == WatchState.QUITTING:
            action_sequence.extend([WatchAction.FULLSCREEN,
                                    WatchAction.FOCUS_SELF])
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.PLAY:
        if new_state == WatchState.PRE_CAPTIONS:
            action_sequence.append(WatchAction.ENABLE_CAPTIONS)
        elif new_state == WatchState.MANUAL_PAUSED:
            action_sequence.append(WatchAction.ENABLE_CAPTIONS)
        elif new_state == WatchState.ESCAPED:
            action_sequence.extend([WatchAction.PLAY,
                                    WatchAction.ENABLE_CAPTIONS,
                                    WatchAction.FOCUS_SELF])
        elif new_state == WatchState.QUITTING:
            action_sequence.extend([WatchAction.FULLSCREEN,
                                    WatchAction.ENABLE_CAPTIONS,
                                    WatchAction.FOCUS_SELF])
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.PRE_CAPTIONS:
        if new_state == WatchState.BREATHING:
            action_sequence.append(WatchAction.PLAY)
        elif new_state == WatchState.MANUAL_PAUSED:
            pass
        elif new_state == WatchState.ESCAPED:
            if watch_input != WatchInput.FULLSCREEN:
                action_sequence.append(WatchAction.FULLSCREEN)
            action_sequence.extend([WatchAction.PLAY,
                                    WatchAction.FOCUS_SELF])
        elif new_state == WatchState.QUITTING:
            action_sequence.extend([WatchAction.FULLSCREEN,
                                    WatchAction.FOCUS_SELF])
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.MANUAL_PAUSED:
        if new_state == WatchState.LINGERING_CAPTIONS:
            pass
        elif new_state == WatchState.PLAY:
            action_sequence.append(WatchAction.DISABLE_CAPTIONS)
        elif new_state == WatchState.PRE_CAPTIONS:
            pass
        elif new_state == WatchState.ESCAPED:
            action_sequence.append(WatchAction.FOCUS_SELF)
            pass
        elif new_state == WatchState.MANUAL_PAUSED:
            pass
        elif new_state == WatchState.BREATHING:
            pass
        else:
            invalid_state_transition(state, new_state)
    return action_sequence


