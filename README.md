# Paste Image Helper

A simple Windows utility to quickly save an image from your clipboard to a file and paste the file path into your active window.

## Features

- **Clipboard Image Saving**: Captures the image currently in your clipboard.
- **File Path Pasting**: Saves the image as a `.png` file and automatically pastes the full file path.
- **Customizable Save Location**: Use the system tray icon to select a folder where your images will be saved.
- **System Tray Icon**: The application runs in the system tray for easy access.
- **Configurable Hotkey**: The default hotkey is `Ctrl+Alt+V`.

## Requirements

- Windows operating system
- Python 3
- The following Python packages:
  - `Pillow`
  - `pynput`
  - `pystray`
  - `pyperclip`

## Installation

1. **Clone the repository or download the `main.py` script.**

2. **Install the required packages:**
   ```bash
   pip install Pillow pynput pystray pyperclip
   ```

## Usage

1. **Run the script:**
   ```bash
   python main.py
   ```
   The script will request administrator privileges to install a global hotkey listener.

2. **Using the Hotkey:**
   - Copy any image to your clipboard.
   - Press `Ctrl+Alt+V`.
   - The image will be saved to your chosen folder, and the file path will be pasted into the active window.

3. **Changing the Save Folder:**
   - Right-click the application icon in your system tray.
   - Select "File Path" to open a folder selection dialog.
   - Choose a new folder where your screenshots will be saved.

4. **Exiting the Application:**
   - Right-click the application icon in your system tray.
   - Select "Exit".
