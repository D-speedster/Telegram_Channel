@echo off
echo Preparing project for Git...
echo.

REM Initialize git if not already initialized
if not exist ".git\" (
    echo Initializing Git repository...
    git init
    echo.
)

REM Add all files (respecting .gitignore)
echo Adding files to Git...
git add .
echo.

REM Show status
echo Current status:
git status
echo.

REM Commit
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update project files

echo Committing changes...
git commit -m "%commit_msg%"
echo.

REM Set main branch
echo Setting main branch...
git branch -M main
echo.

REM Add remote if not exists
git remote | findstr origin >nul
if errorlevel 1 (
    echo Adding remote origin...
    git remote add origin https://github.com/D-speedster/Telegram_Channel.git
    echo.
)

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main
echo.

echo Done!
pause
