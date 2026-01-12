import time
from enum import Enum

from core.listener import listen, listen_for_wake_word
from core.speaker import speak
from core.router import handle_command

# ---------------- CONFIG ----------------
WAKE_WORD = "jarvis"
SESSION_TIMEOUT = 10
PENDING_TIMEOUT = 20

# ---------------- STATES ----------------
class State(Enum):
    SLEEPING = 1
    ACTIVE = 2
    WAITING_FOR_SELECTION = 3
    WAITING_FOR_CONFIRMATION = 4

# ---------------- GLOBALS ----------------
state = State.SLEEPING
pending_action = None
last_active_time = None


# ---------------- HELPERS ----------------
def reset_pending():
    global pending_action
    pending_action = None


def set_pending(data):
    global pending_action
    data["timestamp"] = time.time()
    pending_action = data


def pending_expired():
    if not pending_action:
        return False
    return time.time() - pending_action["timestamp"] > PENDING_TIMEOUT


def session_expired():
    if not last_active_time:
        return False
    return state == State.ACTIVE and time.time() - last_active_time > SESSION_TIMEOUT


def is_yes(text):
    return any(word in text for word in ["yes", "yeah", "yup", "sure"])


def is_no(text):
    return any(word in text for word in ["no", "nope", "cancel"])


def extract_number(text):
    text = text.lower()

    numbers = {
        "one": 1, "first": 1, "1": 1,
        "two": 2, "second": 2, "2": 2,
        "three": 3, "third": 3, "3": 3,
        "four": 4, "fourth": 4, "4": 4,
        "five": 5, "fifth": 5, "5": 5,
        "six": 6, "sixth": 6, "6": 6,
        "seven": 7, "seventh": 7, "7": 7,
        "eight": 8, "eighth": 8, "8": 8,
        "nine": 9, "ninth": 9, "9": 9,
        "ten": 10, "tenth": 10, "10": 10
    }
    for word, num in numbers.items():
        if word in text:
            return num
        
    for char in text:
        if char.isdigit():
            return int(char)
    return None


# ---------------- CORE LOOP ----------------
def main():
    global state, last_active_time

    print("Jarvis core booting...")
    speak("Jarvis is online.")

    while True:

        # ---------- TIMEOUTS ----------
        if pending_action and pending_expired():
            speak("Timed out. Cancelling the request.")
            reset_pending()
            state = State.ACTIVE

        if state == State.ACTIVE and session_expired():
            speak("Going to sleep, wake me when you need me.")
            state = State.SLEEPING
            continue

        # ---------- SLEEP MODE ----------
        if state == State.SLEEPING:
            listen_for_wake_word(WAKE_WORD)
            speak("Yes, I'm listening.")
            state = State.ACTIVE
            last_active_time = time.time()
            continue

        # ---------- LISTEN ----------
        if state in [State.WAITING_FOR_SELECTION, State.WAITING_FOR_CONFIRMATION]:
            command = listen(timeout=5, phrase_time_limit=6, allow_timeout=False)
        else:
            command = listen()    
            
        if not command:
            continue

        print("Heard:", command)
        last_active_time = time.time()

        # ---------- EXIT ----------
        if any(word in command for word in ["exit", "quit", "stop"]):
            speak("Goodbye Sir.")
            break

        # ---------- WAITING FOR SELECTION ----------
        if state == State.WAITING_FOR_SELECTION and pending_action:
            last_active_time = time.time()

            if time.time() - pending_action["timestamp"] > PENDING_TIMEOUT:
                speak("Timed out.")
                reset_pending()
                state = State.ACTIVE
                continue


            if any(word in command for word in ["cancel", "no", "stop"]):
                speak("Cancelled.")
                reset_pending()
                state = State.ACTIVE
                continue

            num = extract_number(command)
            if not num:
                speak("Tell me the number.")
                continue

            index = num - 1
            options = pending_action["options"]

            if index < 0 or index >= len(options):
                speak("Invalid choice.")
                continue

            chosen = options[index]

            handler = pending_action["handler"]
            reset_pending()
            state = State.ACTIVE

            last_active_time = time.time()
            handler(chosen)
            continue


        # ---------- WAITING FOR CONFIRMATION ----------
        if state == State.WAITING_FOR_CONFIRMATION and pending_action:
            last_active_time = time.time()

            if time.time() - pending_action["timestamp"] > PENDING_TIMEOUT:
                speak("Timed out.")
                reset_pending()
                state = State.ACTIVE
                continue


            if any(word in command for word in ["yes", "confirm", "do it", "sure"]):
                handler = pending_action["handler"]
                handler(pending_action["data"])
                speak("Done.")
                reset_pending()
                state = State.ACTIVE
                last_active_time = time.time()
                continue

            if any(word in command for word in ["no", "cancel", "stop"]):
                speak("Cancelled.")
                reset_pending()
                state = State.ACTIVE
                last_active_time = time.time()
                continue

            speak("Please say yes or no.")
            continue

        # ---------- NORMAL COMMAND ----------
        result = handle_command(command)

        if result is None:
            continue

        if isinstance(result, dict) and "type" in result:

            if result["type"] == "selection":
                set_pending({
                    "type": "selection",
                    "options": result["options"],
                    "handler": result["handler"]
                })
                speak("Tell me the number.")
                state = State.WAITING_FOR_SELECTION
                continue

            if result["type"] == "confirmation":
                set_pending({
                    "type": "confirmation",
                    "data": result["data"],
                    "handler": result["handler"]
                })
                speak(result["message"])
                state = State.WAITING_FOR_CONFIRMATION
                continue

        # Handle simple string responses or log unrecognized result types
        elif isinstance(result, str):
            speak(result)


if __name__ == "__main__":
    main()