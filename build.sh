#!/bin/bash
# Bash script to build PIGAS

# shellcheck disable=SC2164
cd "$(dirname "$0")"

export VENV_ACTIVATE=.venv/bin/activate
export BUILD_DIRECTORY=pigas
export PIGAS_PYTHON=pigas.py
export PIGAS_BINARY=pigas.bin
export CONFIG=tmp.config.yaml
export CONTEXT=tmp.context.txt
export README="READ_ME_PLEASE.md"
export DATA_DIR=data

# shellcheck disable=SC1090
source $VENV_ACTIVATE

# Build with nuitka
echo Start building application
python -m nuitka --standalone --onefile $PIGAS_PYTHON
echo Build finished

echo Start copying files in $BUILD_DIRECTORY directory

# Create build directory
mkdir -p $BUILD_DIRECTORY

# Copy files
mv $PIGAS_BINARY $BUILD_DIRECTORY/
cp -r $DATA_DIR $BUILD_DIRECTORY/
cp $README $BUILD_DIRECTORY/
cp $CONFIG $BUILD_DIRECTORY/
cp $CONTEXT $BUILD_DIRECTORY/
echo Copying finished
echo Done

