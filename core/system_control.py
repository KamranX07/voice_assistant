import os
import pyautogui
import psutil
import win32gui, win32con

def lock_pc():
    os.system("rundll32.exe user32.dll,LockWorkStation")

def shutdown_pc():
    os.system("shutdown /s /t 1")

def restart_pc():
    os.system("shutdown /r /t 1")

def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    return "Screenshot taken"

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"Battery is at {battery.percent} percent"
    return "Battery information not available"

def volume_up():
    for _ in range(5):
        pyautogui.press("volumeup")

def volume_down():
    for _ in range(5):
        pyautogui.press("volumedown")

def mute_volume():
    pyautogui.press("volumemute")

def play_pause():
    pyautogui.press("playpause")

def next_track():
    pyautogui.press("nexttrack")

def previous_track():
    pyautogui.press("prevtrack")

def get_active_window():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd if hwnd else None    
def minimize_window():
    try:
        hwnd = get_active_window()
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True
    except:
        return False


def maximize_window():
    try:
        hwnd = get_active_window()

        # If minimized → restore first
        placement = win32gui.GetWindowPlacement(hwnd)
        show_cmd = placement[1]

        if show_cmd == win32con.SW_SHOWMINIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        return True
    except:
        return False