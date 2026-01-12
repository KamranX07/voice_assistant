from core.speaker import speak
from core.memory import remember, get_last_command, get_history
from core.system_control import (
    lock_pc, shutdown_pc, restart_pc, take_screenshot,
    get_battery_status, volume_up, volume_down, mute_volume,
    play_pause, next_track, previous_track,
    minimize_window, maximize_window
)
from core.navigation_engine import (
    resolve_open_target, open_path,
    find_running_apps, is_dangerous_app, close_target,
    delete_path_safe
)


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

        ratio = difflib.SequenceMatcher(None, word, text).ratio()
        if ratio > 0.6:
            return True
    return False


# ---------------- HANDLERS ----------------

def open_handler(path):
    open_path(path)
    speak("Opened.")


def close_handler(item):
    close_target(item)
    speak("Closed.")


def delete_handler(path):
    delete_path_safe(path)
    speak("Moved to recycle bin.")


# ---------------- ROUTER ----------------

def handle_command(command):
    if not command:
        return None

    remember(command)

    # ----------- TIME / DATE -----------

    if match(["time", "clock"], command):
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
        return None

    elif match(["date", "today"], command):
        today = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {today}")
        return None

    # ----------- APPS -----------

    elif match(["notepad", "notes"], command):
        speak("Opening Notepad")
        os.system("notepad")
        return None

    elif match(["calculator", "calc"], command):
        speak("Opening Calculator")
        os.system("calc")
        return None

    elif match(["youtube"], command):
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
        return None

    # ----------- MEMORY -----------

    elif match(["last command", "what did i say"], command):
        last = get_last_command()
        speak(f"You last said: {last}" if last else "I don't remember anything yet.")
        return None

    elif match(["history", "what have i said"], command):
        history = get_history()
        if history:
            for cmd in history:
                speak(cmd)
        else:
            speak("No history yet.")
        return None

    # ----------- SYSTEM -----------

    elif match(["lock"], command):
        speak("Locking your PC.")
        lock_pc()
        return None

    elif match(["shutdown", "turn off"], command):
        speak("Shutting down your PC.")
        shutdown_pc()
        return None

    elif match(["restart", "reboot"], command):
        speak("Restarting your PC.")
        restart_pc()
        return None

    elif match(["screenshot", "capture screen"], command):
        speak("Taking a screenshot.")
        msg = take_screenshot()
        speak(msg)
        return None

    elif match(["battery"], command):
        speak(get_battery_status())
        return None

    elif strict_match(["volume down", "decrease volume"], command):
        volume_down()
        speak("Volume decreased.")
        return None

    elif strict_match(["volume up", "increase volume"], command):
        volume_up()
        speak("Volume increased.")
        return None

    elif match(["mute"], command):
        mute_volume()
        speak("Muted.")
        return None

    elif match(["play", "pause"], command):
        play_pause()
        speak("Playback toggled.")
        return None

    elif match(["next"], command):
        next_track()
        speak("Next track.")
        return None

    elif match(["previous"], command):
        previous_track()
        speak("Previous track.")
        return None

    elif strict_match(["minimize", "minimise"], command):
        minimize_window()
        speak("Minimized.")
        return None

    elif strict_match(["maximize", "maximise"], command):
        maximize_window()
        speak("Maximized.")
        return None

    # ----------- GREETINGS -----------

    elif match(["hello", "hi", "hey"], command):
        speak("Hello! How can I help you?")
        return None

    elif match(["how are you"], command):
        speak("I'm doing great.")
        return None

    elif match(["who are you", "your name", "hu r u", "who r u", "who are u", "your name", "about you"], command):
        speak("I am Jarvis, your personal AI assistant.")
        return None

    elif match(["thank you", "thanks"], command):
        speak("You're welcome.")
        return None

    # ----------- OPEN -----------

    elif command.startswith(("open", "start", "launch", "run")):
        # Extract target safely
        target = None
        for word in ["open", "start", "launch", "run"]:
            if command.startswith(word):
                target = command[len(word):].strip()
                break

        if not target:
            speak("What should I open?")
            return None

        # 1️⃣ Try launching as APP first
        from core.smart_launcher import resolve_app, launch_app

        app_path = resolve_app(target)
        if app_path:
            if launch_app(app_path):
                speak(f"Opening {target}")
                return None

        # 2️⃣ Else try file/folder resolution
        result = resolve_open_target(target)

        if result["type"] == "none":
            speak("I couldn't find that.")
            return None

        if result["type"] == "single":
            open_path(result["path"])
            speak("Opening.")
            return None

        if result["type"] == "multiple":
            speak("I found multiple matches.")
            print("\nMatches:")
            for i, p in enumerate(result["matches"], 1):
                print(f"{i}) {os.path.basename(p)}")

            return {
                "type": "selection",
                "options": result["matches"],
                "handler": open_handler
            }


    # ----------- CLOSE -----------

    elif command.startswith("close"):
        target = command.replace("close", "").strip()

        matches = find_running_apps(target)

        if not matches:
            speak("I couldn't find any matching app or window.")
            return None

        if len(matches) == 1:
            item = matches[0]
            name = item["name"]

            if item["type"] == "process_group" and is_dangerous_app(name):
                return {
                    "type": "confirmation",
                    "data": item,
                    "message": f"Are you sure you want to close all instances of {name}?",
                    "handler": close_handler
                }

            close_target(item)
            speak(f"Closed {name}.")
            return None

        speak("I found multiple matches.")
        print("\nMatches:")
        for i, item in enumerate(matches, 1):
            print(f"{i}) {item['name']} ({item['type']})")

        return {
            "type": "selection",
            "options": matches,
            "handler": close_handler
        }


    # ----------- DELETE -----------

    elif command.startswith("delete"):
        target = command.replace("delete", "").strip()

        result = resolve_open_target(target)

        if result["type"] == "none":
            speak("I couldn't find anything to delete.")
            return None

        if result["type"] == "single":
            name = os.path.basename(result["path"])
            return {
                "type": "confirmation",
                "data": result["path"],
                "message": f"Are you sure you want to delete {name}?",
                "handler": delete_handler
            }

        speak("I found multiple items.")
        print("\nMatches:")
        for i, p in enumerate(result["matches"], 1):
            print(f"{i}) {os.path.basename(p)}")


        return {
            "type": "selection",
            "options": result["matches"],
            "handler": delete_handler
        }


    # ----------- FALLBACK -----------

    else:
        speak("I didn't understand that.")
        return None
