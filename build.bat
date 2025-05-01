@echo off
:: Batch script to build PIGAS

cd /d "%~dp0"

set BUILD_DIRECTORY=pigas
set VENV_ACTIVATE=.venv\Scripts\activate
set PIGAS_PYTHON=pigas.py

:: Check if Python script exists
@REM if not exist "%PIGAS_PYTHON%" (
@REM     echo Python script not found: %PIGAS_PYTHON%
@REM     pause
@REM     exit /b 1
@REM )

:: Check if venv exists
@REM if not exist "%VENV_ACTIVATE%" (
@REM     echo Virtual environment not found at: %VENV_ACTIVATE%
@REM     pause
@REM     exit /b 1
@REM )

:: Activate venv
call "%VENV_ACTIVATE%"

:: Build with nuitka
echo Start building application.
python -m nuitka --standalone --onefile "%PIGAS_PYTHON%"
echo Build finished

:: Create directory for build files
mkdir %BUILD_DIRECTORY% 2>nul || rem
@REM if not exist "%BUILD_DIRECTORY%" (
@REM     echo Something gone wrong and build directory does not exist.
@REM     pause
@REM     exit /b 1
@REM )

:: Copying files to build directory
move "pigas.exe" "%BUILD_DIRECTORY%"
copy /Y "template.config.yaml" "%BUILD_DIRECTORY%"
copy /Y "template.context.txt" "%BUILD_DIRECTORY%"
copy /y "PLEASE README FIRST.md" "%BUILD_DIRECTORY%"
robocopy "data" "%BUILD_DIRECTORY%/data" /E /COPYALL /IS


@REM if %ERRORLEVEL% GEQ 8 (
@REM     echo.
@REM     echo ERROR: Copy failed (ErrorLevel=%ERRORLEVEL%).
@REM     pause
@REM     exit /b 1
@REM )


@REM :: Keep window open
@REM if %ERRORLEVEL% GEQ 8 (
@REM     echo ERROR: Copy failed (ErrorLevel=%ERRORLEVEL%).
@REM )

@REM if %ERRORLEVEL% LSS 8 (
@REM     echo ERROR occurs: (ErrorLevel=%ERRORLEVEL%).
@REM )

echo.
pause