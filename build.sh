#!/bin/bash

# shellcheck disable=SC2164
cd "$(dirname "$0")"

export BUILD_DIRECTORY=pigas
export VENV_ACTIVATE=.venv/bin/activate
export PIGAS_PYTHON=pigas.py

# shellcheck disable=SC1090
source $VENV_ACTIVATE

echo Start building application.
python -m nuitka --standalone --onefile $PIGAS_PYTHON
echo Build finished

mkdir -p $BUILD_DIRECTORY
mv pigas.bin $BUILD_DIRECTORY/
cp -r data $BUILD_DIRECTORY/
cp "PLEASE README FIRST.md" $BUILD_DIRECTORY/
cp template.config.yaml $BUILD_DIRECTORY/
cp template.context.txt $BUILD_DIRECTORY/

