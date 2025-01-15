# CHAT WITH LOGS

# Setup

1. Use `sample.env` as your starting point for creating your `.env` file, which will contain all environment variables and secrets.
   
2. Create your `.env` with:
```bash
cp sample.env .env
```

3. This codebase requires Docker. Development was done using Docker version 20.10.17. Get docker here - https://www.docker.com/ 

# Getting Started with Docker

To build and run the Docker container:

1. Build the Docker image:
```bash
docker compose up --build
```

2. Hop into container `app`:
```bash
docker compose exec app bash
```
You will now be inside the Docker container's bash shell.

3. Inside the docker container run scripts to format and check code:
```bash
format-checks
code-checks
```


