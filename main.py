import time
import copy
from pynput import keyboard
from enum import Enum

class WatchState(Enum):
    ESCAPED = 0
    BREATHING = 1
    PLAYING = 2
    PLAYING_CAPTIONS = 3
    MANUAL_PAUSED = 4
    MANUAL_PLAY = 5

def generate_state_list(iterations, start_breathing, end_breathing):
    state_list = [WatchState.ESCAPED]
    if start_breathing:
        state_list.append(WatchState.BREATHING)
    for i in range(iterations):
        state_list.extend([WatchState.PLAYING_CAPTIONS,
                           WatchState.PLAYING,
                           WatchState.PLAYING_CAPTIONS,
                           WatchState.BREATHING])
    if not end_breathing:
        state_list = state_list[:-1]
    state_list.append(WatchState.ESCAPED)
    return state_list

def generate_next_state_times(state_list, breathing_time, playing_time, lingering_captions_time, pre_captions_time):
    next_state_times = [0]
    previous_state = state_list[0]
    state_time = 0
    for state in state_list[1:]:
        if state == WatchState.BREATHING:
            state_time += breathing_time
        elif state == WatchState.PLAYING:
            state_time += playing_time - lingering_captions_time - pre_captions_time
        elif state == WatchState.PLAYING_CAPTIONS:
            if previous_state == WatchState.PLAYING:
                state_time += pre_captions_time
            else:
                state_time += lingering_captions_time
        previous_state = state
        next_state_times.append(state_time)
    return next_state_times

# the cheeky edge cases are what happens when the user pressed a button during transition
class Consumer:
    def __init__(self):
        self.start_breathing = False
        self.end_breathing = True
        self.breathing_time = 25
        self.playing_time = 90
        self.playing_captions_time = 5
        self.additional_captions_time = 0.1
        self.captions_count = 1
        self.captions_position = 1
        self.lingering_captions_time = self.playing_captions_time
        self.pre_captions_time = self.playing_captions_time + self.captions_position * self.additional_captions_time
        self.iterations = 3
        self.state_i = 0
        self.state_list = generate_state_list(self.iterations, self.start_breathing, self.end_breathing)
        self.next_state_times = generate_next_state_times(self.state_list, self.breathing_time, self.playing_time, self.playing_captions_time, self.playing_captions_time)
        self.transitioning = False # True when inbetween states

    def invalid_state_transition(self, new_state):
        raise Exception(f'Invalid transition from {self.state.name} to {new_state.name}')

    def state(self):
        return self.state_list[self.state_i]

    def change_state(self, new_state):
        if self.state == WatchState.ESCAPED:
            if new_state == WatchState.BREATHING:
                # alt tab
                pass
            elif new_state == WatchState.PLAYING_CAPTIONS:
                # play 
                pass
            else:
                self.invalid_state_transition(new_state)
        elif self.state == WatchState.BREATHING:
            if new_state == WatchState.PLAYING:
                pass
            elif new_state == WatchState.PLAYING_CAPTIONS:
                pass
            elif new_state == WatchState.MANUAL_PLAY:
                pass
        state = new_state

