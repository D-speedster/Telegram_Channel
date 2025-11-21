.PHONY: help install init run clean test lint format

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make init     - Initialize database"
	@echo "  make run      - Run the bot"
	@echo "  make clean    - Clean cache files"
	@echo "  make test     - Run tests (future)"
	@echo "  make lint     - Run linter (future)"
	@echo "  make format   - Format code (future)"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

init:
	@echo "Initializing database..."
	python -m src.database.init_db

run:
	@echo "Starting bot..."
	python -m src.bot

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache cleaned!"

test:
	@echo "Running tests..."
	@echo "Tests not implemented yet"

lint:
	@echo "Running linter..."
	@echo "Linter not configured yet"

format:
	@echo "Formatting code..."
	@echo "Formatter not configured yet"

setup: install init
	@echo "Setup complete! Edit .env file and run 'make run'"
