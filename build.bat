@echo off
echo Building GW2Bard.exe...
pip install pyinstaller -q
pyinstaller gw2bard.spec --clean
echo.
echo Done! Executable in dist\GW2Bard.exe
pause