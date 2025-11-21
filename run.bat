@echo off
echo Starting Telegram Post Bot...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/Update requirements
echo Installing requirements...
pip install -r requirements.txt
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    pause
    exit /b 1
)

REM Check if database is initialized
if not exist "data\database\bot.db" (
    echo Initializing database...
    python -m src.database.init_db
    echo.
)

REM Run the bot
echo Starting bot...
python -m src.bot

pause
