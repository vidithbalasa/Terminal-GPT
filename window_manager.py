import os
import curses
import tempfile
import textwrap
import subprocess

class WindowManager:
    def __init__(self, stdscr, input_window, chat_window):
        self.input_window = input_window
        self.chat_window = chat_window
        self.stdscr = stdscr

        self.edit_mode = False

        self.chat_history = [{
            'role':'system',
            'content': "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown."
        }]

    def handle_input(self) -> bool:
        c = self.stdscr.getch()

        # Enter
        if c == ord('\x0a'):
            self.add_chat_message('user', self.input_window.user_input)
            self.input_window.user_input = ""
            return True
        # Edit Mode (Option e)
        elif c == 180:
            pass
            # self.open_edit_mode()
            #self.add_chat_message('L', 'You')
            #self.edit_mode = not self.edit_mode
        # Arrow up
        elif c == curses.KEY_UP:
            self.chat_window.handle_scroll('UP', self.chat_line_count)
            self.chat_window.display_messages(self.chat_window_height, self.chat_history)
        # Arrow down
        elif c == curses.KEY_DOWN:
            self.chat_window.handle_scroll('DOWN', self.chat_line_count)
            self.chat_window.display_messages(self.chat_window_height, self.chat_history)
        # Backspace
        elif c == ord('\x7f'):
            self.input_window.user_input = self.input_window.user_input[:-1]
        # Other character
        elif c != -1 and self.input_window.is_valid_input(c):
            self.input_window.user_input += chr(c)

    def open_edit_mode(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
            # Write the list of strings to the temporary file
            tmp_file.write("\n".join([x['content'] for x in self.chat_history]))
            tmp_file.flush()

            # Close the curses window
            curses.endwin()

            # Open the temporary file in a text editor
            editor = os.getenv("EDITOR", "vim")
            subprocess.call([editor, tmp_file.name])

            # Read the updated list of strings back into the application
            with open(tmp_file.name, "r") as updated_file:
                for idx, content in enumerate(updated_file.read().splitlines()):
                    self.chat_history[idx]['content'] = content 

            # Delete the temporary file
            os.unlink(tmp_file.name)

    def update_window_sizes(self):
        self.input_window.update_window()
        #self.chat_window.window.resize(self.chat_window_height, curses.COLS)
        self.chat_window.window.resize(10000, curses.COLS)
        self.chat_window.display_messages(
            self.chat_window_height,
            self.chat_history
        )

    def add_chat_message(self, role, content):
        self.chat_history.append({'role':role,'content':content})
        self.chat_window.display_messages(self.chat_window_height, self.chat_history)

    @property
    def chat_line_count(self):
        total_lines = 0
        for msg in self.chat_history:
            name, content = msg['role'], msg['content']
            split_msg = f"{name}: {content}".split('\n')
            num_lines = lambda m: len(textwrap.wrap(m, curses.COLS))
            total_lines += sum([num_lines(x) for x in split_msg])
        return total_lines

    @property
    def chat_window_height(self):
        return curses.LINES - self.input_window.old_rows - 1
