"""Simple example to accumulate honey from text and voice chat."""

class User:
    def __init__(self):
        self.honey = 0.0

    def add_text_chat(self):
        self.honey += 1

    def add_voice_chat(self):
        self.honey += 0.5

    def get_honey_str(self):
        return f"{self.honey:.1f}"
