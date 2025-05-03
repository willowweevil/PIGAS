#!/bin/bash
# Bash script to build PIGAS

# shellcheck disable=SC2164
cd "$(dirname "$0")"

export VENV_ACTIVATE=.venv/bin/activate
export PIGAS_PYTHON=pigas.py
export PIGAS_BINARY=pigas.bin
export CONFIG=tmp.config.yaml
export CONTEXT=tmp.context.txt
export OPEN_AI=tmp.open-ai.yaml
export README="READ_ME_PLEASE.pdf"
export FOR_BUILD_DIR=for_build
export DATA_DIR=data
export BUILD_DIR=pigas

# shellcheck disable=SC1090
source $VENV_ACTIVATE

# Build with nuitka
echo Start building application
python -m nuitka --standalone --onefile $PIGAS_PYTHON
echo Build finished

echo Start copying files in $BUILD_DIR/ directory

# Create build directory
mkdir -p $BUILD_DIR

# Copy files
mv $PIGAS_BINARY $BUILD_DIR/$PIGAS_BINARY
cp -r $DATA_DIR $BUILD_DIR/$DATA_DIR
cp $FOR_BUILD_DIR/$CONFIG $BUILD_DIR/
cp $FOR_BUILD_DIR/$OPEN_AI $BUILD_DIR/
cp $FOR_BUILD_DIR/$CONTEXT $BUILD_DIR/
cp $FOR_BUILD_DIR/$README $BUILD_DIR/
echo Copying finished
echo Done

