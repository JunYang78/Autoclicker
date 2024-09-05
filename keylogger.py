import tkinter as tk
import threading
import json
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

mouse_controller = MouseController()
keyboard_controller = KeyboardController()

recording = []
is_recording = False
mouse_listener = None
keyboard_listener = None

def on_press(key):
    if not is_recording:
        return
    try:
        json_object = {
            'action': 'pressed_key',
            'key': key.char
        }
    except AttributeError:
        json_object = {
            'action': 'pressed_key',
            'key': str(key)
        }
    recording.append(json_object)

def on_release(key):
    if not is_recording:
        return
    try:
        json_object = {
            'action': 'released_key',
            'key': key.char
        }
    except AttributeError:
        json_object = {
            'action': 'released_key',
            'key': str(key)
        }
    recording.append(json_object)

def on_click(x, y, button, pressed):
    if not is_recording:
        return
    json_object = {
        'action': 'clicked' if pressed else 'unclicked',
        'button': str(button),
        'x': x,
        'y': y
    }
    recording.append(json_object)

def on_scroll(x, y, dx, dy):
    if not is_recording:
        return
    json_object = {
        'action': 'scroll',
        'vertical_direction': int(dy),
        'horizontal_direction': int(dx),
        'x': x,
        'y': y
    }
    recording.append(json_object)

def start_recording():
    global is_recording, mouse_listener, keyboard_listener
    is_recording = True

    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)

    mouse_listener = mouse.Listener(
        on_click=on_click,
        on_scroll=on_scroll)

    keyboard_listener.start()
    mouse_listener.start()

    keyboard_listener.join()
    mouse_listener.join()

def stop_recording():
    global is_recording
    is_recording = False

    if keyboard_listener:
        keyboard_listener.stop()
    if mouse_listener:
        mouse_listener.stop()

    with open('recording.json', 'w') as f:
        json.dump(recording, f)

    print("Recording stopped and saved to recording.json")

def playback_actions():
    with open('recording.json', 'r') as f:
        actions = json.load(f)
    
    for action in actions:
        if action['action'] == 'clicked':
            button = Button.left if action['button'] == 'Button.left' else Button.right
            mouse_controller.position = (action['x'], action['y'])
            mouse_controller.press(button)
        elif action['action'] == 'unclicked':
            button = Button.left if action['button'] == 'Button.left' else Button.right
            mouse_controller.position = (action['x'], action['y'])
            mouse_controller.release(button)
        elif action['action'] == 'scroll':
            mouse_controller.position = (action['x'], action['y'])
            mouse_controller.scroll(action['horizontal_direction'], action['vertical_direction'])
        elif action['action'] == 'pressed_key':
            key = Key.esc if action['key'] == 'Key.esc' else action['key']
            keyboard_controller.press(key)
        elif action['action'] == 'released_key':
            key = Key.esc if action['key'] == 'Key.esc' else action['key']
            keyboard_controller.release(key)

def start_thread():
    threading.Thread(target=start_recording).start()

app = tk.Tk()
app.title("Recording Application")

start_button = tk.Button(app, text="Start Recording", command=start_thread)
start_button.pack(pady=20)

stop_button = tk.Button(app, text="Stop Recording", command=stop_recording)
stop_button.pack(pady=20)

playback_button = tk.Button(app, text="Playback Actions", command=lambda: threading.Thread(target=playback_actions).start())
playback_button.pack(pady=20)

app.mainloop()
