@echo off
set /p fname=Enter the filename (example: fix.ps1): 
echo Creating %fname%
type nul > "%fname%"
echo Opening Notepad for editing...
start notepad.exe "%fname%"
exit
