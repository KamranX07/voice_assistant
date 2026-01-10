from core.listener import listen
from core.speaker import speak
from core.router import handle_command

def main():
    speak("Jarvis is now online. How can I help you?")

    while True:
        command = listen()

        if command == "internet_error":
            speak("You are offline. I will use offline mode.")
            continue

        elif "exit" in command or "quit" in command or "stop" in command:
            speak("Goodbye!")
            break

        else:
            handle_command(command)

if __name__=="__main__":
    main()