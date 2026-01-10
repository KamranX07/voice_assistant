import queue
import sounddevice as sd
import socket
import json
import vosk

vosk.SetLogLevel(-1)
model = vosk.Model("models/vosk-model-small-en-us-0.15")
q = queue.Queue()

def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def listen():
    if is_connected():
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening(online)...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)
    
        try:
            text = r.recognize_google(audio)
            print("Online:", text)
            return text.lower()
        except:
            return ""
    else:
        print("Listening (offline)...")
        rec = vosk.KaldiRecognizer(model, 16000)

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=callback):
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result= json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print("Offline:", text)
                        return text.lower()