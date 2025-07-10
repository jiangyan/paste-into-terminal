
import os
import sys
import time
import ctypes
from datetime import datetime
from PIL import Image, ImageGrab
from pynput import keyboard
import pystray
import threading
import pyperclip
import tkinter
from tkinter import filedialog

# --- Admin Rights Helper ---

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# --- Core Application Logic ---

# Define the default directory
DEFAULT_DIR = os.path.join(os.environ["TEMP"], "fileforterminal")
# Use a global variable for the target directory
screenshot_folder = DEFAULT_DIR

# Create the temporary directory if it doesn't exist
os.makedirs(screenshot_folder, exist_ok=True)

# Event to signal the main thread to open the folder dialog
select_folder_event = threading.Event()

# --- Core Functions ---

def select_folder():
    """
    Opens a dialog to select a new folder for saving screenshots.
    MUST BE RUN IN THE MAIN THREAD.
    """
    global screenshot_folder
    # Hide the root tkinter window
    root = tkinter.Tk()
    root.withdraw()
    # Bring the dialog to the front
    root.attributes("-topmost", True)
    new_folder = filedialog.askdirectory(
        parent=root,
        initialdir=screenshot_folder,
        title="Select a folder to store screenshots"
    )
    root.destroy()
    if new_folder:
        screenshot_folder = new_folder
        # We can create it here to be safe
        os.makedirs(screenshot_folder, exist_ok=True)


def do_paste_work():
    """
    This function performs the actual work of saving the image and pasting the path.
    It is designed to be run in a separate thread to avoid blocking the hotkey listener.
    """
    # A crucial delay to ensure the hotkey keys (Ctrl, Alt, V) have been released
    # before we try to simulate new key presses.
    time.sleep(0.2)

    try:
        # Ensure the directory exists, in case it was deleted
        os.makedirs(screenshot_folder, exist_ok=True)
        # Get image from clipboard
        img = ImageGrab.grabclipboard()

        if isinstance(img, Image.Image):
            # Generate a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
            filepath = os.path.join(screenshot_folder, filename)

            # Save the image
            img.save(filepath, "PNG")

            # Copy the file path to the clipboard
            pyperclip.copy(filepath)
            time.sleep(0.1)  # Give the clipboard a moment to update

            # Simulate a Ctrl+V paste
            keyboard_controller = keyboard.Controller()
            keyboard_controller.press(keyboard.Key.ctrl)
            keyboard_controller.press('v')
            keyboard_controller.release('v')
            keyboard_controller.release(keyboard.Key.ctrl)

    except Exception as e:
        # Silently ignore any errors
        pass

# --- Hotkey Setup ---

def on_hotkey_press():
    """
    This function is called directly by the hotkey listener.
    Its only job is to start a new thread to do the actual work. This is critical
    to prevent the listener from blocking and interfering with the paste action.
    """
    threading.Thread(target=do_paste_work).start()

def start_hotkey_listener():
    # Define the hotkey combination
    # Using Ctrl+Alt+V for pasting
    hotkey_str = '<ctrl>+<alt>+v'

    # Start listening for the hotkey
    with keyboard.GlobalHotKeys({
        hotkey_str: on_hotkey_press
    }) as h:
        h.join()


# --- System Tray Application ---

def on_select_folder_clicked(icon, item):
    """Callback for the 'File Path' menu item."""
    select_folder_event.set()

def exit_action(icon, item):
    """Callback for the 'Exit' menu item."""
    icon.stop()

def setup_tray_icon():
    """Sets up and runs the system tray icon."""
    # Load a placeholder icon
    width = 64
    height = 64
    color1 = (0, 0, 0)
    color2 = (255, 255, 255)
    image = Image.new('RGB', (width, height), color1)

    # Create a simple icon
    import PIL.ImageDraw
    dc = PIL.ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    # Setup the tray icon and menu
    icon = pystray.Icon(
        "paste_image_helper",
        image,
        "Paste Image Helper",
        menu=pystray.Menu(
            pystray.MenuItem("File Path", on_select_folder_clicked),
            pystray.MenuItem("Exit", exit_action)
        )
    )
    icon.run()


# --- Main Execution ---

if __name__ == "__main__":
    if is_admin():
        # Start the hotkey listener in a daemon thread
        listener_thread = threading.Thread(target=start_hotkey_listener, daemon=True)
        listener_thread.start()

        # Start the system tray icon in a daemon thread
        icon_thread = threading.Thread(target=setup_tray_icon, daemon=True)
        icon_thread.start()

        # Main thread loop to handle GUI events
        while icon_thread.is_alive():
            # Wait for the event to be set, with a timeout
            event_is_set = select_folder_event.wait(timeout=0.1)
            if event_is_set:
                select_folder()
                select_folder_event.clear()  # Reset the event
    else:
        # If not admin, re-run the script with admin rights
        run_as_admin()
