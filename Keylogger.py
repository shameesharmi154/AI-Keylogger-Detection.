import tkinter as tk
from tkinter import *
from tkinter import messagebox
from pynput import keyboard
import threading
import time
import json
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

root = tk.Tk()
root.title("AI-Based Keylogger Detection System")
root.geometry("950x600")
root.configure(bg="#e3f2fd")
root.resizable(False, False)

listener = None
running = False
masked = False
keystrokes = ""
key_times = []
last_alert_time = 0

status_text = StringVar(value="Status: Idle")
anomaly_text = StringVar(value="Anomaly: None")
speed_text = StringVar(value="Typing Speed: 0 keys/sec")

model = IsolationForest(contamination=0.05)
trained = False

def save_logs():
    with open("logs.txt", "w", encoding="utf-8") as f:
        f.write(keystrokes)
    with open("logs.json", "w", encoding="utf-8") as f:
        json.dump(keystrokes, f)

def train_model():
    global trained
    if len(key_times) > 30:
        intervals = np.diff(key_times)
        intervals = intervals[intervals > 0.04]
        if len(intervals) > 15:
            model.fit(intervals.reshape(-1, 1))
            trained = True

def detect_anomaly():
    global last_alert_time
    if trained and len(key_times) > 2:
        interval = key_times[-1] - key_times[-2]
        if interval < 0.03:
            result = model.predict([[interval]])
            if result[0] == -1:
                if time.time() - last_alert_time > 8:
                    anomaly_text.set("⚠ Suspicious Typing Detected!")
                    messagebox.showwarning(
                        "Security Alert",
                        "Non-human typing speed detected!\nPossible automated activity."
                    )
                    last_alert_time = time.time()

def update_speed():
    if len(key_times) > 5:
        recent = key_times[-5:]
        duration = recent[-1] - recent[0]
        if duration > 0:
            speed = round((len(recent) - 1) / duration, 2)
            speed_text.set(f"Typing Speed: {speed} keys/sec")

def on_press(key):
    global keystrokes
    if not running:
        return False

    now = time.time()
    key_times.append(now)

    key_char = str(key).replace("'", "")
    if key_char == "Key.space":
        key_char = " "
    elif key_char == "Key.enter":
        key_char = "\n"

    display_char = "●" if masked else key_char

    keystrokes += key_char
    live_box.insert(END, display_char)
    live_box.see(END)

    save_logs()
    update_speed()
    train_model()
    detect_anomaly()

def run_keylogger():
    global listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def start_keylogger():
    global running
    if not running:
        running = True
        status_text.set("Status: Running")
        threading.Thread(target=run_keylogger, daemon=True).start()

def stop_keylogger():
    global running, listener
    running = False
    status_text.set("Status: Stopped")
    if listener:
        listener.stop()

def toggle_mask():
    global masked
    masked = not masked

def show_graph():
    if len(key_times) < 3:
        messagebox.showinfo("Info", "Not enough data to plot graph")
        return
    intervals = np.diff(key_times)
    plt.figure()
    plt.plot(intervals, marker='o')
    plt.title("Keystroke Timing Pattern")
    plt.xlabel("Keystroke Count")
    plt.ylabel("Time Interval (seconds)")
    plt.grid(True)
    plt.show()

main = Frame(root, bg="white", bd=2, relief=RIDGE)
main.place(relx=0.5, rely=0.5, anchor=CENTER, width=820, height=480)

Label(
    main,
    text="AI-BASED KEYLOGGER DETECTION SYSTEM",
    font=("Verdana", 17, "bold"),
    bg="white",
    fg="#0d47a1"
).pack(pady=10)

Label(
    main,
    textvariable=status_text,
    font=("Verdana", 12, "bold"),
    bg="white"
).pack()

Label(
    main,
    textvariable=speed_text,
    font=("Verdana", 12, "bold"),
    fg="#2e7d32",
    bg="white"
).pack(pady=3)

Label(
    main,
    textvariable=anomaly_text,
    font=("Verdana", 11, "bold"),
    fg="red",
    bg="white"
).pack(pady=5)

Label(
    main,
    text="Live Keystroke Viewer",
    font=("Verdana", 12, "bold"),
    bg="white"
).pack(pady=5)

live_box = Text(main, height=6, width=85, font=("Consolas", 10))
live_box.pack(pady=5)

btn = Frame(main, bg="white")
btn.pack(pady=15)

Button(btn, text="START", width=14, bg="#1976d2", fg="white",
       font=("Verdana", 10, "bold"), command=start_keylogger).grid(row=0, column=0, padx=8)

Button(btn, text="STOP", width=14, bg="#d32f2f", fg="white",
       font=("Verdana", 10, "bold"), command=stop_keylogger).grid(row=0, column=1, padx=8)

Button(btn, text="MASK PASSWORD", width=16, bg="#6a1b9a", fg="white",
       font=("Verdana", 10, "bold"), command=toggle_mask).grid(row=0, column=2, padx=8)

Button(btn, text="SHOW GRAPH", width=14, bg="#00796b", fg="white",
       font=("Verdana", 10, "bold"), command=show_graph).grid(row=0, column=3, padx=8)

Label(
    root,
    text="Cyber Security Mini Project | Educational Use Only",
    font=("Verdana", 9),
    bg="#e3f2fd"
).pack(side=BOTTOM, pady=8)

root.mainloop()
