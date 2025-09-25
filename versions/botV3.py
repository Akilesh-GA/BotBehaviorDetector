import sys
import time
import threading
import random
import string
from pynput.keyboard import Controller
from PyQt5.QtWidgets import QApplication, QWidget

keyboard = Controller()

def generate_random_text(length=300):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def bot_type_text(text, delay=0.01):
    for char in text:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(delay)

class HiddenBot(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()
        threading.Thread(target=self.start_bot, daemon=True).start()

    def start_bot(self):
        time.sleep(3)
        text = generate_random_text()
        bot_type_text(text, delay=0.01)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hidden_bot = HiddenBot()
    sys.exit(app.exec_())
