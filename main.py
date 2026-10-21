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

class WatchAction(Enum):
    FOCUS_PLAYER = 0
    FOCUS_SELF = 1
    PLAYING = 2
    ENABLE_CAPTIONS = 3
    DISABLE_CAPTIONS = 4
    FULLSCREEN = 5

class WatchInput(Enum):
    NONE = 0
    FULLSCREEN = 1
    QUIT = 2
    PLAYING = 3

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

def invalid_state_transition(state, new_state):
    raise Exception(f'Invalid transition from {state.name} to {new_state.name}')

# question as to whether to add in a breathing state after a manual pause if start_breathing == True
def get_next_state(state, iterations, i, watch_input, start_breathing, end_breathing, should_skip):
    next_state = WatchState.ESCAPED
    if watch_input == WatchInput.FULLSCREEN:
        next_state = WatchState.ESCAPED
    elif state == WatchState.ESCAPED:
        if start_breathing:
            next_state = WatchState.BREATHING
        else:
            next_state = WatchState.LINGERING_CAPTIONS
            i += 1
    elif state == WatchState.BREATHING:
        if watch_input == WatchInput.PLAYING:
            next_state = WatchState.MANUAL_PLAY
        else:
            if i == iterations:
                next_state = WatchState.ESCAPED
            else:
                next_state = WatchState.LINGERING_CAPTIONS
                i += 1
    elif state == WatchState.LINGERING_CAPTIONS:
        if watch_input == WatchInput.PLAYING:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.PLAYING
    elif state == WatchState.PLAYING:
        if watch_input == WatchInput.PLAYING:
            next_state = WatchState.MANUAL_PAUSED
        else:
            next_state = WatchState.PRE_CAPTIONS
    elif state == WatchState.PRE_CAPTIONS:
        if watch_input == WatchInput.PLAYING:
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
        if watch_input == WatchInput.PLAYING:
            if i == iterations and should_skip:
                if end_breathing:
                    next_state = WatchState.BREATHING
                else:
                    next_state = WatchState.ESCAPED
            else:
                if should_skip:
                    i += 1
                next_state = WatchState.LINGERING_CAPTIONS
        else:
            next_state = WatchState.ESCAPED
        #manual play, end clause
    elif state == WatchState.MANUAL_PLAY:
        if i == iterations:
            next_state = WatchState.ESCAPED
        else:
            next_state = WatchState.LINGERING_CAPTIONS
            i += 1
    return next_state, i


def change_state(state, new_state):
    action_sequence = []
    if state == WatchState.ESCAPED:
        if new_state == WatchState.BREATHING:
            action_sequence.append(WatchAction.FOCUS_PLAYER)
        elif new_state == WatchState.LINGERING_CAPTIONS:
            action_sequence.extend([WatchAction.FOCUS_PLAYER,
                                    WatchAction.PLAYING])
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.BREATHING:
        if new_state == WatchState.LINGERING_CAPTIONS:
            action_sequence.append(WatchAction.PLAYING)
        elif new_state == WatchState.MANUAL_PLAY:
            pass
        elif new_state == WatchState.ESCAPED:
            action_sequence.append(WatchAction.FOCUS_SELF)
        else:
            invalid_state_transition(new_state)
    elif state == WatchState.LINGERING_CAPTIONS:
        if new_state == WatchState.PLAYING:
            action_sequence.append(WatchAction.DISABLE_CAPTIONS)
        elif new_state == WatchState.MANUAL_PAUSED:
            pass
        elif new_state == WatchState.ESCAPED:
            action_sequence.extend([WatchAction.PLAYING,
                                    WatchAction.FOCUS_SELF])
        elif new_state == WatchState.QUITTING:
            action_sequence.extend([WatchAction.FULLSCREEN,
                                    WatchAction.FOCUS_SELF])
        else:
            invalid_state_transition(new_state)
    elif state == WatchState.PLAYING:
        if new_state == WatchState.PRE_CAPTIONS:
            action_sequence.append(WatchAction.ENABLE_CAPTIONS)
        elif new_state == WatchState.MANUAL_PAUSED:
            action_sequence.append(WatchAction.ENABLE_CAPTIONS)
        elif new_state == WatchState.ESCAPED:
            action_sequence.extend([WatchAction.PLAYING,
                                    WatchAction.ENABLE_CAPTIONS,
                                    WatchAction.FOCUS_SELF])
        elif new_state == WatchState.QUITTING:
            action_sequence.extend([WatchAction.FULLSCREEN,
                                    WatchAction.ENABLE_CAPTIONS,
                                    WatchAction.FOCUS_SELF])
        else:
            invalid_state_transition(new_state)
    elif state == WatchState.PRE_CAPTIONS:
        if new_state == WatchState.BREATHING:
            action_sequence.append(WatchAction.PLAYING)
        elif new_state == WatchState.MANUAL_PAUSED:
            pass
        elif new_state == WatchState.ESCAPED:
            action_sequence.extend([WatchAction.PLAYING,
                                    WatchAction.FOCUS_SELF])
        elif new_state == WatchState.QUITTING:
            action_sequence.extend([WatchAction.FULLSCREEN,
                                    WatchAction.FOCUS_SELF])
        else:
            invalid_state_transition(new_state)
    elif state == WatchState.MANUAL_PAUSED:
        if new_state == WatchState.LINGERING_CAPTIONS:
            pass
        elif new_state == WatchState.PLAYING:
            action_sequence.append(WatchAction.DISABLE_CAPTIONS)
        elif new_state == WatchState.PRE_CAPTIONS:
            pass
        elif new_state == WatchState.ESCAPED:
            action_sequence.append(WatchAction.FOCUS_SELF)
            pass
        else:
            invalid_state_transition(new_state)
    elif state == WatchState.MANUAL_PLAY:
        if new_state == WatchState.LINGERING_CAPTIONS:
            pass
        elif new_state == WatchState.ESCAPED:
            pass
        else:
            invalid_state_transition(new_state)
    return action_sequence


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

class Program:
    def __init__(self, captions_key):
        self.captions_key = captions_key

    def press(self, action):
        if action == WatchState.ENABLE_CAPTIONS or action == WatchState.DISABLE_CAPTIONS:
            pyautogui.press(self.captions_key)

# interactive style watch :)
def watch(playing_time, breathing_time, iterations, program_name, captions_count=1, captions_position=1):
    program = Program('c')
    if program_name == 'vlc':
        program = Program('v')
    consumer = Consumer(iterations, breathing_time, playing_time, program, 5, True, True, False, True, captions_count, captions_posiition, 0.1)
    consumer.watch()

# the cheeky edge cases are what happens when the user pressed a button during transition
class Consumer:
    def __init__(self, iterations, breathing_time, playing_time, program,
            playing_captions_time, lingering_captions, pre_captions,
            start_breathing, end_breathing,
            captions_count, captions_position, additional_captions_time,
            state_history=None):
#        self.press_key = press_key
#        self.watch_wait = watch_wait # returns elapsed_time, keys_pressed
        self.breathing_time = breathing_time
        self.playing_time = playing_time
        self.iterations = iterations
        self.program = program
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
        if state_history:
            self.state_history = state_history
        else:
            self.state_history = [] # (state, time)


    def current_state(self):
        return self.state_list[self.state_i]

    def press_pyautogui(self, action):
        if action == WatchAction.FOCUS_PLAYER:
            time.sleep(0.6)
            pyautogui.hotkey('alt', 'tab')
        elif action == WatchAction.FOCUS_SELF:
            time.sleep(0.6)
            pyautogui.hotkey('alt', 'tab')
        elif action == WatchAction.PLAYING:
            time.sleep(0.1)
            pyautogui.press('space')
        elif action == WatchAction.ENABLE_CAPTIONS:
            for i in range(self.captions_position):
                time.sleep(self.additional_captions_time)
                self.program.press(action)
        elif action == WatchAction.DISABLE_CAPTIONS:
            for i in range(1+self.captions_count-self.captions_position):
                time.sleep(self.additional_captions_time)
                self.program.press(action)
        elif action == WatchAction.FULLSCREEN:
            time.sleep(0.3)
            pyautogui.press('f')


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

    def watch(self):
        self.state = WatchState.ESCAPED
        i = 0
        while self.state != WatchState.ESCAPED or i == 0:
            next_state, i = get_next_state(self.state, self.iterations, i, WatchInput.NONE, self.start_breathing, self.end_breathing, False)
            action_sequence = change_state(self.state, next_state)
            for action in action_sequence:
                self.press_pyautiogui(action)
            self.state = next_state


