import sys
import time
import threading
from pynput.keyboard import Controller
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

keyboard = Controller()

def bot_type_text(text, delay=0.03):
    for char in text:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(delay)

class BotTyperUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot Typing Simulator")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Press 'Start Bot' and switch to Notepad within 3 seconds.")
        layout.addWidget(self.label)

        self.start_button = QPushButton("Start Bot Typing")
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def start_bot(self):
        self.label.setText("Bot Simulation Testing Started..")
        threading.Thread(target=self.run_bot, daemon=True).start()

    def run_bot(self):
        time.sleep(3)
        text = "hello world" * 50
        bot_type_text(text, delay=0.02)
        self.label.setText("✅ Bot typing finished.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BotTyperUI()
    window.show()
    sys.exit(app.exec_())
