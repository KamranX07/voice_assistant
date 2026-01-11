memory = {
    "last_command": None,
    "history": []
}

IGNORE_COMMANDS = [
    "what did i say",
    "last command",
    "show history",
    "what have i said",
]

def should_ignore(command):
    return any(phrase in command for phrase in IGNORE_COMMANDS)

def remember(command):
    if should_ignore(command):
        return

    memory["last_command"] = command
    memory["history"].append(command)

def get_last_command():
    return memory["last_command"] 

def get_history():
    return memory["history"][-5:]