#!/usr/bin/env bash

# Test runner script

set -e

echo "🧪 Running test suite..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run code formatting checks
echo "🎨 Checking code formatting..."
black --check src tests || {
    echo "❌ Code formatting issues found. Run: black src tests"
    exit 1
}

# Run import sorting checks
echo "📦 Checking import sorting..."
isort --check-only src tests || {
    echo "❌ Import sorting issues found. Run: isort src tests"
    exit 1
}

# Run linting
echo "🔍 Running linting..."
flake8 src tests

# Run type checking
echo "🔍 Running type checking..."
mypy src

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80

echo "✅ All tests passed!"
