import time
from pynput.keyboard import Controller

keyboard = Controller()

def bot_type_text(text, delay=0.05):
    """Simulate bot typing with uniform delay"""
    for char in text:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(delay)

if __name__ == "__main__":
    print("⏳ Switch to Notepad (or any text field). Typing will start in 3 seconds...")
    time.sleep(3)

    text = "hello" * 50  

    bot_type_text(text, delay=0.01)
    print("✅ Bot typing simulation finished.")
