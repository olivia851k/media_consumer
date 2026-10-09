import time
import copy
import cv2
import pyautogui
from pynput import keyboard


class Watcher:
    escaped = False
    paused = True
    quited = False
    max_idle_time = 240

    def on_press(self, key):
        try:
            if key.char == 'f':
                self.escaped = True
            elif key.char == 'q':
                self.quited = True
        except AttributeError:
            if key == keyboard.Key.space:
                self.paused = not self.paused
            elif key == keyboard.Key.esc:
                self.escaped = True

    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
    def stop(self):
        self.listener.stop()


def sleep_eye_open(duration, watcher):
    watcher.start()
    changed = False
    paused = watcher.paused
    escaped = watcher.escaped
    quited = watcher.quited
    idle_time = 0
    tick_time = 0.01
    for i in range(int(duration/tick_time)):
        time.sleep(tick_time)
        idle_time += tick_time
        if idle_time > watcher.max_idle_time:
            pyautogui.press("'")
            idle_time = 0
        if watcher.paused != paused or \
           watcher.escaped != escaped or \
           watcher.quited != quited:
            changed = True
            break
    watcher.stop()
    return changed

def sleep_not_paused(duration, program, watcher, i_sub_track):
    changed = sleep_eye_open(duration, watcher)
    if changed:
        if watcher.escaped:
            manual_escape(program, watcher.paused, i_sub_track)
        elif watcher.paused:
            enable_subs(program, i_sub_track)
            watcher.start()
            while not watcher.escaped and watcher.paused:
                time.sleep(0.01)
            watcher.stop()
            if watcher.escaped:
                manual_escape(program, watcher.paused, i_sub_track)
    return changed

def enable_subs(program, i_sub_track):
    if program == 'youtube':
        pyautogui.press('c')
        time.sleep(0.1)
    if program == 'vlc':
        for i in range(i_sub_track):
            pyautogui.press('v')
            time.sleep(0.1)

def disable_subs(program, n_sub_tracks, i_sub_track):
    if program == 'youtube':
        time.sleep(0.1)
        pyautogui.press('c')
    if program == 'vlc' and n_sub_tracks > 0:
        for i in range(1+n_sub_tracks-i_sub_track):
            time.sleep(0.1)
            pyautogui.press('v')

def manual_escape(program, paused, i_sub_track):
    if not paused:
        time.sleep(0.1)
        pyautogui.press('space')
        enable_subs(program, i_sub_track)
    time.sleep(0.5)
    pyautogui.hotkey('alt', 'tab')

def quit_watch(program, paused, i_sub_track):
    if not paused:
        time.sleep(0.1)
        enable_subs(program, i_sub_track)
    time.sleep(0.1)
    pyautogui.press('esc')
    time.sleep(0.5)
    pyautogui.hotkey('alt', 'tab')

def watch(play_time, pause_time, count, program, n_sub_tracks=0, i_sub_track=0, keep_awake_time=250, fullscreen=True):
    watcher = Watcher()
    pre_sub_time = 5 + i_sub_track*0.1
    pre_sub = False
    if program == 'vlc':
        pre_sub = True
        play_time -= pre_sub_time
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.1)
    if fullscreen:
        pyautogui.press('f')
        time.sleep(0.1)
    i = 0
    while i < count:
        if watcher.paused:
            pyautogui.press('space')
        watcher.paused = False
        disable_subs(program, n_sub_tracks, i_sub_track)
        changed = sleep_not_paused(play_time, program, watcher, i_sub_track)
        if changed:
            if watcher.escaped:
                return
            elif watcher.quited:
                quit_watch(program, watcher.paused, i_sub_track)
                return
            elif not watcher.paused:
                continue
        enable_subs(program, i_sub_track)
        if pre_sub:
            changed = sleep_not_paused(pre_sub_time, program, watcher, i_sub_track)
            if changed:
                if watcher.escaped:
                    return
                elif watcher.quited:
                    quit_watch(program, watcher.paused, i_sub_track)
                    return
                elif not watcher.paused:
                    continue
        pyautogui.press('space')
        watcher.paused = True
        changed = sleep_eye_open(pause_time, watcher)
        if changed:
            if watcher.escaped:
                manual_escape(program, watcher.paused, i_sub_track)
                return
            elif watcher.quited:
                quit_watch(program, watcher.paused, i_sub_track)
                return
            elif not watcher.paused and i == count - 1:
                time.sleep(0.6)
                pyautogui.press('space')
                watcher.paused = True
                time.sleep(0.1)
        i += 1
    if fullscreen:
        pyautogui.press('f')
        time.sleep(0.1)
    pyautogui.hotkey('alt', 'tab')
    time.sleep(0.1)
    pyautogui.press('up')


