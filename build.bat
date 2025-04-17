@echo off
:: Batch script to build PIGAS

cd /d "%~dp0"

set BUILD_DIRECTORY=pigas
set VENV_ACTIVATE=.venv\Scripts\activate
set PIGAS_PYTHON=pigas.py

:: Check if Python script exists
if not exist "%PIGAS_PYTHON%" (
    echo Python script not found: %PIGAS_PYTHON%
    pause
    exit /b 1
)

:: Check if venv exists
if not exist "%VENV_ACTIVATE%" (
    echo Virtual environment not found at: %VENV_ACTIVATE%
    pause
    exit /b 1
)

:: Activate venv
call "%VENV_ACTIVATE%"

:: Build with nuitka
python -m nuitka --standalone --onefile "%PIGAS_PYTHON%"

:: Create directory for build files
mkdir %BUILD_DIRECTORY% 2>nul || rem
if not exist "%BUILD_DIRECTORY%" (
    echo Something gone wrong and build directory does not exist.
    pause
    exit /b 1
)

:: Copying files to build directory
copy /Y "template.config.yaml" "%BUILD_DIRECTORY%"
copy /Y "template.context.txt" "%BUILD_DIRECTORY%"
copy /Y "pigas.exe" "%BUILD_DIRECTORY%"
copy /y "README.txt" "%BUILD_DIRECTORY%"
robocopy "data" "%BUILD_DIRECTORY%/data" /E /COPYALL /IS
if %ERRORLEVEL% GEQ 8 (
    echo.
    echo ERROR: Copy failed (ErrorLevel=%ERRORLEVEL%).
    exit /b 1
)


:: Keep window open
echo.
echo Script finished. Check output above for errors.
pause