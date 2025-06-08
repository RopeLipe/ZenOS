@echo off
echo Starting GTK4 System Installer...
echo.
echo Note: This requires GTK4 and PyGObject to be installed.
echo For Windows, you can install via MSYS2:
echo   pacman -S mingw-w64-x86_64-gtk4 mingw-w64-x86_64-python-gobject
echo.
python main.py
pause
