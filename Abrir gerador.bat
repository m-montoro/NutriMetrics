@echo off
cd /d "%~dp0"
python -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
    python simulador\interface_gerador.py
    if errorlevel 1 pause
    exit /b
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" simulador\interface_gerador.py
    if errorlevel 1 pause
    exit /b
)
echo Instale o Python com Tkinter e adicione-o ao PATH.
pause
