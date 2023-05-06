import copy
import curses
import textwrap

class ChatWindow:
    # Add the __init__, add_message, and _update_chat_window methods
    # from your original code, and adjust them to fit this class
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.chat_history = [{
            'role':'system',
            'content': "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown."
        }]

        self.window = curses.newpad(10000, curses.COLS)
        self.window.scrollok(False)
        self.scroll_position = 0
        self.old_chat_history = copy.deepcopy(self.chat_history)
        curses.curs_set(0)

    def display_messages(self, window_height: int):
        self.window.erase()
        lines_used = 0

        for i, msg in enumerate(self.chat_history):
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
        self.old_chat_history = copy.deepcopy(self.chat_history)

    def update_last_message(self, new_content):
        self.chat_history[-1]['content'] = new_content
