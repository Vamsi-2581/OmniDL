@echo off
title Launch browser with OmniDL Pro
cd /d "%~dp0"
rem Chrome 137+ ignores --load-extension, so use Edge (still honours it).
rem Own profile dir: the flag is ignored when the main Edge profile is already open.
echo Launching Microsoft Edge with OmniDL Pro Video Grabber pre-loaded...
start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --user-data-dir="%LOCALAPPDATA%\OmniDL\edge-profile" --no-first-run --load-extension="%~dp0extension"
exit
