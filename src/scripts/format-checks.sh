#!/bin/bash
# format-checks.sh
# Code formatting tool

LINE_LENGTH=120
APP_DIR="/src"

echo "Sorting imports with isort..."
isort --profile black $APP_DIR

echo "Formatting code with black..."
black -l $LINE_LENGTH $APP_DIR

echo "✅ Formatting complete!"
