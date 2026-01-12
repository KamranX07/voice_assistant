import os
import subprocess
import winreg

APP_ALIASES = {
    "chrome": ["chrome", "google chrome", "browser"],
    "edge": ["edge", "microsoft edge"],
    "brave": ["brave"],
    "firefox": ["firefox"],
    "code": ["vs code", "visual studio code", "code"],
}

KNOWN_EXECUTABLES = {
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "brave": ["brave.exe"],
    "firefox": ["firefox.exe"],
    "code": ["code.exe"],
}

def normalize(text):
    return text.lower().strip()

def find_installed_apps():
    found = {}

    roots = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths",
    ]

    for root in roots:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root)
        except:
            continue

        for i in range(0, winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                value, _ = winreg.QueryValueEx(subkey, None)
                exe = os.path.basename(value).lower()
                found[exe] = value
            except:
                pass

    return found

INSTALLED_APPS = find_installed_apps()

def resolve_app(target):
    t = normalize(target)

    for app, aliases in APP_ALIASES.items():
        if any(a in t for a in aliases):
            exes = KNOWN_EXECUTABLES.get(app, [])
            for exe in exes:
                if exe in INSTALLED_APPS:
                    return INSTALLED_APPS[exe]

    return None

def launch_app(path):
    try:
        subprocess.Popen(path, shell=True)
        return True
    except:
        return False