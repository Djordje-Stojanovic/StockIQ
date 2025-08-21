@echo off
REM Setup Python for StockIQ project
echo Setting up Python environment variables...

REM Add Python to PATH for this session
set PATH=C:\Users\djord\AppData\Local\Programs\Python\Python313;C:\Users\djord\AppData\Local\Programs\Python\Python313\Scripts;%PATH%

REM Create python and py aliases
doskey python=C:\Users\djord\AppData\Local\Programs\Python\Python313\python.exe $*
doskey py=C:\Users\djord\AppData\Local\Programs\Python\Python313\python.exe $*
doskey pip=C:\Users\djord\AppData\Local\Programs\Python\Python313\Scripts\pip.exe $*

echo Python setup complete!
echo You can now use: python, py, or pip commands
python --version