@echo off
cd /d "%~dp0"
python -m learning.web_server --open
if errorlevel 1 pause
