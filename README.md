# 🧠 JARVIS: Offline Voice-Controlled AI Assistant with Face Authentication

**JARVIS** is a Python-based offline AI assistant that combines speech recognition, face verification, local app control, and LLM responses — all running without internet.

---

## 🔑 Features

- 🎙️ Wake word detection ("Jarvis") using VOSK
- 🧔 Face authentication using InsightFace
- 🧠 Offline voice recognition (VOSK + PyAudio)
- 🧠 Local chatbot replies via Ollama (Mistral, LLaMA, etc.)
- 🖥️ GUI to control assistant (Tkinter)
- 💻 Smart app launcher with LLM understanding
- 📝 Logging of commands and chatbot replies

---

## 🗂️ Folder Structure

```bash
jarvis-assistant/
├── main.py                 # GUI control panel
├── jarvis.py               # Main assistant logic
├── wakeword_listener.py    # Listens for "Jarvis"
├── run.bat                 # Optional Windows startup script
├── known_face.jpg          # Image used for face authentication
├── models/                 # VOSK voice model folder (not uploaded to GitHub)
├── requirements.txt        # Python dependencies
├── README.md               # This file


## 🛡 License
This project is licensed under the MIT License.  
You are free to use, modify, and share this project — just give credit.  
See [LICENSE](LICENSE) for more details.
