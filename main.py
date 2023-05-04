import curses
import string
import openai
import textwrap
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

class GPT:
    def __init__(self, model: str = 'gpt-3.5-turbo'):
        self.temperature = 0.7
        self.max_tokens = 10

        if model not in {'gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314'}:
            raise ValueError('Please enter a valid openai model')
        self.model = model

    def call(self, chat_history: list[str], prompt: str) -> str:
        """ Call's GPT and stores the result in chat history. """
        res = openai.ChatCompletion.create(
			model = self.model,
			temperature = self.temperature,
			messages = chat_history,
            max_tokens = self.max_tokens,
            stream = True
		)
        for i in res:
            yield i
        
        output = ''
        for i in res:
            output += i['choices'][0]['delta']['content']
            yield output

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.old_rows = 1
        self.shown_default = False

        # Initialize the screen
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

        # Create a window for the chat history
        self.window = curses.newwin(curses.LINES - 2, curses.COLS, 0, 0)
        self.window.scrollok(False)
        self.scroll_position = 0

        # Create a window for the input box
        self.input_win = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

        self.gpt = GPT()
        self.chat_history = [{
			'role': 'system',
			'content': "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown."
		}]
        self.user_input = ""
        self.show_settings = False

        while True:
            # Get user input
            self.handle_input()

            rows = ( len(self.user_input) // curses.COLS ) + 1
            
            if not self.shown_default:
                self._update_chat_window()
                self.shown_default = True
            if not self.user_input:
                self._reset_input()

    def handle_input(self):
        self.stdscr.keypad(True)
        c = self.stdscr.getch()

         # Arrow up
        if c == curses.KEY_UP:
            self.handle_scroll('up')
            return

        # Arrow down
        if c == curses.KEY_DOWN:
            self.handle_scroll('down')
            return

        # Enter
        if c == ord('\n'):
            self._reset_input()
            self._update_chat_window()
            self.handle_output()
            self.user_input = ""
            return

        # Backspace
        if c == ord('\x7f'):
            self.user_input = self.user_input[:-1]
        elif c != -1 and (chr(c).isalnum() or chr(c).isspace() or chr(c) in string.punctuation):
            self.user_input += chr(c)
 
        wrapped_text = textwrap.wrap('Type here: ' + self.user_input, curses.COLS-1)

        rows = len(wrapped_text)
        if rows != self.old_rows:
            self.input_win.resize(rows, curses.COLS)
            self.input_win.mvwin(curses.LINES - rows, 0)
            self.old_rows = rows
        self.input_win.clear()

        for i, line in enumerate(wrapped_text):
            self.input_win.addstr(i, 0, line)
        self.input_win.refresh()

    def handle_output(self):
        output = ''
        self.chat_history.append({'role':'user','content':self.user_input})
        self.chat_history.append({'role':'assistant','content':''})
        self._update_chat_window()

        combined_output = ''
        for tokens in self.gpt.call(self.chat_history, self.user_input):
            output_delta = tokens['choices'][0]['delta']
            if not output_delta.get('content'): continue # Empty streams

            combined_output += output_delta['content']
            self.chat_history[-1]['content'] = combined_output
            self._update_chat_window()

    '''
    def _update_chat_window(self):
        self.window.erase()
        lines_used = 0
        for i, msg in enumerate(self.chat_history[-(curses.LINES - 3):]):
            name = str.capitalize(msg['role'])
            content = msg['content']
            formatted_str = f'{str.capitalize(name)}: {content}'

            """
            rendered_msg = self._render_markdown(content)
            self.window.addstr(i+lines_used, 0, f"{name}: ")
            for line in rendered_msg:
                self.window.addstr(i+lines_used, len(name)+2, line.text)
                lines_used += 1
            """

            split_text = formatted_str.split('\n')
            for text_item in split_text:
                wrapped_text = textwrap.wrap(text_item, curses.COLS)
                for i, line in enumerate(wrapped_text):
                    self.window.addstr(i+lines_used, 0, line)
                lines_used += len(wrapped_text) + 1

        self.window.refresh()
    '''

    def _update_chat_window(self):
        self.window.erase()
        lines_used = 0
        self.total_lines = sum(len(textwrap.wrap(f"{str.capitalize(msg['role'])}: {msg['content']}", curses.COLS)) for msg in self.chat_history)

        for i, msg in enumerate(self.chat_history):
            name = str.capitalize(msg['role'])
            content = msg['content']
            formatted_str = f'{str.capitalize(name)}: {content}'

            split_text = formatted_str.split('\n')
            for text_item in split_text:
                wrapped_text = textwrap.wrap(text_item, curses.COLS)
                for i, line in enumerate(wrapped_text):
                    if lines_used >= self.scroll_position and lines_used - self.scroll_position < curses.LINES - 2:
                        self.window.addstr(lines_used - self.scroll_position, 0, line)
                    lines_used += 1

        self.window.refresh()

    def _reset_input(self):
        self.input_win.clear()
        self.input_win.addstr(0, 0, 'Type here: ')
        self.input_win.refresh()

    def handle_scroll(self, direction):
        if direction == 'up' and self.scroll_position > 0:
            self.scroll_position -= 1
        elif direction == 'down' and self.scroll_position < self.total_lines - (curses.LINES - 2):
            self.scroll_position += 1
        self._update_chat_window()

    def _render_markdown(self, markdown_text: str):
        console = Console()
        md = Markdown(markdown_text)
        text = console.render(md)
        return text

if __name__ == "__main__":
    curses.wrapper(App)
