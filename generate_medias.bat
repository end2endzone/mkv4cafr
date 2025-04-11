@echo off
set PATH=%PATH%;C:\Program Files\MKVToolNix

cd /d "%~dp0"

python -m tools.generate_medias.generate_medias
pause
