#!/bin/bash
# format-checks.sh
# code formating tool

LINE_LENGTH=120
APP_DIR="/src"

isort --profile black $APP_DIR
black -l $LINE_LENGTH $APP_DIR