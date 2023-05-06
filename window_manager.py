import curses

class WindowManager:
    def __init__(self, stdscr, input_window, chat_window):
        self.input_window = input_window
        self.chat_window = chat_window
        self.stdscr = stdscr

    def add_chat_message(self, role, content):
        self.chat_history.append({'role':role,'content':content})
        self.chat_window.display_messages(self.chat_window_height)

    def update_last_message(self, new_content):
        self.chat_window.update_last_message(new_content)

    def handle_input(self) -> bool:
        c = self.input_window.window.getch()

        # Enter
        if c == ord('\n'):
            self.add_chat_message('user', self.input_window.user_input)
            self.input_window.user_input = ""
            return True
        # Backspace
        if c == ord('\x7f'):
            self.input_window.user_input = self.input_window.user_input[:-1]
        # Other character
        elif c != -1 and self.input_window.is_valid_input(c):
            self.input_window.user_input += chr(c)

        self.input_window.display_input()

    def update_window_sizes(self):
        self.update_chat_window()
        self.update_input_window()

    def update_chat_window(self):
        # Update the chat window size based on the input window size
        self.chat_window.window.resize(self.chat_window_height, curses.COLS)
        self.chat_window.display_messages(window_height=self.chat_window_height)

    def update_input_window(self):
        self.input_window.window.resize(1, curses.COLS)
        self.input_window.window.mvwin(curses.LINES - 1, 0)
        self.input_window.reset_input()

    @property
    def chat_window_height(self):
        return curses.LINES - self.input_window.old_rows - 1
        
    @property
    def chat_history(self):
        return self.chat_window.chat_history
