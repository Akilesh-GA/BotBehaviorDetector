from pynput import keyboard
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt5.QtCore import QTimer
import sys
import time
import statistics
import math

# Typing data
keystroke_data = []
current_keys = {}
text_buffer = ""
last_key_time = None
IDLE_THRESHOLD = 5  # seconds
ui_window = None

# Entropy calculation
def entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum(p * math.log2(p) for p in prob)

# Keyboard event handlers
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

# Analyze typing and show alert
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

    # Show alert
    QMessageBox.warning(ui_window, "Typing Analysis", msg)

    # Reset typing data
    keystroke_data.clear()
    text_buffer = ""

# Qt-based typing monitor
def check_idle():
    global last_key_time
    now = time.time()
    if last_key_time is None:
        last_key_time = now
    if now - last_key_time >= IDLE_THRESHOLD:
        analyze_typing()
        last_key_time = now

class HiddenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.hide()

if __name__ == "__main__":
    print("Typing monitor started in background.")
    app = QApplication(sys.argv)
    ui_window = HiddenWindow()

    # Start keyboard listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Start Qt timer to monitor idle typing
    timer = QTimer()
    timer.timeout.connect(check_idle)
    timer.start(500)  # check every 0.5 seconds

    sys.exit(app.exec_())
