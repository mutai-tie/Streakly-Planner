@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 was not found. Install Python from https://www.python.org/downloads/
  echo Select "Add Python to PATH" during installation, then run this installer again.
  pause
  exit /b 1
)
set "APP=%~dp0streakly.py"
set "ICON=%~dp0streakly.ico"
set "SHORTCUT=%USERPROFILE%\Desktop\Streakly Planner.lnk"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('%SHORTCUT%'); $s.TargetPath=(py -3 -c \"import sys; print(sys.executable.replace('python.exe','pythonw.exe'))\"); $s.Arguments='\"%APP%\"'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICON%'; $s.Description='Streakly Planner offline daily planner'; $s.Save()"
if errorlevel 1 (
  echo Shortcut creation failed. You can still double-click launch_streakly.bat.
  pause
  exit /b 1
)
echo.
echo Done! Streakly Planner is now on your Desktop.
echo It runs offline and does not open a command window.
pause
