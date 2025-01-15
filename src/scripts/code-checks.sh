#!/bin/bash
# code-checks.sh

LINE_LENGTH=120
APP_DIR="/src"

black $APP_DIR -l $LINE_LENGTH --check
flake8 $APP_DIR --max_line_length=$LINE_LENGTH
mypy $APP_DIR