@echo off
:: Batch script to build PIGAS

chcp 65001

cd /d "%~dp0"

set VENV_ACTIVATE=.venv\Scripts\activate
set BUILD_DIRECTORY=pigas
set PIGAS_PYTHON=pigas.py
set PIGAS_BINARY=pigas.exe
set CONFIG=tmp.config.yaml
set CONTEXT=tmp.context.txt
set README="READ_ME_PLEASE.md"
set DATA_DIR=data

:: Activate venv
call "%VENV_ACTIVATE%"

:: Build with nuitka
echo Start building application
python -m nuitka --enable-plugin=tk-inter --standalone --onefile "%PIGAS_PYTHON%"
echo Build finished

echo Start copying files in %BUILD_DIRECTORY% directory

:: Create build directory
mkdir %BUILD_DIRECTORY% 2>nul || rem

:: Copy files
move "%PIGAS_BINARY%" "%BUILD_DIRECTORY%"
copy /Y "%CONFIG%" "%BUILD_DIRECTORY%"
copy /Y "%CONTEXT%" "%BUILD_DIRECTORY%"
copy /y "%README%" "%BUILD_DIRECTORY%"
robocopy "%DATA_DIR%" "%BUILD_DIRECTORY%/%DATA_DIR%" /E /COPYALL /IS
echo Copying finished
echo Done

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

@REM if not exist "%BUILD_DIRECTORY%" (
@REM     echo Something gone wrong and build directory does not exist.
@REM     pause
@REM     exit /b 1
@REM )

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