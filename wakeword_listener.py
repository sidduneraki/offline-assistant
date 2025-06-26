import json
import pyaudio
from vosk import Model, KaldiRecognizer

def listen_for_wake_word(callback):
    model = Model("models/vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("🎧 Listening for wake word 'jarvis'...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()
                print("Heard:", text)

                if "jarvis" in text:
                    print("🔊 Wake word 'jarvis' detected!")
                    callback()
    except KeyboardInterrupt:
        print("Wake word listener stopped.")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
