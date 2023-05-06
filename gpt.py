import threading
import openai

class GPT:
    def __init__(self, model: str = 'gpt-3.5-turbo'):
        self.temperature = 0.5
        self.max_tokens = 2000

        if model not in {'gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314'}:
            raise ValueError('Please enter a valid openai model')
        self.model = model

    def call(self, chat_history: list[str]) -> str:
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

class GPTHandler:
    def __init__(self, window_manager):
        self.model = GPT()
        self.window_manager = window_manager

    def model_output(self):
        self.window_manager.add_chat_message('assistant', '')
        gpt_thread = threading.Thread(target=self._gpt_call)
        gpt_thread.start()

    def _gpt_call(self):
        combined_output = ''
        for tokens in self.model.call(self.window_manager.chat_history):
            output_delta = tokens['choices'][0]['delta']
            if not output_delta.get('content'): continue # Empty streams

            combined_output += output_delta['content']
            self.window_manager.chat_history[-1]['content'] = combined_output
            self.window_manager.chat_window.display_messages(
                self.window_manager.chat_window_height,
                self.window_manager.chat_history
            )
