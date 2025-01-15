# 🚀 Docker API Template

Welcome to the **Docker API Template**! This template is designed to streamline your Docker-based development workflow. Whether you're building an API or managing a complex system, this setup gets you up and running quickly. Here's how to get started:

---

## 🛠️ Setup

### 1. Create Your `.env` File

To begin, create your `.env` file from the provided `sample.env`. This will store all your environment variables and secrets securely.

Run the following command:

```bash
cp sample.env .env
```

### 2. Customize Your `.env`

In your new `.env` file, you'll need to configure your environment-specific variables.

For example:

```bash
USER_NAME=user
PROJECT_NAME="awesome-project"
```

### 3. Install Docker

This codebase requires Docker to run. Development was done using Docker version 20.10.17. If you don't have Docker installed, you can grab it here: [Docker Installation](https://www.docker.com/).

---

## 🚢 Getting Started with Docker

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

And that’s it! 🚀 You’re now ready to start developing with Docker. If you need help, feel free to explore the docs or contact the team. Enjoy the ride! 😄

---
