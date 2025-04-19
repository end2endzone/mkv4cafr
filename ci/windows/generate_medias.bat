@echo off

:: Set PRODUCT_SOURCE_DIR root directory
setlocal enabledelayedexpansion
if "%PRODUCT_SOURCE_DIR%"=="" (
  :: Delayed expansion is required within parentheses https://superuser.com/questions/78496/variables-in-batch-file-not-being-set-when-inside-if
  cd /d "%~dp0"
  cd ..\..
  set PRODUCT_SOURCE_DIR=!CD!
  cd ..\..
  echo PRODUCT_SOURCE_DIR set to '!PRODUCT_SOURCE_DIR!'.
)
endlocal & set PRODUCT_SOURCE_DIR=%PRODUCT_SOURCE_DIR%
echo.

:: Return back to scripts folder
cd /d "%~dp0"

:: Allow finding MKVToolNix tools more easily from PATH
set PATH=%PATH%;C:\Program Files\MKVToolNix

:: Generate media files
echo "Starting media generation..."
python -m tools.generate_medias.generate_medias
if %errorlevel% neq 0 pause && exit /b %errorlevel%
echo "Media generation completed."
echo.
