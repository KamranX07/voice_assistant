print("File Loaded")
import time
from core.listener import listen, listen_for_wake_word
from core.speaker import speak
from core.router import handle_command
from core.file_control import delete_path

pending_action = None
SESSION_TIMEOUT = 10

def main():
    global pending_action

    print("Jarvis core starting...")
    speak("Jarvis is online.")

    while True:
        # ---------------- SLEEP MODE ----------------
        listen_for_wake_word("jarvis")
        speak("Yes, I'm listening.")
        
        session_start = time.time()

        # ---------------- ACTIVE SESSION ----------------        
        while True:
            if time.time() - session_start > SESSION_TIMEOUT:
                speak("Going to sleep, wake me when you need me.")
                break

        # ---------------- COMMAND MODE ----------------
            command = listen(timeout=5, phrase_time_limit=6)
            print("Command heard:", command)

            if not command:
                continue

            session_start = time.time()

            if any(word in command for word in ["exit", "quit", "stop"]):
                speak("Goodbye!")
                return

        # ---------------- CONFIRMATION MODE ----------------
            if pending_action:
                if "yes" in command:
                    if pending_action["action"] == "confirm_delete":
                        msg = delete_path(pending_action["path"])
                        speak(msg)
                else:
                    speak("Action cancelled.")

                pending_action = None
                continue

        # ---------------- NORMAL COMMAND ----------------
            result = handle_command(command)

            if isinstance(result, dict):
                pending_action = result


if __name__ == "__main__":
    main()
