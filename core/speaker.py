import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()
    engine.stop()