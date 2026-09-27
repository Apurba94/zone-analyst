@echo off
setlocal
title Zone Analyst - local website
cd /d "%~dp0website"

rem Prefer the Python launcher, then python. On Windows "python" can be a
rem Microsoft Store placeholder that opens the Store instead of running,
rem so each candidate is tested before it is used.
set "PY="
py -3 --version >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if defined PY goto havepython
python --version >nul 2>nul
if not errorlevel 1 set "PY=python"
if not defined PY goto nopython

:havepython

echo.
echo   Zone Analyst is running at   http://localhost:8000
echo   Your browser opens in a moment. Close this window to stop the server.
echo.
rem Open the browser after a short pause, once the server is listening.
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start "" http://localhost:8000/index.html"
%PY% -m http.server 8000 --bind 127.0.0.1
echo.
echo   The server stopped. If it said the port is in use, close the other
echo   window that is already running it, or restart your computer.
pause
goto :eof

:nopython
echo.
echo   Python is not installed, so the site will open straight from disk.
echo   Everything works that way too.
echo.
echo   For a local server later, install Python from https://www.python.org/downloads/
echo   and tick "Add python.exe to PATH" during setup.
echo.
start "" "%~dp0website\index.html"
pause
