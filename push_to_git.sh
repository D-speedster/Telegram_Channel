#!/bin/bash

echo "Preparing project for Git..."
echo ""

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    echo ""
fi

# Add all files (respecting .gitignore)
echo "Adding files to Git..."
git add .
echo ""

# Show status
echo "Current status:"
git status
echo ""

# Commit
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Update project files"
fi

echo "Committing changes..."
git commit -m "$commit_msg"
echo ""

# Set main branch
echo "Setting main branch..."
git branch -M main
echo ""

# Add remote if not exists
if ! git remote | grep -q origin; then
    echo "Adding remote origin..."
    git remote add origin https://github.com/D-speedster/Telegram_Channel.git
    echo ""
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main
echo ""

echo "Done!"
