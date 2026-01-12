import os
import time
import difflib
import psutil
from send2trash import send2trash


DANGEROUS_APPS = [
    "chrome", "msedge", "firefox", "brave",
    "code", "pycharm", "idea",
    "notepad++", "word", "excel", "powerpnt",
    "photoshop", "premiere"
]

APP_ALIASES = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ],
    "brave": [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    ],
    "edge": [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ],
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "visual studio": "code",
    "code editor": "code",
    "notepad": "notepad",
    "calculator": "calc"
}

# Known user folders
UP = os.environ["USERPROFILE"]

KNOWN_FOLDERS = {
    "desktop": os.path.join(UP, "Desktop"),
    "downloads": os.path.join(UP, "Downloads"),
    "documents": os.path.join(UP, "Documents"),
    "pictures": os.path.join(UP, "Pictures"),
    "music": os.path.join(UP, "Music"),
    "videos": os.path.join(UP, "Videos"),
    "onedrive desktop": os.path.join(UP, "OneDrive", "Desktop"),
    "onedrive documents": os.path.join(UP, "OneDrive", "Documents"),
}

# Add local app data for more search reach
SEARCH_DIRS = []
for folder in KNOWN_FOLDERS.values():
    if os.path.exists(folder):
        SEARCH_DIRS.append(folder)

# ------------------ Utilities ------------------

def similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def open_path(path):
    try:
        os.startfile(path)
        return True
    except:
        return False

def resolve_open_target(name, timeout=2):
    name = name.lower().strip()

    # 1️⃣ Exact known folder
    if name in KNOWN_FOLDERS:
        return {"type": "single", "path": KNOWN_FOLDERS[name]}

    matches = []
    seen_paths = set()
    start_time = time.time()

    # 2️⃣ Fast top-level scan
    for base in SEARCH_DIRS:
        try:
            for item in os.listdir(base):
                if name in item.lower():
                    full_path = os.path.join(base, item)
                    if full_path not in seen_paths:
                        matches.append(full_path)
                        seen_paths.add(full_path)
        except:
            pass

    # 3️⃣ Limited deep scan (timeout protected)
    for base in SEARCH_DIRS:
        for root, dirs, files in os.walk(base):
            if time.time() - start_time > timeout:
                break

            for item in dirs + files:
                if name in item.lower():
                    full_path = os.path.join(root, item)
                    if full_path not in seen_paths:
                        matches.append(full_path)
                        seen_paths.add(full_path)

            if len(matches) > 25:
                break

    if not matches:
        return {"type": "none"}

    if len(matches) == 1:
        return {"type": "single", "path": matches[0]}

    return {"type": "multiple", "matches": matches}


def find_running_apps(name):
    name = name.lower()

    # Normalize aliases
    for alias, val in APP_ALIASES.items():
        if alias in name:
            if isinstance(val, list):
                # get exe name from path
                name = os.path.basename(val[0]).replace(".exe", "").lower()
            else:
                name = val.lower()
            break

    matches = []

    # 1. Check processes - Group by name
    proc_groups = {}  # name -> list of process objects
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name']
            pname_lower = pname.lower()
            if name in pname_lower or similarity(name, pname_lower.replace(".exe", "")) > 0.8:
                if pname not in proc_groups:
                    proc_groups[pname] = []
                proc_groups[pname].append(proc)
        except:
            pass

    for pname, procs in proc_groups.items():
        matches.append({"type": "process_group", "objs": procs, "name": pname})
            
    # 2. Check windows (from pygetwindow)
    import pygetwindow as gw
    for win in gw.getAllWindows():
        if win.title and name in win.title.lower():
            # Check if we should add this window
            # If it's a browser, sometimes the title is specific but it's part of a process group
            matches.append({"type": "window", "obj": win, "name": win.title})

    return matches


def is_dangerous_app(app_name):
    return any(d in app_name.lower() for d in DANGEROUS_APPS)


def close_target(item):
    try:
        if item["type"] == "process_group":
            for p in item["objs"]:
                try:
                    p.terminate()
                except:
                    pass
        elif item["type"] == "window":
            item["obj"].close()
        return True
    except:
        return False

def delete_path_safe(path):
    try:
        send2trash(path)
        return True
    except:
        return False