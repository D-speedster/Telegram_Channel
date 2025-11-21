# Telegram Channel Bot

A professional Telegram bot for managing channel posts with automated formatting and design features.

## Features

- Post creation with predefined types
- Movie post designer with automatic formatting
- Admin panel for managing post types
- Multi-admin support
- Automatic banner attachment
- Persian language support

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Configure your bot token and admin IDs
3. Initialize database:

```bash
python -m src.database.init_db
```

## Usage

```bash
python -m src.bot
```

## Project Structure

```
src/
├── bot.py              # Main entry point
├── config.py           # Configuration
├── database/           # Database models and management
├── handlers/           # Bot handlers
└── utils/              # Utility functions
```

## License

MIT
