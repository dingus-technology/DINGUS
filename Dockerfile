FROM python:3.11-slim

ENV USER_NAME=dingus
ENV PROJECT_NAME="CHAT-WITH-LOGS"

# Update system dependencies
RUN apt-get update \
    && apt-get install -y dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG UID=1000
ARG GID=1001
RUN groupadd -g ${GID} $USER_NAME && \
    useradd -m -u ${UID} --gid ${GID} $USER_NAME

USER $USER_NAME

WORKDIR /src

ENV ENV_PATH=/home/$USER_NAME/venv
RUN python -m venv ${ENV_PATH}
ENV PATH="$ENV_PATH/bin:$PATH" \
    PYTHONPATH="${PYTHONPATH}:/src/"

# Copy over requirements
COPY --chown=$USER_NAME:$USER_NAME requirements.txt /src/requirements.txt

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r /src/requirements.txt

# Copy source code
COPY --chown=$USER_NAME:$USER_NAME ./src /src/

# Ensure scripts have execute permissions
RUN chmod +x /src/scripts/

# Ensure LF line ending
RUN dos2unix /src/scripts/

# Add aliases for scripts
RUN echo 'alias format-checks="/src/scripts/format-checks.sh"' >> /home/$USER_NAME/.bashrc
RUN echo 'alias code-checks="/src/scripts/code-checks.sh"' >> /home/$USER_NAME/.bashrc

# Custom Shell Prompt
RUN echo 'PS1="\e[1;31m[$PROJECT_NAME] \e[1;34m\u@\h\e[m \w\$ "' >> /home/$USER_NAME/.bashrc

# Set the entrypoint
ENTRYPOINT ["/src/scripts/entrypoint.sh"]
