from pynput import keyboard
import threading, time, statistics, math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit

keystroke_data = []
current_keys = {}
text_buffer = ""
start_time = None
backspace_count = 0
SESSION_DURATION = 60

ui_window = None

def entropy(s):
    """Calculate entropy of a string"""
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum(p * math.log2(p) for p in prob)

def on_press(key):
    global start_time, text_buffer, current_keys, backspace_count
    now = time.time()
    if start_time is None:
        start_time = now
    try:
        char = key.char
        text_buffer += char
    except AttributeError:
        if key == keyboard.Key.backspace:
            text_buffer = text_buffer[:-1]
            backspace_count += 1
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

    if key == keyboard.Key.esc:
        analyze_typing()
        return False

def monitor_typing():
    global start_time
    while True:
        time.sleep(1)
        if start_time and time.time() - start_time > SESSION_DURATION:
            analyze_typing()
            reset_state()

def reset_state():
    global keystroke_data, current_keys, text_buffer, start_time, backspace_count
    keystroke_data.clear()
    current_keys.clear()
    text_buffer = ""
    start_time = None
    backspace_count = 0

def analyze_typing():
    if not keystroke_data:
        return
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
    result = []
    if superhuman_speed or uniform_typing or low_entropy:
        result.append("⚠️ Suspicious typing detected (possible bot):")
        if superhuman_speed: result.append("   - Speed too high")
        if uniform_typing: result.append("   - Timing too uniform")
        if low_entropy: result.append("   - Low randomness")
    else:
        result.append("✅ Typing pattern appears human.")

    if ui_window:
        ui_window.append_text("\n".join(result))

class TypingMonitorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Typing Pattern Monitor")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        self.label = QLabel("⏳ Monitoring typing... Press ESC to stop")
        self.textbox = QTextEdit()
        self.textbox.setReadOnly(True)

        layout.addWidget(self.label)
        layout.addWidget(self.textbox)
        self.setLayout(layout)

    def append_text(self, text):
        self.textbox.append(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui_window = TypingMonitorUI()
    ui_window.show()

    threading.Thread(target=monitor_typing, daemon=True).start()
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    sys.exit(app.exec_())
