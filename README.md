
# [Dingus](https://www.dingusai.dev) – Advanced Bug Identification and Debugging

![Dingus Screenshot](assets/screenshot.png)

Dingus isn’t just another log viewer - it’s your debugging partner. Instead of drowning in dashboards and grepping through logs, Dingus automatically:

* Surfaces the issues that actually matter
* Traces them back to your codebase
* Suggests practical fixes you can apply immediately

### Why Developers Use Dingus

* **Zero guesswork** → Know *what* broke and *where* in minutes, not hours
* **Context-rich insights** → See errors in the bigger picture of your system
* **Code-first debugging** → Jump straight from anomalies to actionable fixes

If you’ve ever burned a day chasing a production bug that turned out to be something trivial, Dingus was built for you.


## 🛠️ Setup Guide

### Kubernetes Config

For Dingus to observe your K8s cluster, place your kube config in the top-level directory:

```bash
DINGUS/.kube/config
```

### Running on Mac (Colima Recommended)

On macOS, use [Colima](https://github.com/abiosoft/colima) for reduced overhead compared to Docker Desktop:

```bash
colima start
```

---

## 🐳 Run Dingus with Docker

### Build & Start

Spin everything up in one step:

```bash
docker compose up --build
```

Once running, open [http://0.0.0.0:8501/](http://0.0.0.0:8501/) and add your configs.

👉 No production logs handy? Try our [simulation repo](https://github.com/dingus-technology/INFRASTRUCTURE-SIMULATION) to generate fake logs locally.

---

## ✅ Development: Run Code Checks

Keep the codebase clean and consistent:

```bash
docker compose exec dingus bash
```

Then run:

```bash
format-checks
code-checks
```


## ⚙️ Optional Configuration

Set environment variables by copying the sample file:

```bash
cp sample.env .env
```

These are required for connecting Dingus to **K8s** and **Loki**.

> **Note:** On Linux, replace `http://host.docker.internal` with your host machine’s local IP.

👉 Don’t want to connect Loki yet? Use the [simulation repo](https://github.com/dingus-technology/INFRASTRUCTURE-SIMULATION) to get started locally.

| Variable Name        | Example Value           | Description                                                   |
| -------------------- | ----------------------- | ------------------------------------------------------------- |
| **OPENAI_API_KEY**   | `sk-xxxxxxxxxx`         | API key for OpenAI (AI-driven log analysis).                  |
| **LOKI_URL**         | `http://localhost:3100` | URL of your Loki instance, where logs are stored and queried. |
| **LOKI_JOB_NAME**    | `my-app-logs`           | The Loki job name that Dingus will analyze.                   |
| **KUBE_CONFIG_PATH** | `file_path/config.yaml` | Path to your Kubernetes config file.                          |


## 🚀 What’s Next?

* Hook Dingus up to your real cluster and logs
* Start catching bugs **before they catch you**
* Move from reactive firefighting to proactive debugging
