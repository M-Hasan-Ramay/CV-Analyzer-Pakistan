@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
    echo ERROR: The project virtual environment was not found:
    echo   %PYTHON%
    pause
    exit /b 1
)

"%PYTHON%" -m pip install -r "%~dp0requirements-build.txt"
if errorlevel 1 (
    echo ERROR: Could not install the portable-build requirements.
    pause
    exit /b 1
)

"%PYTHON%" "%~dp0build_portable.py"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" echo Portable build failed with code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
