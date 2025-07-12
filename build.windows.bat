@echo off
:: Batch script to build PIGAS

chcp 65001

cd /d "%~dp0"

set VENV_ACTIVATE=.venv\Scripts\activate
set PIGAS_PYTHON=pigas.py
set PIGAS_BINARY=pigas.exe
set CONFIG=tmp.config.yaml
set CONTEXT=tmp.context.txt
set OPEN_AI=tmp.open-ai.yaml
set README="README.md"
set IMAGE="pigas.png"
set FOR_BUILD_DIR=data\templates
set DATA_DIR=data
set BUILD_DIR=pigas

:: Activate venv
call "%VENV_ACTIVATE%"

:: Build with nuitka
echo Start building application
python -m nuitka --enable-plugin=tk-inter --standalone --onefile "%PIGAS_PYTHON%"
echo Build finished

echo Start copying files in %BUILD_DIR% directory

:: Create build directory
mkdir %BUILD_DIR% 2>nul || rem

:: Copy files
move "%PIGAS_BINARY%" "%BUILD_DIR%"
copy /Y "%FOR_BUILD_DIR%\%CONFIG%" "%BUILD_DIR%"
copy /y "%FOR_BUILD_DIR%\%OPEN_AI%" "%BUILD_DIR%"
copy /Y "%FOR_BUILD_DIR%\%CONTEXT%" "%BUILD_DIR%"
copy /y "%README%" "%BUILD_DIR%"
copy /y "%IMAGE%" "%BUILD_DIR%"
robocopy "%DATA_DIR%" "%BUILD_DIR%\%DATA_DIR%" /E /COPYALL /IS
echo Copying finished
echo Done
