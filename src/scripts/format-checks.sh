#!/bin/bash
# format-checks.sh
# code formating tool

LINE_LENGTH=120
APP_DIR="/src"

isort --profile black --check $APP_DIR
black --check -l $LINE_LENGTH $APP_DIR