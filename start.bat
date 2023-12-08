@echo off
echo Starting Rutgers AutoSniper setup...

:: Check if the virtual environment directory exists, if not create it
if not exist .venv (
 echo Creating a Python virtual environment in the current directory...
 python -m venv .venv
 call .venv\Scripts\activate
 echo Installing dependencies from requirements.txt...
 python -m pip install --upgrade pip
 pip install -r requirements.txt
) else (
 echo Activating the virtual environment...
 call .venv\Scripts\activate
)


:: Run the Python program in the ./src/configure.py directory
python .\src\configure.py

:: Ask the user if they want to hide the browser window. Don't make a new line after the question
set /p hide=Do you want to hide the browser window? (y/n): 
if %hide% == y (
 set args=
) else (
 set args=--browser
)

:: Run the appropriate Python script based on the user's choice
python .\src\sniper.py %args%