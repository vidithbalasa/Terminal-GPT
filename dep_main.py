import threading
import curses
import string
import openai
import textwrap
import signal

class GPT:
    def __init__(self, model: str = 'gpt-4'):
        self.temperature = 0.5
        self.max_tokens = 2000

        if model not in {'gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314'}:
            raise ValueError('Please enter a valid openai model')
        self.model = model

    def call(self, chat_history: list[str], prompt: str) -> str:
        """ Calls GPT and stores the result in chat history. """
        res = openai.ChatCompletion.create(
			model = self.model,
			temperature = self.temperature,
			messages = chat_history,
            max_tokens = self.max_tokens,
            stream = True
		)
        for i in res:
            yield i
        
class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.old_rows = 1

        # Initialize the screen
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

        # Create a window for the chat history
        self.window = curses.newpad(10000, curses.COLS)
        self.window.scrollok(False)
        self.scroll_position = 0

        # Create a window for the input box
        self.input_win = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

        self.model = GPT()
        self.chat_history = [{
			'role': 'system',
			'content': "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown."
		}]
        self.user_input = ""
        self.show_settings = False

        while True:
            signal.signal(signal.SIGWINCH, lambda signum, frame: self.sigwinch_handler(signum, frame, self.stdscr))

            self.handle_input()

            self._update_chat_window()

            if not self.user_input:
                self._reset_input()

    def handle_input(self):
        c = self.stdscr.getch()

        # Arrow up
        if c == curses.KEY_UP:
            self._handle_scroll('up')
            return

        # Arrow down
        if c == curses.KEY_DOWN:
            self._handle_scroll('down')
            return

        # Enter
        if c == ord('\n'):
            self._update_chat_window()
            self.handle_output()
            self.user_input = ""
            return

        # Backspace
        if c == ord('\x7f'):
            self.user_input = self.user_input[:-1]
        elif c != -1 and (c in range(65,91) or c in range(97,123) or c in range(48,58) or chr(c).isspace() or chr(c) in string.punctuation):
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

        gpt_thread = threading.Thread(target=self._gpt_call)
        gpt_thread.start()

    def _gpt_call(self):
        combined_output = ''
        for tokens in self.model.call(self.chat_history, self.user_input):
            output_delta = tokens['choices'][0]['delta']
            if not output_delta.get('content'): continue # Empty streams

            combined_output += output_delta['content']
            self.chat_history[-1]['content'] = combined_output
            self._update_chat_window()

    def _update_chat_window(self):
        # Resize the chat window based on the input window size
        chat_window_height = curses.LINES - self.old_rows - 1

        self.window.erase()
        lines_used = 0

        for i, msg in enumerate(self.chat_history):
            name = str.capitalize(msg['role'])
            content = msg['content']
            formatted_str = f'{str.capitalize(name)}: {content}'

            split_text = formatted_str.split('\n')
            for text_item in split_text:
                wrapped_text = textwrap.wrap(text_item, curses.COLS)
                for i, line in enumerate(wrapped_text):
                    self.window.addstr(lines_used, 0, line)
                    lines_used += 1
            self.window.addstr(lines_used, 0, '-'*curses.COLS)
            lines_used += 1

        #self.window.refresh(self.scroll_position, 0, 0, 0, curses.LINES - 3, curses.COLS)
        self.window.refresh(self.scroll_position, 0, 0, 0, chat_window_height, curses.COLS)

    def _reset_input(self):
        self.input_win.clear()
        self.input_win.resize(1, curses.COLS)
        self.input_win.mvwin(curses.LINES - 1, 0)
        self.input_win.addstr(0, 0, f'Type here: {self.user_input}')
        self.input_win.refresh()

    def _handle_scroll(self, direction):
        total_lines = self._calculate_total_lines()
        max_scroll_position = max(0, total_lines - (curses.LINES - 3))

        if direction == 'up' and self.scroll_position > 0:
            self.scroll_position -= 1
        elif direction == 'down' and self.scroll_position < max_scroll_position:
            self.scroll_position += 1
        self._update_chat_window()

    def _render_markdown(self, markdown_text: str):
        console = Console()
        md = Markdown(markdown_text)
        text = console.render(md)
        return text
    
    def _calculate_total_lines(self):
        total_lines = 0
        for msg in self.chat_history:
            name, content = msg['role'], msg['content']
            split_msg = f"{name}: {content}".split('\n')
            num_lines = lambda m: len(textwrap.wrap(m, curses.COLS))
            total_lines += sum([num_lines(x) for x in split_msg])
        return total_lines

    def sigwinch_handler(self, signum, frame, stdscr):
        curses.endwin()
        stdscr.refresh()
        curses.update_lines_cols()

if __name__ == "__main__":
    curses.wrapper(App)
