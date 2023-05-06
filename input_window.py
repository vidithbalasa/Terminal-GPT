import curses
import string
import textwrap

class InputWindow:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.user_input = ""
        self.old_rows = 0
        self.window = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

    def display_input(self):
        wrapped_text = textwrap.wrap('Type here: ' + self.user_input, curses.COLS-1)
        rows = len(wrapped_text)

        if rows != self.old_rows:
            self.window.resize(rows, curses.COLS)
            self.window.mvwin(curses.LINES - rows, 0)
            self.old_rows = rows

        self.window.clear()

        for i, line in enumerate(wrapped_text):
            self.window.addstr(i, 0, line)

        self.window.refresh()

    def is_valid_input(self, user_input) -> bool:
        # a -> z
        if user_input in range(65,91):
            return True
        # A -> Z
        if user_input in range(97,123):
            return True
        # 0 -> 9
        if user_input in range(48,58):
            return True
        if chr(user_input).isspace() or chr(user_input) in string.punctuation:
            return True

        return False

    def update_window(self):
        self.display_input()
        if not self.user_input:
            self.reset_input()

    def reset_input(self):
        self.window.clear()
        self.window.resize(1, curses.COLS)
        self.window.mvwin(curses.LINES - 1, 0)
        self.window.addstr(0, 0, f'Type here: ')
        self.window.refresh()
