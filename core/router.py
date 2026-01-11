from core.speaker import speak
from core.memory import remember, get_last_command, get_history
from core.system_control import lock_pc, shutdown_pc, restart_pc, take_screenshot, get_battery_status, volume_up, volume_down, mute_volume, play_pause, next_track, previous_track, minimize_window, maximize_window
from core.file_control import delete_path
from core.listener import listen
import datetime
import os
import webbrowser
import difflib

def strict_match(words, text):
    return any(word in text for word in words)

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

    remember(command)
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

    elif match(["last command", "what did i say"], command):
        last = get_last_command()
        if last:
            speak(f"You last said: {last}")
        else:
            speak("I don't remember any real commands yet.")

    elif match(["history", "what have i said"], command):
        history = get_history()
        if history:
            speak("Here are your last commands.")
            for cmd in history:
                speak(cmd)
        else:
            speak("No history yet.")

    elif match(["lock", "lock pc", "lock my pc"], command):
        speak(["Locking your PC."])
        lock_pc()

    elif match(["shutdown", "turn off"], command):
        speak(["Shutting down your PC."])
        shutdown_pc()

    elif match(["restart", "reboot"], command):
        speak(["Restarting your PC."])
        restart_pc()

    elif match(["screenshot", "take screenshot", "capture screen"], command):
        speak(["Taking a screenshot."])
        msg = take_screenshot()
        speak(msg)

    elif match(["battery", "battery status", "power"], command):
        status = get_battery_status()
        speak(status)

    elif strict_match(["volume down", "decrease volume", "lower"], command):
        speak("Decreasing volume.")
        volume_down()

    elif strict_match(["volume up", "increase volume", "louder"], command):
        speak("Increasing volume.")
        volume_up()

    elif match(["mute", "mute volume"], command):
        speak("Muting volume.")
        mute_volume()

    elif match(["play", "pause"], command):
        speak("Toggling playback.")
        play_pause()

    elif match(["next", "next song"], command):
        speak("Next track.")
        next_track()

    elif match(["previous", "previous song"], command):
        speak("Previous volume.")
        previous_track()

    elif strict_match(["minimize", "minimise", "minimize window"], command):
        speak("Minimizing window.")
        minimize_window()

    elif strict_match(["maximize", "maximise", "maximize window"], command):
        speak("Maximizing window.")
        maximize_window()

    elif match(["hello", "hi", "hey"], command):
        speak("Hello! How can I help you?")

    elif match(["how are you"], command):
        speak("I'm doing great. Ready to help you.")

    elif match(["who are you", "who r you", "who r u", "hu r u", "your name", "about you"], command):
        speak("I am Jarvis, your personal AI assistant.")

    elif match(["thank you", "thanks"], command):
        speak("You're welcome. Always here for you.")

    else:
        speak("I didn't understand that.")