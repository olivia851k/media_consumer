import time
import copy
from pynput import keyboard
from enum import Enum

class WatchState(Enum):
    ESCAPED = 0
    BREATHING = 1
    LINGERING_CAPTIONS = 2
    PLAYING = 3
    PRE_CAPTIONS = 4
    MANUAL_PAUSED = 5
    MANUAL_PLAY = 6
    QUITTING = 7

def generate_state_list(iterations, start_breathing, end_breathing):
    state_list = [WatchState.ESCAPED]
    if start_breathing:
        state_list.append(WatchState.BREATHING)
    for i in range(iterations):
        state_list.extend([WatchState.LINGERING_CAPTIONS,
                           WatchState.PLAYING,
                           WatchState.PRE_CAPTIONS,
                           WatchState.BREATHING])
    if not end_breathing:
        state_list = state_list[:-1]
    state_list.append(WatchState.ESCAPED)
    return state_list

# question as to whether to add in a breathing state after a manual pause if start_breathing == True
def get_next_state(state, iterations, i, space_pressed, escape_pressed, quit_pressed, start_breathing, end_breathing, should_skip):
    next_state = WatchState.ESCAPED
    if escape_pressed:
        next_state = WatchState.ESCAPED
    elif state == WatchState.ESCAPED:
        if start_breathing:
            next_state = WatchState.BREATHING
        else:
            next_state = WatchState.LINGERING_CAPTIONS
            i += 1
    elif state == WatchState.BREATHING:
        if space_pressed:
            next_state = WatchState.MANUAL_PLAY
        else:
            if i == iterations:
                next_state = WatchState.ESCAPED
            else:
                next_state = WatchState.LINGERING_CAPTIONS
                i += 1
    elif state == WatchState.LINGERING_CAPTIONS:
        if space_pressed:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.PLAYING
    elif state == WatchState.PLAYING:
        if space_pressed:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.PRE_CAPTIONS
    elif state == WatchState.PRE_CAPTIONS:
        if space_pressed:
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
        if space_pressed:
            if should_skip:
                i += 1
            next_state = WatchState.LINGERING_CAPTIONS
        else:
            next_state = WatchState.ESCAPED
    #manual play, end clause
    return next_state, i


class GUI:
    def __init__(self):
        self.start_breathing = False
        self.end_breathing = True
        self.breathing_time = 25
        self.playing_time = 90
        self.playing_captions_time = 5
        self.additional_captions_time = 0.1
        self.captions_count = 1 # also used so captions aren't changed by program
        self.captions_position = 1
        self.iterations = 3

# interactive style watch :)
def watch():
    consumer = Consumer(iterations, breathing_time, playing_time, 5, True, True, False, True, captions_count, captions_posiition, 0.1)

# the cheeky edge cases are what happens when the user pressed a button during transition
class Consumer:
    def __init__(self, press_key, watch_wait,
            iterations, breathing_time, playing_time,
            playing_captions_time, lingering_captions, pre_captions,
            start_breathing, end_breathing,
            captions_count, captions_position, additional_captions_time,
            resume_time):
        self.press_key = press_key
        self.watch_wait = watch_wait # returns elapsed_time, keys_pressed
        self.breathing_time = breathing_time
        self.playing_time = playing_time
        self.captions_count = captions_count
        self.captions_position = captions_position
        self.lingering_captions_time = playing_captions_time
        self.pre_captions_time = playing_captions_time + self.captions_position * additional_captions_time
        self.state_i = 0
        self.state_list = generate_state_list(iterations, start_breathing, end_breathing)
        self.transitioning = False # True when inbetween states
        self.start_time = 0
        self.state = WatchState.ESCAPED
        self.resume_time = resume_time

    def invalid_state_transition(self, new_state):
        raise Exception(f'Invalid transition from {self.state.name} to {new_state.name}')

    def current_state(self):
        return self.state_list[self.state_i]

    def get_state_time(self, state):
        state_time = 0
        if state == WatchState.BREATHING:
            state_time = self.breathing_time
        elif state == WatchState.PLAYING:
            state_time = self.playing_time - self.lingering_captions_time - self.pre_captions_time
        elif state == WatchState.LINGERING_CAPTIONS:
            state_time = self.lingering_captions_time
        elif state == WatchState.PRE_CAPTIONS:
            state_time = self.pre_captions_time
        return state_time

    def get_state_i_at_time(self, at_time):
        total_time = 0
        state_i = 0
        for state in self.state_list:
            state_time = get_state_time(self, state)
            total_time += state_time
            if at_time <= total_time:
                break
            state_i += 1
        return state_i, total_time - at_time

    def change_state(self, state, new_state):
        if state == WatchState.ESCAPED:
            if new_state == WatchState.BREATHING:
                # alt tab
                pass
            elif new_state == WatchState.LINGERING_CAPTIONS:
                # play 
                pass
            elif new_state == WatchState.PLAYING:
                pass
            elif new_state == WatchState.PRE_CAPTIONS:
                pass
        elif state == WatchState.BREATHING:
            if new_state == WatchState.LINGERING_CAPTIONS:
                pass
            elif new_state == WatchState.MANUAL_PLAY:
                pass
            elif new_state == WatchState.ESCAPED:
                pass
            else:
                self.invalid_state_transition(new_state)
        elif state == WatchState.LINGERING_CAPTIONS:
            if new_state == WatchState.PLAYING:
                pass
            elif new_state == WatchState.MANUAL_PAUSED:
                pass
            elif new_state == WatchState.ESCAPED:
                pass
            elif new_state == WatchState.QUITTING:
                pass
            else:
                self.invalid_state_transition(new_state)
        elif state == WatchState.PLAYING:
            if new_state == WatchState.PRE_CAPTIONS:
                pass
            elif new_state == WatchState.MANUAL_PAUSED:
                pass
            elif new_state == WatchState.ESCAPED:
                pass
            elif new_state == WatchState.QUITTING:
                pass
            else:
                self.invalid_state_transition(new_state)
        elif state == WatchState.PRE_CAPTIONS:
            if new_state == WatchState.BREATHING:
                pass
            elif new_state == WatchState.MANUAL_PAUSED:
                pass
            elif new_state == WatchState.ESCAPED:
                pass
            elif new_state == WatchState.QUITTING:
                pass
            else:
                self.invalid_state_transition(new_state)
        elif state == WatchState.MANUAL_PAUSED:
            if new_state == WatchState.LINGERING_CAPTIONS:
                pass
            elif new_state == WatchState.PLAYING:
                pass
            elif new_state == WatchState.PRE_CAPTIONS:
                pass
            elif new_state == WatchState.ESCAPED:
                pass
            else:
                self.invalid_state_transition(new_state)
        elif state == WatchState.MANUAL_PLAY:
            if new_state == WatchState.LINGERING_CAPTIONS:
                pass
            elif new_state == WatchState.ESCAPED:
                pass
            else:
                self.invalid_state_transition(new_state)
        state = new_state

    def watch(self):
        self.state = WatchState.ESCAPED
        self.state_i, time_through_state = self.get_state_i_at_time(self.resume_time)
        self.change_state(self.state, self.current_state())

