@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~dp0.."
set "PY_SCRIPT=%ROOT_DIR%\spotify_dj_preview_downloader.py"

if not exist "%PY_SCRIPT%" (
  echo [ERROR] Script introuvable: "%PY_SCRIPT%"
  exit /b 1
)

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "MODE=%~1"
set "INPUT=%~2"
set "OUTPUT="
set "OVERWRITE="

if not "%~3"=="" (
  if /I "%~3"=="--overwrite" (
    set "OVERWRITE=--overwrite"
  ) else (
    set "OUTPUT=%~3"
  )
)

if not "%~4"=="" (
  if /I "%~4"=="--overwrite" (
    set "OVERWRITE=--overwrite"
  ) else (
    echo [ERROR] Option inconnue: %~4
    goto :usage
  )
)

if /I "%MODE%"=="preview" goto :run_preview
if /I "%MODE%"=="full-legal" goto :run_full_legal

echo [ERROR] Mode inconnu: %MODE%
goto :usage

:run_preview
if "%OUTPUT%"=="" (
  python "%PY_SCRIPT%" preview "%INPUT%" %OVERWRITE%
) else (
  python "%PY_SCRIPT%" preview "%INPUT%" -o "%OUTPUT%" %OVERWRITE%
)
exit /b %ERRORLEVEL%

:run_full_legal
if "%OUTPUT%"=="" (
  python "%PY_SCRIPT%" full-legal "%INPUT%" %OVERWRITE%
) else (
  python "%PY_SCRIPT%" full-legal "%INPUT%" -o "%OUTPUT%" %OVERWRITE%
)
exit /b %ERRORLEVEL%

:usage
echo Usage:
echo   cmd\lancer.cmd preview ^<playlist_url_ou_id^> [output_dir] [--overwrite]
echo   cmd\lancer.cmd full-legal ^<manifest.csv^> [output_dir] [--overwrite]
echo.
echo Exemples:
echo   cmd\lancer.cmd preview "https://open.spotify.com/playlist/PLAYLIST_ID"
echo   cmd\lancer.cmd preview "PLAYLIST_ID" mes_previews --overwrite
echo   cmd\lancer.cmd full-legal manifest.csv mes_full_tracks
exit /b 1
