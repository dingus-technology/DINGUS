
# [Dingus](https://www.dingusai.dev) – Advanced Bug Identification and Debugging

![Dingus Screenshot](assets/screenshot.png)

# 📚 Contents

- [Dingus – Advanced Bug Identification and Debugging](#dingus--advanced-bug-identification-and-debugging)
- [📚 Contents](#-contents)
- [Why Developers Use Dingus](#why-developers-use-dingus)
  - [Workflows That Just Flow – Connect the in Dots Seconds, Not Hours](#workflows-that-just-flow--connect-the-in-dots-seconds-not-hours)
- [🛠️ Setup Guide](#️-setup-guide)
    - [Kubernetes Config](#kubernetes-config)
    - [Running on Mac (Colima Recommended)](#running-on-mac-colima-recommended)
  - [🐳 Run Dingus with Docker](#-run-dingus-with-docker)
      - [Build \& Start](#build--start)
    - [✅ Development: Run Code Checks](#-development-run-code-checks)
      - [Docker Hub Deployment](#docker-hub-deployment)


# Why Developers Use Dingus
Dingus is a tool to gather critical insights and recommend fixes, making it easier and faster to resolve production issues. Instead of drowning in dashboards and grepping through logs, Dingus automatically:

* Surfaces the issues that actually matter.
* Traces them back to the root.
* Suggests practical fixes you can apply immediately.

Dingus reviews logs, metrics, code, commits and more in order to build a holistic view of what casued a production issue.

* **Zero guesswork** → Know *what* broke and *where* in minutes, not hours.
* **Context-rich insights** → See errors in the bigger picture of your system.
* **Faster debugging** → Jump straight from anomalies to fixes.

If you’ve ever burned a day chasing a production bug that turned out to be something trivial, Dingus was built for you.

## Workflows That Just Flow – Connect the in Dots Seconds, Not Hours
We don’t believe in replacing your existing tools. Instead, we integrate with them to create a seamless experience. Our goal is to help you resolve issues faster by providing the right information and suggesting effective fixes.

![Dingus Integrations](assets/AI-logs-analysis-production-bug-fixes-chart-2.png)

# 🛠️ Setup Guide

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

## 🐳 Run Dingus with Docker

#### Build & Start

Spin everything up in one step:

```bash
docker compose up --build
```

Once running, open [http://0.0.0.0:8501/](http://0.0.0.0:8501/) and add your configs.

👉 No production logs handy? Try our [simulation repo](https://github.com/dingus-technology/INFRASTRUCTURE-SIMULATION) to generate fake logs locally.

> **Note:** Not on MacOS? Replace `http://host.docker.internal` with your host machine’s local IP in `DINGUS/docker-compose`.


### ✅ Development: Run Code Checks

Keep the codebase clean and consistent:

```bash
docker compose exec dingus bash
```

Then run:

```bash
format-checks
code-checks
```

#### Docker Hub Deployment

To push a new image use:
```bash
docker build -t dingusai/dingus:latest .;
docker login;
docker push dingusai/dingus:latest;
```
                       