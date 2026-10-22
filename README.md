# Streakly Planner

Streakly Planner is a simple desktop app for organising your day, keeping track of tasks, and building a consistent routine. Your plans stay on your computer, so you can use it without creating an account.

## What you can do

- Browse the monthly calendar and select any date.
- Plan your day with timed tasks.
- Add, edit, complete, and delete tasks.
- Keep notes for each day.
- Track your completion streak.
- Switch the interface between English, Kiswahili, French, and Spanish.
- Scroll the planner panels with a mouse wheel, touchpad, or supported keyboard keys.

## What you need

- Windows 10 or Windows 11.
- Python 3.10 or newer, installed from [python.org](https://www.python.org/downloads/). Make sure the Tcl/Tk feature is included during installation.
- No extra Python packages are needed.

## Getting started

1. Download the project ZIP and extract it to a folder where you want to keep it.
2. If Python is not installed, install it from the link above.
3. Double-click `setup.bat` to create a **Streakly Planner** shortcut on your desktop.
4. Open the app from that shortcut. You can also use `launch_streakly.bat` to start it directly.

## Your data and privacy

Your tasks and notes are saved locally on your computer here:

`%LOCALAPPDATA%\Streakly Planner\planner_data.json`

The project ZIP does not contain personal planner entries. Streakly Planner does not need an account and does not send your planner data over the internet. To keep a backup, copy `planner_data.json` somewhere safe. If you delete that file, your saved plans will be deleted too.

## Scrolling tips

- **Mouse wheel or touchpad:** move the pointer over the panel you want to scroll.
- **Keyboard:** with the pointer over a panel, use the Up/Down arrows or Page Up/Page Down.
- Inside a text field, the keys continue to work as normal text-editing keys.

## Files in this project

- `streakly.py` — the application.
- `streakly.ico` — app and desktop shortcut icon.
- `setup.bat` — creates the desktop shortcut.
- `launch_streakly.bat` — starts the app directly.
- `LICENSE` — MIT license.

## Check the Python file

From this folder, run:

```powershell
py -3 -m py_compile streakly.py
```

## License

Streakly Planner is released under the MIT License. See [LICENSE](LICENSE).
