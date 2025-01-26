@echo off
set PATH=%PATH%;C:\Program Files\MKVToolNix

cd /d "%~dp0"

python generate.py
pause
