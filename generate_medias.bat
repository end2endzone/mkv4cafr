@echo off
set PATH=%PATH%;C:\Program Files\MKVToolNix

cd /d "%~dp0"

python src/generate_medias.py
pause
