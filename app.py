import curses
import signal
from chat_window import ChatWindow
from input_window import InputWindow
from window_manager import WindowManager
from gpt import GPTHandler

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.chat_window = ChatWindow(stdscr)
        self.input_window = InputWindow(stdscr)
        self.window_manager = WindowManager(stdscr, self.input_window, self.chat_window)
        self.gpt_handler = GPTHandler(self.window_manager)

        # Set up signal handler for window resizing
        signal.signal(signal.SIGWINCH, lambda signum, frame: self.sigwinch_handler(signum, frame, self.stdscr))

        self.main_loop()

    def main_loop(self):
        while True:
            self.window_manager.update_window_sizes()
            user_call = self.window_manager.handle_input()
            if user_call:
                self.gpt_handler.model_output()
    
    def sigwinch_handler(self, signum, frame, stdscr):
        curses.endwin()
        self.stdscr.refresh()
        curses.update_lines_cols()
        self.window_manager.update_window_sizes()
