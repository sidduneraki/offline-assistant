import os
import json
import pyttsx3
import requests
import difflib
import glob
import tkinter as tk
import insightface
import cv2
import numpy as np
from vosk import Model, KaldiRecognizer
import pyaudio

MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")
PASS_PHRASE = "open offline ai"
KNOWN_FACE_PATH = "known_face.jpg"

# Text-to-speech

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Query LLM

def query_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
        )
        return response.json()["response"].strip().lower()
    except Exception as e:
        print("Error communicating with Ollama:", e)
        return "unknown"

# Installed app shortcuts

def get_installed_app_shortcuts():
    paths = [
        r"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs",
        os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs")
    ]
    shortcuts = {}
    for path in paths:
        for file in glob.glob(path + "/**/*.lnk", recursive=True):
            name = os.path.splitext(os.path.basename(file))[0].lower()
            shortcuts[name] = file
    return shortcuts

installed_apps = get_installed_app_shortcuts()

# Extract app name using few-shot prompt

def extract_app_name(text):
    prompt = f"""
You are a voice assistant. The user said: "{text}"

If the user is trying to open or launch an app, extract only the app name.
Examples:
- "open chrome" -> chrome
- "can you launch zoom" -> zoom
- "start my music" -> spotify
- "i want to browse" -> chrome
- "watch a video" -> vlc
- "start notepad" -> notepad
- "launch vs code" -> code
If they are not trying to open an app, reply with "none".
Return only the app name (lowercase).
"""
    app_name = query_ollama(prompt)
    print("LLM extracted app name:", app_name)
    return app_name

# Try launching app

def try_open_app_from_text(text):
    app_name = extract_app_name(text)
    if app_name != "none":
        best_match = difflib.get_close_matches(app_name, installed_apps.keys(), n=1, cutoff=0.6)
        if best_match:
            app_key = best_match[0]
            confidence = difflib.SequenceMatcher(None, app_name, app_key).ratio()
            if confidence < 0.7:
                speak(f"I think you meant {app_key}, opening it.")
            else:
                speak(f"Opening {app_key}")
            os.startfile(installed_apps[app_key])
            return True
        else:
            speak("Sorry, I couldn't find that app.")
            return True
    return False

# Face recognition login using InsightFace

def verify_face():
    if not os.path.exists(KNOWN_FACE_PATH):
        print("No known face image found.")
        return True

    model = insightface.app.FaceAnalysis(name="buffalo_l")
    model.prepare(ctx_id=0)

    known_img = cv2.imread(KNOWN_FACE_PATH)
    known_face = model.get(known_img)
    if not known_face:
        print("❌ No face found in known image.")
        return False

    known_embedding = known_face[0].embedding

    cap = cv2.VideoCapture(0)
    speak("Scanning your face")
    ret, frame = cap.read()
    cap.release()

    user_face = model.get(frame)
    if not user_face:
        print("❌ No face found in webcam")
        return False

    user_embedding = user_face[0].embedding

    cos_sim = np.dot(known_embedding, user_embedding) / (np.linalg.norm(known_embedding) * np.linalg.norm(user_embedding))
    print("Similarity:", cos_sim)
    return cos_sim > 0.3

# GUI log viewer

def show_log_viewer():
    log_window = tk.Tk()
    log_window.title("JARVIS Log Viewer")
    log_window.geometry("500x400")

    text_area = tk.Text(log_window, wrap=tk.WORD, font=("Consolas", 10))
    text_area.pack(expand=True, fill=tk.BOTH)

    if os.path.exists("jarvis_log.txt"):
        with open("jarvis_log.txt", "r") as f:
            text_area.insert(tk.END, f.read())
    else:
        text_area.insert(tk.END, "Log file not found.")

    log_window.mainloop()

# Assistant loop

def run_assistant():
    global running
    running = False

    model = Model("models/vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    speak("Say your passphrase to unlock")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            print("Passphrase heard:", text)

            if PASS_PHRASE in text:
                if verify_face():
                    speak("Access granted")
                    running = True
                    break
                else:
                    speak("Face not recognized. Access denied.")

    speak("Assistant is now listening")
    while running:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            print("Heard:", text)

            if not text.strip():
                continue

            if "show my logs" in text:
                speak("Opening your logs.")
                show_log_viewer()
                continue

            if try_open_app_from_text(text):
                with open("jarvis_log.txt", "a") as log:
                    log.write(f"Heard: {text} → App launch attempt\n")
                continue

            speak("Let me think...")
            reply = query_ollama(text)[:400]
            print("Chatbot:", reply)
            speak(reply)

            with open("jarvis_log.txt", "a") as log:
                log.write(f"Heard: {text} → Chatbot: {reply}\n")

    stream.stop_stream()
    stream.close()
    mic.terminate()
    print("Assistant stopped listening")


def stop_assistant():
    global running
    running = False
