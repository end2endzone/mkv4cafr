@echo off
set PATH=%PATH%;C:\Program Files\MKVToolNix

cd /d "%~dp0"

set PYTHONPATH=%CD%;%PYTHONPATH%
python tools/generate_medias/generate_medias.py
pause
