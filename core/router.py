from core.speaker import speak
import datetime
import os
import webbrowser
import difflib

def match(words, text):
    for word in words:
        if word in text:
            return True
        
        ratio = difflib.SequenceMatcher(None, word, text). ratio()
        if ratio > 0.6:
            return True
    return False

def handle_command(command):
    if not command:
        return

    if match(["time", "clock"], command):
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")

    elif match(["date", "today"], command):
        today = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {today}")

    elif match(["notepad", "notes"], command):
        speak("Opening Notepad")
        os.system("notepad")

    elif match(["calculator", "calc"], command):
        speak("Opening Calculator")
        os.system("calc")

    elif match(["youtube", "video"], command):
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif match(["hello", "hi", "hey"], command):
        speak("Hello! How can I help you?")

    else:
        speak("I didn't understand that.")