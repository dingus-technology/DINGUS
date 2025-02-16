#!/bin/bash
# code-checks.sh

LINE_LENGTH=120
APP_DIR="/src"

# Color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

# Run black and capture any errors
echo -e "${BLUE}Running black...${NC}"
black_output=$(black $APP_DIR -l $LINE_LENGTH --check 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}black failed with errors:${NC}"
    echo -e "${YELLOW}$black_output${NC}"
fi

# Run flake8 and capture any errors
echo -e "${BLUE}Running flake8...${NC}"
flake8_output=$(flake8 $APP_DIR --max-line-length=$LINE_LENGTH 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}flake8 failed with errors:${NC}"
    echo -e "${YELLOW}$flake8_output${NC}"
fi

# Run mypy and capture any errors
echo -e "${BLUE}Running mypy...${NC}"
mypy_output=$(mypy $APP_DIR 2>&1)
if [[ $? -ne 0 ]]; then
    echo -e "${RED}mypy failed with errors:${NC}"
    echo -e "${YELLOW}$mypy_output${NC}"
fi
