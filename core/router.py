from core.speaker import speak
import datetime
import os
import webbrowser

def handle_command(command):
    if not command:
        return
    
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")

    elif "date" in command:
        today = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {today}")

    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")

    elif "open calculator" in command:
        speak("Opening Calculator")
        os.system("calc")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif "hello" in command or "hi" in command:
        speak("Hello! How can I help you")

    else:
        speak("I didn't understand that.")