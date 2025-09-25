import sys
import time
import threading
import random
import string
import statistics
import math
from pynput import keyboard
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt5.QtCore import QTimer

keystroke_data = []
current_keys = {}
text_buffer = ""
last_key_time = None
IDLE_THRESHOLD = 5
ui_window = None

keyboard_controller = keyboard.Controller()

def entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum(p * math.log2(p) for p in prob)

def on_press(key):
    global last_key_time, text_buffer, current_keys
    now = time.time()
    last_key_time = now
    try:
        char = key.char
        text_buffer += char
    except AttributeError:
        if key == keyboard.Key.backspace:
            text_buffer = text_buffer[:-1]
        elif key == keyboard.Key.space:
            text_buffer += ' '
        elif key == keyboard.Key.enter:
            text_buffer += '\n'
        else:
            return
    current_keys[key] = now

def on_release(key):
    global keystroke_data
    now = time.time()
    press_time = current_keys.pop(key, None)
    if press_time:
        dwell = now - press_time
        ikd = 0
        if keystroke_data:
            ikd = press_time - keystroke_data[-1]['release_time']
        try:
            char = key.char
        except AttributeError:
            char = str(key)
        keystroke_data.append({
            'char': char,
            'press_time': press_time,
            'release_time': now,
            'dwell_time': dwell,
            'inter_key_delay': ikd
        })

def analyze_typing():
    global keystroke_data, text_buffer
    if not keystroke_data:
        msg = "✅ No typing detected — human idle."
    else:
        chars = len(keystroke_data)
        time_span = keystroke_data[-1]['release_time'] - keystroke_data[0]['press_time']
        words = len(text_buffer.split())
        wpm = (words / time_span) * 60 if time_span > 0 else 0
        dwells = [k['dwell_time'] for k in keystroke_data]
        delays = [k['inter_key_delay'] for k in keystroke_data[1:]]
        dwell_var = statistics.variance(dwells) if len(dwells) > 1 else 0
        delay_var = statistics.variance(delays) if len(delays) > 1 else 0
        char_entropy = entropy(text_buffer)

        uniform_typing = delay_var < 0.0002
        superhuman_speed = wpm > 150
        low_entropy = char_entropy < 2.5 and chars > 30

        if superhuman_speed or uniform_typing or low_entropy:
            msg = "⚠️ Suspicious typing detected!\n"
            if superhuman_speed: msg += "   - Speed too high\n"
            if uniform_typing: msg += "   - Timing too uniform\n"
            if low_entropy: msg += "   - Low randomness\n"
        else:
            msg = "✅ Typing pattern appears human."

    QMessageBox.warning(ui_window, "Typing Analysis", msg)
    keystroke_data.clear()
    text_buffer = ""

def check_idle():
    global last_key_time
    now = time.time()
    if last_key_time is None:
        last_key_time = now
    if now - last_key_time >= IDLE_THRESHOLD:
        QTimer.singleShot(0, analyze_typing)
        last_key_time = now

def generate_random_text(length=50):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def bot_type_text(text, delay=0.01):
    for char in text:
        keyboard_controller.press(char)
        keyboard_controller.release(char)
        time.sleep(delay)

BOT_DURATION = 15

def start_bot():
    time.sleep(3)
    end_time = time.time() + BOT_DURATION
    while time.time() < end_time:
        text = generate_random_text(length=50)
        bot_type_text(text, delay=0.01)
        time.sleep(0.05)

class HiddenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()

if __name__ == "__main__":
    print("Typing monitor started in background.")
    app = QApplication(sys.argv)
    ui_window = HiddenWindow()

    threading.Thread(target=start_bot, daemon=True).start()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    timer = QTimer()
    timer.timeout.connect(check_idle)
    timer.start(500)

    sys.exit(app.exec_())