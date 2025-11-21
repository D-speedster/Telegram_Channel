#!/bin/bash

echo "Starting Telegram Post Bot..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Install/Update requirements
echo "Installing requirements..."
pip install -r requirements.txt
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    echo ""
    exit 1
fi

# Check if database is initialized
if [ ! -f "data/database/bot.db" ]; then
    echo "Initializing database..."
    python -m src.database.init_db
    echo ""
fi

# Run the bot
echo "Starting bot..."
python -m src.bot
