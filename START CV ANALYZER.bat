@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0CV Analyzer.exe" (
    start "" "%~dp0CV Analyzer.exe"
    exit /b 0
)

set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo ERROR: The project virtual environment was not found:
    echo   %PYTHON%
    echo.
    echo Set up the project environment before starting the analyzer.
    pause
    exit /b 1
)

if not exist "%~dp0app\cv_analyzer_gui.py" (
    echo ERROR: The analyzer script was not found:
    echo   %~dp0app\cv_analyzer_gui.py
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0app\cv_analyzer_gui.py"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" echo Analyzer exited with code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
