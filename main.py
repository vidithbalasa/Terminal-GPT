import threading
import string
import time
import curses
import openai
import argparse
import textwrap

class GPT:
    def __init__(self, model: str = 'gpt-4'):
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

    def fake_call(self, *args):
        output = [x+' ' for x in 'Hello this is vidith here to tell you somethin'.split(' ')]
        for i in output:
            yield {'choices': [{'delta': {'content': i}}]}
            time.sleep(1)
		
class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.old_rows = 1

        # Initialize the screen
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)

        # Create a window for the chat history
        self.window = curses.newwin(curses.LINES - 2, curses.COLS, 0, 0)
        self.window.scrollok(True)

        # Create a window for the input box
        self.input_win = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

        self.gpt = GPT()
        self.chat_history = [{
			'role': 'system',
			'content': "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown."
		}]
        self.user_input = ""

        while True:
            # Get user input
            self.handle_input()

            rows = ( len(self.user_input) // curses.COLS ) + 1
            
            # Update chat history window
            if len(self.chat_history) == 1:
                self._update_chat_window()

            # Default input box message
            if self.user_input == "":
                self._reset_input()

    def handle_input(self):
        c = self.stdscr.getch()

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
        elif c != -1:
            self.user_input += chr(c)
 
        rows = ( len(self.user_input) // curses.COLS ) + 1
        if self.old_rows != rows:
            self.input_win.resize(rows, curses.COLS)
            self.input_win.mvwin(curses.LINES - rows, 0)
        self.input_win.clear()
        
        wrapped_text = textwrap.wrap(self.user_input, curses.COLS)
        for i, line in enumerate(wrapped_text):
            if i == 0:
                line = 'Type here: ' + line
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

    def _update_chat_window(self):
        self.window.erase()
        lines_used = 0
        for i, msg in enumerate(self.chat_history[-(curses.LINES - 3):]):
            name = str.capitalize(msg['role'])
            content = msg['content']
            formatted_str = f'{str.capitalize(name)}: {content}'

            wrapped_text = textwrap.wrap(formatted_str, curses.COLS)
            for i, line in enumerate(wrapped_text):
                self.window.addstr(i+lines_used, 0, line)
            lines_used += len(wrapped_text)

        self.window.refresh()

    def _reset_input(self):
        self.input_win.clear()
        self.input_win.addstr(0, 0, 'Type here: ')
        self.input_win.refresh()

if __name__ == "__main__":
    curses.wrapper(App)
