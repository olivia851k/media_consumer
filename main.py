import time
import copy
import pyautogui
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QCheckBox, QLineEdit, QComboBox, QSpinBox,
    QLabel, QLineEdit
)
from PyQt6.QtCore import Qt
from pynput import keyboard
from watch_state import *

class CaptionsOptionsType(Enum):
    NONE = 0
    SINGLE = 1
    MULTIPLE = 2

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


def time_spin_box(label, on_changed):
    time_layout = QHBoxLayout()
    time_min = QSpinBox()
    time_min.setMaximum(600)
    time_min.valueChanged.connect(on_changed)
    time_sec = QSpinBox()
    time_sec.setMaximum(59)
    time_sec.setSingleStep(5)
    time_sec.valueChanged.connect(on_changed)
    time_layout.addWidget(QLabel(label))
    time_layout.addWidget(time_min)
    time_layout.addWidget(time_sec)
    return time_layout, time_min, time_sec

def set_checked(check_box, checked):
    if checked:
        check_box.setCheckState(Qt.CheckState.Checked)
    else:
        check_box.setCheckState(Qt.CheckState.Unchecked)

def is_checked(check_box):
    checked_state = check_box.checkState()
    checked = True
    if checked_state == Qt.CheckState.Unchecked:
        checked = False
    return checked


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        program_list = ['vlc', 'youtube', 'natcol']
        self.programs = {}
        for program_name in program_list:
            self.programs[program_name] = Program(program_name)
        self.program = self.programs['vlc']
        self.programs['vlc'].captions_key='v'
        self.programs['vlc'].playing_time=300
        self.programs['vlc'].iterations=6
        self.programs['vlc'].start_breathing=True
        self.programs['natcol'].captions_count = 0
        self.programs['natcol'].captions_position = 0
        self.programs['natcol'].playing_time = 80
        self.programs['natcol'].breathing_time = 20
        self.programs['natcol'].play_key = 'k'
        self.resume_i = 0

        self.init_gui()

    def init_gui(self):
        self.setWindowTitle('Media Consumer')
        self.setGeometry(2000, 200, 400, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        tabs = QTabWidget()
        watch_tab_tab = QWidget()
        profile_tab_tab = QWidget()
        watch_tab = QVBoxLayout()
        profile_tab = QVBoxLayout()

        program_layout = QHBoxLayout()
        self.program_combo_box = QComboBox()
        self.program_combo_box.addItems(self.program_names())
        self.program_combo_box.setCurrentIndex(self.program_names().index(self.program.name))
        self.program_combo_box.currentTextChanged.connect(self.load_program_name)
        program_layout.addWidget(QLabel('Program'))
        program_layout.addWidget(self.program_combo_box)

        iterations_layout = QHBoxLayout()
        self.iterations_spin_box = QSpinBox()
        self.iterations_spin_box.setMaximum(600)
        self.iterations_spin_box.setMinimum(1)
        self.iterations_spin_box.valueChanged.connect(self.update_stats)
        iterations_layout.addWidget(QLabel('Iterations'))
        iterations_layout.addWidget(self.iterations_spin_box)

        playing_time_layout, self.playing_time_min, self.playing_time_sec = time_spin_box('Playing Time', self.update_stats)
        breathing_time_layout, self.breathing_time_min, self.breathing_time_sec = time_spin_box('Breathing Time', self.update_stats)

        breathing_layout = QHBoxLayout()
        self.start_breathing_check_box = QCheckBox('Start Breathing')
        self.end_breathing_check_box = QCheckBox('End Breathing')
        self.start_breathing_check_box.checkStateChanged.connect(self.update_stats)
        self.end_breathing_check_box.checkStateChanged.connect(self.update_stats)
        breathing_layout.addWidget(self.start_breathing_check_box)
        breathing_layout.addWidget(self.end_breathing_check_box)

        self.watch_time_label = QLabel()
        self.total_time_label = QLabel()
        self.end_time_label = QLabel()
        self.update_stats()

        time_stats_layout = QHBoxLayout()
        time_stats_layout.addWidget(self.watch_time_label)
        time_stats_layout.addWidget(self.total_time_label)
        time_stats_layout.addWidget(self.end_time_label)

        self.watch_button = QPushButton('Watch')
        self.watch_button.clicked.connect(self.watch)

        watch_tab.addLayout(iterations_layout)
        watch_tab.addLayout(playing_time_layout)
        watch_tab.addLayout(breathing_time_layout)
        watch_tab.addLayout(breathing_layout)
        watch_tab.addLayout(time_stats_layout)
        watch_tab.addWidget(self.watch_button)


        name_layout = QHBoxLayout()
        self.name_line_edit = QLineEdit()
        self.name_line_edit.editingFinished.connect(self.update_programs)
        name_layout.addWidget(QLabel('Name'))
        name_layout.addWidget(self.name_line_edit)

        captions_time_layout = QHBoxLayout()
        self.captions_time_spin_box = QSpinBox()
        self.captions_time_spin_box.setMaximum(600)
        captions_time_layout.addWidget(QLabel('Show captions while playing for'))
        captions_time_layout.addWidget(self.captions_time_spin_box)
        captions_time_layout.addWidget(QLabel('seconds'))
        self.lingering_captions_check_box = QCheckBox()
        self.pre_captions_check_box = QCheckBox()
        captions_ling_pre_layout = QHBoxLayout()
        captions_ling_pre_layout.addWidget(QLabel('Show before breath'))
        captions_ling_pre_layout.addWidget(self.pre_captions_check_box)
        captions_ling_pre_layout.addWidget(QLabel('Linger after breath'))
        captions_ling_pre_layout.addWidget(self.lingering_captions_check_box)

        profile_tab.addLayout(name_layout)
        profile_tab.addLayout(captions_time_layout)
        profile_tab.addLayout(captions_ling_pre_layout)

        self.load_program(self.program)
        watch_tab_tab.setLayout(watch_tab)
        profile_tab_tab.setLayout(profile_tab)
        tabs.addTab(watch_tab_tab, 'Watch')
        tabs.addTab(profile_tab_tab, 'Profile')
        main_layout.addLayout(program_layout)
        main_layout.addWidget(tabs)

        central_widget.setLayout(main_layout)

    @property
    def iterations(self):
        return self.iterations_spin_box.value()
    @property
    def playing_time(self):
        return self.playing_time_min.value() * 60 + self.playing_time_sec.value()
    @property
    def breathing_time(self):
        return self.breathing_time_min.value() * 60 + self.breathing_time_sec.value()
    @property
    def start_breathing(self):
        return is_checked(self.start_breathing_check_box)
    @property
    def end_breathing(self):
        return is_checked(self.end_breathing_check_box)

    def update_stats(self):
        watch_time = self.playing_time * self.iterations
        watch_time_min = watch_time//60
        watch_time_sec = watch_time%60
        self.watch_time_label.setText(f'Watch Time  {watch_time_min}m {watch_time_sec}s')
        n_breaths = self.iterations
        if self.start_breathing:
            n_breaths += 1
        if not self.end_breathing:
            n_breaths -= 1
        total_time = watch_time + self.breathing_time * n_breaths
        total_time_min = total_time//60
        total_time_sec = total_time%60
        self.total_time_label.setText(f'Total Time  {total_time_min}m {total_time_sec}s')
        end_time = datetime.now() + timedelta(seconds=total_time)
        self.end_time_label.setText(f'End Time  {end_time.hour}:{end_time.minute}')

    def program_names(self):
        names = list(self.programs.keys())
        names.sort()
        return names

    def update_programs(self):
        self.program_combo_box.currentTextChanged.disconnect()
        self.program_combo_box.clear()
        self.save_program()
        self.program_combo_box.addItems(self.program_names())
        self.program_combo_box.setCurrentIndex(self.program_names().index(self.program.name))
        self.program_combo_box.currentTextChanged.connect(self.load_program_name)

    def load_program_name(self, name):
        self.save_program()
        self.load_program(self.programs[name])

    def load_program(self, program):
        self.program = program
        self.iterations_spin_box.setValue(program.iterations)
        self.playing_time_min.setValue(program.playing_time//60)
        self.playing_time_sec.setValue(program.playing_time%60)
        self.breathing_time_min.setValue(program.breathing_time//60)
        self.breathing_time_sec.setValue(program.breathing_time%60)
        set_checked(self.start_breathing_check_box, program.start_breathing)
        set_checked(self.end_breathing_check_box, program.end_breathing)

        self.name_line_edit.setText(program.name)
        self.captions_time_spin_box.setValue(program.playing_captions_time)
        set_checked(self.lingering_captions_check_box, program.lingering_captions)
        set_checked(self.pre_captions_check_box, program.pre_captions)

    def save_program(self):
        self.program.iterations = self.iterations
        self.program.playing_time = self.playing_time
        self.program.breathing_time = self.breathing_time
        self.program.start_breathing = self.start_breathing
        self.program.end_breathing = self.end_breathing

        old_name = self.program.name
        self.program.name = self.name_line_edit.text()
        if old_name != self.program.name:
            self.programs[self.program.name] = self.program
            self.programs.pop(old_name)
        self.program.playing_captions_time = self.captions_time_spin_box.value()
        self.program.lingering_captions = is_checked(self.lingering_captions_check_box)
        self.program.pre_captions = is_checked(self.pre_captions_check_box)

    def new_consumer(self):
        self.save_program()
        self.consumer = Consumer(self.program)

    def watch(self):
        self.new_consumer()
        self.resume_i = self.consumer.watch()
        self.update_stats()

    def resume(self):
        self.new_consumer()
        self.consumer.watch(i = self.resume_i)
        self.update_stats()


@dataclass
class Program:
    name: str
    play_key: str = 'space'
    captions_key: str = 'c'
    fullscreen_key: str = 'f'
    
    iterations: int = 3
    playing_time: int = 90
    breathing_time: int = 25
    playing_captions_time: int = 5
    lingering_captions: bool = False
    pre_captions: bool = True
    start_breathing: bool = False
    end_breathing: bool = True
    captions_count: int = 1
    captions_position: int = 1
    additional_captions_time: float = 0.1

    def __init__(self, name):
        self.name = name
        self.captions_key = 'c'
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

    def press_pyautogui(self, action):
        if action == WatchAction.ENABLE_CAPTIONS:
            for i in range(self.captions_position):
                self.press(action)
        elif action == WatchAction.DISABLE_CAPTIONS:
            for i in range(1+self.captions_count-self.captions_position):
                self.press(action)
        else:
            self.press(action)


# interactive style watch :)
def watch(playing_time, breathing_time, iterations, program_name, captions_count=1, captions_position=1):
    program = Program(program_name)
    if program_name == 'vlc':
        program = Program(program_name)
        program.captions_key = 'v'
    if program_name == 'tnc':
        program.play_key = 'k'
        captions_count = 0
        captions_position = 0
    consumer = Consumer(iterations, breathing_time, playing_time, program, 5, True, True, False, True, captions_count, captions_position, 0.1)
    consumer.watch()

# the cheeky edge cases are what happens when the user pressed a button during transition
class Consumer:
    def __init__(self, program, state_history=None):
#        self.press_key = press_key
#        self.watch_wait = watch_wait # returns elapsed_time, keys_pressed
        self.program = program
        if self.program.lingering_captions:
            self.lingering_captions_time = self.program.playing_captions_time
        else:
            self.lingering_captions_time = self.program.additional_captions_time
        self.pre_captions_time = self.program.captions_position * self.program.additional_captions_time
        if self.program.pre_captions:
            self.pre_captions_time += self.program.playing_captions_time
        self.state_i = 0
        self.transitioning = False # True when inbetween states
        self.start_time = 0
        self.state = WatchState.START
        self.monitor = Monitor(program)
        if state_history:
            self.state_history = state_history
        else:
            self.state_history = [] # (state, time)

    def get_state_time(self, state):
        state_time = 0
        if state == WatchState.BREATHING:
            state_time = self.program.breathing_time
        elif state == WatchState.PLAY:
            state_time = self.program.playing_time - self.lingering_captions_time - self.pre_captions_time
        elif state == WatchState.LINGERING_CAPTIONS:
            state_time = self.lingering_captions_time
        elif state == WatchState.PRE_CAPTIONS:
            state_time = self.pre_captions_time
        elif state == WatchState.MANUAL_PAUSED:
            state_time = 10
        return state_time

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
    
    def watch(self, i=0):
        self.state = WatchState.START
        self.monitor.start()
        while self.state != WatchState.ESCAPED:
            watch_input = self.sleep_eye_open(self.get_state_time(self.state))
            next_state, i = get_next_state(self.state, self.program.iterations, i, watch_input, self.program.start_breathing, self.program.end_breathing, False)
            print(next_state, i)
            action_sequence = change_state(self.state, next_state, watch_input)
            print(action_sequence)
            self.monitor.stop()
            for action in action_sequence:
                self.program.press_pyautogui(action)
            self.state = next_state
            self.monitor.start()
        time.sleep(0.1)
        self.monitor.stop()
        return i

def start_gui():
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())

