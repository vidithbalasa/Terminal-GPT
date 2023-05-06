import time
import threading
import curses
import signal
from chat_window import ChatWindow
from input_window import InputWindow
from window_manager import WindowManager
from gpt import GPTHandler
from functools import partial

def debounce(wait):
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)

            if debounced._timer is not None:
                debounced._timer.cancel()
            debounced._timer = threading.Timer(wait, call_it)
            debounced._timer.start()

        debounced._timer = None
        return debounced

    return decorator

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr

        # Initialize the screen
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

        self.chat_window = ChatWindow(stdscr)
        self.input_window = InputWindow(stdscr)
        self.window_manager = WindowManager(stdscr, self.input_window, self.chat_window)
        self.gpt_handler = GPTHandler(self.window_manager)

        # Set up signal handler for window resizing
        signal.signal(signal.SIGWINCH, partial(self.sigwinch_handler, self.stdscr))

        self.main_loop()

    def main_loop(self):
        while True:
            self.window_manager.update_window_sizes()
            user_call = self.window_manager.handle_input()
            if user_call:
                self.gpt_handler.model_output()
    
    @debounce(0.2)
    def sigwinch_handler(self, stdscr, signum, frame):
        curses.endwin()
        self.stdscr.refresh()
        curses.update_lines_cols()
        self.window_manager.update_window_sizes()
