# [Dingus](https://www.dingusai.dev) Advanced Bug Identification and Debugging

![Dingus Screenshot](assets/screenshot.png)


## 🛠️ Setup Guide  

### 1️⃣ Create Your `.env` File  

Before getting started, configure your environment variables and folders. Copy the sample configuration:  

```bash
mkdir logs data reports .kube
cp sample.env .env
```

##### Configure Environment Variables  

These environment variables are essential for connecting to **K8** & **Loki** (Note: if you are using linux, swap `http://host.docker.internal` with your host machine's local IP).

*If you do not wish to start with your Loki production logs, [use this simulation repository](https://github.com/dingus-technology/INFRASTRUCTURE-SIMULATION) for creating simulated logs locally*


| Variable Name        | Example Value           | Description                                                    |
| -------------------- | ----------------------- | -------------------------------------------------------------- |
| **OPENAI_API_KEY**   | `sk-xxxxxxxxxx`         | API key for OpenAI, required for AI-driven log analysis.       |
| **LOKI_URL**         | `http://localhost:3100` | URL of your Loki instance, where logs are stored and queried.  |
| **LOKI_JOB_NAME**    | `my-app-logs`           | The Loki job name that Chat with Logs will analyze for issues. |
| **KUBE_CONFIG_PATH** | `file_path/config.yaml` | The Kubernetes config file path.                               |
---

### 2️⃣ Using colima

If running on mac, use colima for reduced overheads rather that Docker Desktop

```bash
colima start
```

## 🐳 Running with Docker

### 1. Build & Start the Docker Container

Run the following command to build and start everything:

```bash
docker compose up --build
```

This will pull dependencies, build the image, and fire up the container.

### 2. Enter the App Container

```bash
docker compose exec dingus bash
```

### ✅ 3. Run Code Checks

Keep your code clean and formatted:

```bash
format-checks
code-checks
```
