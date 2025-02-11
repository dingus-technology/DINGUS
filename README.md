# 🚀 Chat with Logs


---

## 🛠️ Setup

### 1. Create Your `.env` File

To begin, create your `.env` file from the provided `sample.env`. This will store all your environment variables and secrets securely.

Run the following command:

```bash
cp sample.env .env
```

### 2. Make src/scripts Executable

Ensure that the src/scripts directory is executable. Run the following command:

```bash
chmod +x src/scripts/*
```

### 3. Install Docker

This codebase requires Docker to run. Development was done using Docker version 20.10.17. If you don't have Docker installed, you can grab it here: [Docker Installation](https://www.docker.com/).

---

## 🐋 Getting Started with Docker

Now, let’s build and run your Docker container. It's time to get the engine running!

### 1. Build the Docker Image

First, build the Docker image by running:

```bash
docker compose up --build
```

This command will pull in all dependencies, build the image, and start the container.

### 2. Access the App Container

To enter the container's bash shell, run:

```bash
docker compose exec app bash
```

Welcome inside! You're now in the heart of the Docker container, ready to execute commands, explore the environment, and start developing.

### 3. Run Code Checks

Ensure your code is in top shape! Run the following commands to format and check your code:

```bash
format-checks
code-checks
```

These will ensure that your code adheres to best practices and is properly formatted.

---

# Chat With Logs

To run the chat cli:

```bash
python app/chat_with_logs.py
```
