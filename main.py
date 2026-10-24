import time
import copy
import pyautogui
from pynput import keyboard
from enum import Enum

class WatchState(Enum):
    ESCAPED = 0
    BREATHING = 1
    LINGERING_CAPTIONS = 2
    PLAY = 3
    PRE_CAPTIONS = 4
    MANUAL_PAUSED = 5
    MANUAL_PLAY = 6
    QUITTING = 7

class WatchAction(Enum):
    FOCUS_PLAYER = 0
    FOCUS_SELF = 1
    PLAY = 2
    ENABLE_CAPTIONS = 3
    DISABLE_CAPTIONS = 4
    FULLSCREEN = 5

class WatchInput(Enum):
    NONE = 1000
    FULLSCREEN = 1
    QUIT = 2
    PLAY = 3
    PLAY_AFTER_BREATH = 4

class Monitor:
    watch_inputs = []

    def __init__(self, program):
        self.program = program

    def on_press(self, key):
        watch_input = self.program.key_to_input(key)
        if watch_input != WatchInput.NONE:
            self.watch_inputs.append(watch_input)

    def collapse_input_queue(self):
        watch_input = WatchInput.NONE
        for test in self.watch_inputs:
            if test.value < watch_input.value:
                watch_input = test
        self.watch_inputs = []
        return watch_input

    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    def stop(self):
        self.listener.stop()

def key_to_str(key):
    key_str = ''
    try:
        key_str = key.char
    except AttributeError:
        key_str = str(key)[4:]
    return key_str


def generate_state_list(iterations, start_breathing, end_breathing):
    state_list = [WatchState.ESCAPED]
    if start_breathing:
        state_list.append(WatchState.BREATHING)
    for i in range(iterations):
        state_list.extend([WatchState.LINGERING_CAPTIONS,
                           WatchState.PLAY,
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
        if watch_input == WatchInput.PLAY:
            next_state = WatchState.MANUAL_PLAY
        else:
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
                                    WatchAction.FULLSCREEN,
                                    WatchAction.PLAY])
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.BREATHING:
        if new_state == WatchState.LINGERING_CAPTIONS:
            action_sequence.append(WatchAction.PLAY)
        elif new_state == WatchState.MANUAL_PLAY:
            pass
        elif new_state == WatchState.ESCAPED:
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
        else:
            invalid_state_transition(state, new_state)
    elif state == WatchState.MANUAL_PLAY:
        if new_state == WatchState.LINGERING_CAPTIONS:
            pass
        elif new_state == WatchState.ESCAPED:
            pass
        else:
            invalid_state_transition(state, new_state)
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
    def __init__(self, name, captions_key):
        self.name = name
        self.captions_key = captions_key
        self.fullscreen_key = 'f'
        self.play_key = 'space'

    def press(self, action):
        if action == WatchAction.ENABLE_CAPTIONS or action == WatchAction.DISABLE_CAPTIONS:
            time.sleep(0.1)
            pyautogui.press(self.captions_key)
        elif action == WatchAction.FOCUS_PLAYER:
            time.sleep(0.6)
            pyautogui.hotkey('alt', 'tab')
        elif action == WatchAction.FOCUS_SELF:
            time.sleep(0.6)
            pyautogui.hotkey('alt', 'tab')
        elif action == WatchAction.PLAY:
            time.sleep(0.1)
            pyautogui.press(self.play_key)
        elif action == WatchAction.FULLSCREEN:
            time.sleep(0.3)
            pyautogui.press(self.fullscreen_key)

    def key_to_input(self, key):
        key = key_to_str(key)
        watch_input = WatchInput.NONE
        if key == self.fullscreen_key or key == 'esc':
            watch_input = WatchInput.FULLSCREEN
        elif key == self.play_key:
            watch_input = WatchInput.PLAY
        elif key == 'q':
            watch_input = WatchInput.QUIT
        elif key == 'b':
            watch_input = WatchInput.PLAY_AFTER_BREATH
        return watch_input


# interactive style watch :)
def watch(playing_time, breathing_time, iterations, program_name, captions_count=1, captions_position=1):
    program = Program(program_name, 'c')
    if program_name == 'vlc':
        program = Program(program_name, 'v')
    consumer = Consumer(iterations, breathing_time, playing_time, program, 5, True, True, False, True, captions_count, captions_position, 0.1)
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
        self.start_breathing = start_breathing
        self.end_breathing = end_breathing
        self.captions_count = captions_count
        self.captions_position = captions_position
        self.lingering_captions_time = playing_captions_time
        self.pre_captions_time = playing_captions_time + self.captions_position * additional_captions_time
        self.state_i = 0
        self.transitioning = False # True when inbetween states
        self.start_time = 0
        self.state = WatchState.ESCAPED
        self.monitor = Monitor(program)
        #self.resume_time = resume_time
        if state_history:
            self.state_history = state_history
        else:
            self.state_history = [] # (state, time)


    def current_state(self):
        return self.state_list[self.state_i]

    def press_pyautogui(self, action):
        if action == WatchAction.ENABLE_CAPTIONS:
            for i in range(self.captions_position):
                self.program.press(action)
        elif action == WatchAction.DISABLE_CAPTIONS:
            for i in range(1+self.captions_count-self.captions_position):
                self.program.press(action)
        else:
            self.program.press(action)

    def get_state_time(self, state):
        state_time = 0
        if state == WatchState.BREATHING:
            state_time = self.breathing_time
        elif state == WatchState.PLAY:
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

    def sleep_eye_open(self, duration):
        # add back in idle time
        tick_time = 0.01
        watch_input = WatchInput.NONE
        for i in range(int(duration/tick_time)):
            time.sleep(tick_time)
            watch_input = self.monitor.collapse_input_queue()
            if watch_input != WatchInput.NONE:
                break
        return watch_input
    
    def watch(self):
        self.state = WatchState.ESCAPED
        self.monitor.start()
        i = 0
        while self.state != WatchState.ESCAPED or i == 0:
            watch_input = self.sleep_eye_open(self.get_state_time(self.state))
            next_state, i = get_next_state(self.state, self.iterations, i, watch_input, self.start_breathing, self.end_breathing, False)
            print(next_state, i)
            action_sequence = change_state(self.state, next_state)
            print(action_sequence)
            self.monitor.stop()
            print('TEST')
            for action in action_sequence:
                self.press_pyautogui(action)
            self.state = next_state
            self.monitor.start()
        self.monitor.stop()


