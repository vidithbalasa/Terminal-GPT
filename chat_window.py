import copy
import curses
import textwrap

class ChatWindow:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.window = curses.newpad(10000, curses.COLS)
        self.window.scrollok(False)
        self.scroll_position = 0

    def display_messages(self, window_height: int, chat_history: list):
        #chat_window_height = window_height - 1
        #self.window = curses.newpad(10000, curses.COLS)
        #self.window.scrollok(False)

        self.window.resize(10000, curses.COLS)

        self.window.erase()
        lines_used = 0

        for i, msg in enumerate(chat_history):
            name = str.capitalize(msg['role'])
            formatted_str = f'{name}: {msg["content"]}'

            split_text = formatted_str.split('\n')
            for text_item in split_text:
                wrapped_text = textwrap.wrap(text_item, curses.COLS)
                for i, line in enumerate(wrapped_text):
                    self.window.addstr(lines_used, 0, line)
                    lines_used += 1
            self.window.addstr(lines_used, 0, '-'*curses.COLS)
            lines_used += 1

        self.window.refresh(self.scroll_position, 0, 0, 0, window_height, curses.COLS)

    def handle_scroll(self, direction, total_lines):
        max_scroll_position = max(0, total_lines - (curses.LINES - 1))

        if direction == 'UP' and self.scroll_position > 0:
            self.scroll_position -= 1
        elif direction == 'DOWN' and self.scroll_position < max_scroll_position:
            self.scroll_position += 1
