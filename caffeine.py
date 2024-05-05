"""
Keeps the screen awake by moving the mouse randomly
"""
import threading
import time
from itertools import cycle
import random
import sys

from pynput import keyboard
import pyautogui
from AppKit import NSBundle


class Caffiene:
    """
    Class to encapsulate data and logic

    *runtime*
        duration the instance should run
    *hotcorners*
        prevents mouse from touching the edges of the screen
    *animate*
        flag to determine write to console
    """
    def __init__(self, runtime: int = 0, hotcorners: bool = False, animate: bool = True) -> None:
        self.runtime = runtime
        self.hotcorners = hotcorners
        self.animate = animate

        # running thread initialization
        self._running_thread = threading.Thread(target=self._running_animation)
        self._running_thread.daemon = True

        # keyboard listener initialization
        self._key_listener = keyboard.Listener(
            on_press=self._key_pressed,
            suppress=True
        )
        self._key_listener.daemon = True

        # mouse thread initialization
        self.mouse_thread = threading.Thread(target=self.move_mouse)
        self.mouse_thread.daemon = True

        # pyautogui initialization
        pyautogui.FAILSAFE = True
        self._SCREEN_WIDTH, self._SCREEN_HEIGHT = pyautogui.size()
        self._TWEENING_FUNCTIONS = [
            pyautogui.easeInQuad,
            pyautogui.easeOutQuad,
            pyautogui.easeInOutQuad,
            pyautogui.easeInBounce,
            pyautogui.easeInElastic
        ]

        # prevents icon popup on macos
        app_info = NSBundle.mainBundle().infoDictionary()
        app_info["LSBackgroundOnly"] = "1"

    def _running_animation(self):
        """
        Renders an animation to cli while the instance is running
        """
        LOADING_FRAMES = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]

        start_time = time.monotonic()
        for frame in cycle(LOADING_FRAMES):
            time_delta = int(time.monotonic() - start_time)
            print(f'Running {time_delta}/{self.runtime}s {frame}', flush=True, end='\r')
            time.sleep(0.1)

    def run(self):
        """
        Starts background threads and main logic
        """
        return self.start()

    def start(self):
        """
        Starts background threads and main logic
        """
        self._running_thread.start()
        if self.animate:
            self._key_listener.start()

        reinit_thread = False

        end_time = time.monotonic() + self.runtime
        while self._under_runtime(end_time):
            interval = random.randint(5, 10)
            interval_time = time.monotonic() + interval

            if reinit_thread and not self.mouse_thread.is_alive():
                self.mouse_thread = threading.Thread(target=self.move_mouse)
                self.mouse_thread.daemon = True
                self.mouse_thread.start()
            elif not reinit_thread:
                reinit_thread = True
                self.mouse_thread.start()
            else:
                continue

            while time.monotonic() < interval_time and self._under_runtime(end_time):
                if not self._key_listener.is_alive():
                    self.stop()

                time.sleep(0.01)

    def _under_runtime(self, end_time: float) -> bool:
        """
        Check to keep running the program

        *end_time*
            time the loop should end
        """
        if self.runtime == 0:
            return True

        curr_time = time.monotonic()
        return curr_time < end_time

    def move_mouse(self) -> None:
        """
        Moves mouse to random position on screen
        """
        screen_x = (0, self._SCREEN_WIDTH)
        screen_y = (0, self._SCREEN_HEIGHT)
        if self.hotcorners:
            padding_x = int(self._SCREEN_WIDTH * 0.1)
            padding_y = int(self._SCREEN_HEIGHT * 0.1)

            screen_x = (0 + padding_x, self._SCREEN_WIDTH - padding_x)
            screen_y = (0 + padding_y, self._SCREEN_HEIGHT - padding_y)

        pos_x = random.randint(*screen_x)
        pos_y = random.randint(*screen_y)
        duration = random.randint(1, 5)
        tween = random.choice(self._TWEENING_FUNCTIONS)

        try:
            pyautogui.moveTo(pos_x, pos_y, duration, tween)
        except pyautogui.FailSafeException:
            pass

    def _key_pressed(self, key: keyboard.KeyCode):
        """
        Wrapper to terminate instance from key_listener

        *key*
            key that was pressed
        """
        self.stop()

    def stop(self) -> None:
        """
        Safely terminates instance
        """
        sys.exit()


def caffeine(runtime: int = 0, hotcorners: bool = False) -> None:
    """
    Keeps the screen awake for specifed duration
    """
    caff_job = Caffiene(runtime, hotcorners)
    try:
        caff_job.run()
    except KeyboardInterrupt:
        caff_job.stop()
