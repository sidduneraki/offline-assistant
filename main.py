import tkinter as tk
import threading
import jarvis
import wakeword_listener

jarvis_thread = None
is_running = False

def toggle_jarvis():
    global jarvis_thread, is_running

    if not is_running:
        status_label.config(text="Status: ON", fg="green")
        jarvis_thread = threading.Thread(target=wakeword_listener.listen_for_wake_word, args=(jarvis.run_assistant,))
        jarvis_thread.daemon = True
        jarvis_thread.start()
        is_running = True
    else:
        status_label.config(text="Status: OFF", fg="red")
        jarvis.stop_assistant()
        is_running = False

# GUI setup
root = tk.Tk()
root.title("JARVIS Control")
root.geometry("200x120")

toggle_btn = tk.Button(root, text="Toggle JARVIS", command=toggle_jarvis, font=("Arial", 12))
toggle_btn.pack(pady=10)

status_label = tk.Label(root, text="Status: OFF", fg="red", font=("Arial", 10))
status_label.pack()

root.mainloop()
