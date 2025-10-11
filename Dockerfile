FROM python:3.11-slim

ENV USER_NAME=dingus
ENV PROJECT_NAME="DINGUS"

# Update system dependencies
RUN apt-get update \
    && apt-get install -y dos2unix curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/


# Create a non-root user
ARG UID=2000
ARG GID=3000
RUN groupadd -g ${GID} $USER_NAME && \
    useradd -m -u ${UID} --gid ${GID} $USER_NAME

# Make dirs and change owner 
RUN mkdir -p /logs /data /reports /.kube && chown -R $USER_NAME:$USER_NAME /logs /data /reports /.kube

# Set user
USER $USER_NAME

# Set dir
WORKDIR /src

# Python env
ENV ENV_PATH=/home/$USER_NAME/venv
RUN python -m venv ${ENV_PATH}
ENV PATH="$ENV_PATH/bin:$PATH" \
    PYTHONPATH="${PYTHONPATH}:/src/:/"

# Copy and install dependencies
COPY --chown=$USER_NAME:$USER_NAME /requirements.txt /src/requirements.txt
RUN pip install --upgrade pip && pip install -r /src/requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy source code
COPY --chown=$USER_NAME:$USER_NAME ./assets /assets/
COPY --chown=$USER_NAME:$USER_NAME ./src /src/

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Add aliases
RUN echo 'alias format-checks="bash /scripts/format-checks.sh"' >> /home/$USER_NAME/.bashrc
RUN echo 'alias code-checks="bash /scripts/code-checks.sh"' >> /home/$USER_NAME/.bashrc
RUN echo 'alias k="kubectl"' >> /home/$USER_NAME/.bashrc

# Custom shell prompt
RUN echo 'PS1="\e[1;31m[$PROJECT_NAME] \e[1;34m\u@\h\e[m \w\$ "' >> /home/$USER_NAME/.bashrc

# Expose port
EXPOSE 8000

ENTRYPOINT ["bash", "entrypoint.sh"]
