#!/bin/sh

# Create environment
python -m venv env

# Install packages
pip install -r requirements.txt

# Set python working directory
export PYTHONPATH=.

# Run service
python src/main_api.py

## Create executable file
#pip install pyinstaller
#cd src
#pyinstaller --onefile --hidden-import=src.api main_api.py
#
## Move service and remove all code
## is this needed?
#
## Run service
#cd dist
#ls -l
#./main_api -e $1
