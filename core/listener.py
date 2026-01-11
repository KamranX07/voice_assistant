import socket
import time
import speech_recognition as sr

recognizer = sr.Recognizer()


def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False


def listen(timeout=5, phrase_time_limit=5):
    """Listen for any speech with timeout."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.WaitTimeoutError:
        return ""
    except:
        return ""


def listen_for_wake_word(wake_word="jarvis"):
    """Listens until wake word is detected."""
    print("🟡 Sleeping... Say 'Jarvis' to wake me.")

    while True:
        text = listen(timeout=4, phrase_time_limit=3)
        if not text:
            continue

        print("Heard:", text)

        if wake_word in text:
            print("🟢 Wake word detected")
            return True
