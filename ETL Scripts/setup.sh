#!/bin/bash

# Real Estate Search Engine - Setup Script
# This script sets up the environment and dependencies

echo "=========================================="
echo "Real Estate Search Engine - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version

if [ $? -ne 0 ]; then
    echo "Python not found. Please install Python 3.10+"
    exit 1
fi

echo "Python found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo "Dependencies installed"
echo ""

# Check .env file
echo "Checking configuration..."
if [ ! -f ".env" ]; then
    echo ".env file not found"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "Created .env file"
    echo "Please edit .env file with your actual credentials"
else
    echo ".env file found"
fi
echo ""

# Check MySQL connection
echo "Checking MySQL connection..."
python -c "
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        port=int(os.getenv('MYSQL_PORT', 3306))
    )
    conn.close()
    print('MySQL connection successful')
except Exception as e:
    print(f'MySQL connection failed: {e}')
"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs
echo "Directories created"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python setup_db.py (to initialize database)"
echo "3. Run: streamlit run Home.py (to start the app)"
echo ""
