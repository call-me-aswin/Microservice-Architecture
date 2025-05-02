
# 🎬 Video to MP3 Converter – Microservices Architecture

## 🚀 Overview

This project showcases a **microservices-based architecture** for a full-stack **Video to MP3 Converter** application. It utilizes **Docker**, **Kubernetes**, **RabbitMQ**, and **Python-based services** to provide a scalable, containerized, and modular solution. Users can upload videos, convert them to MP3 format, and download the resulting files—all orchestrated seamlessly across distributed services.

---

## 🧩 Key Features

- 🔐 **Authentication Service** – Manages user login and token-based JWT authentication.
- 🌐 **API Gateway Service** – Routes requests to backend services and manages client interactions.
- 🎞️ **Converter Service** – Transforms uploaded video files into MP3 using `moviepy`.
- 📧 **Notification Service** – Sends email alerts once conversions are completed.
- 📬 **RabbitMQ** – Enables asynchronous communication between microservices.
- 🗃️ **MongoDB** – Stores video and MP3 files with GridFS.
- 🗄️ **MySQL** – Maintains user credentials and authentication data.

---

## 🏗️ System Architecture

```
             +-----------------+        +------------------+
             |                 |        |                  |
             |  Auth Service   +<------>+     MySQL DB     |
             |                 |        |                  |
             +--------+--------+        +---------+--------+
                      |                           |
                      | JWT                       |
                      v                           v
            +---------+---------+       +---------+---------+
            |                   |       |                   |
            |  Gateway Service  +<----->+     Frontend      |
            |                   |       |                   |
            +---------+---------+       +---------+---------+
                      |
                      v
             +--------+--------+
             |                 |
             | Converter Svc   |
             |                 |
             +--------+--------+
                      |
                      v
             +--------+--------+        +------------------+
             |                 |        |                  |
             | Notification Svc+<------>+     RabbitMQ      |
             |                 |        |                  |
             +-----------------+        +------------------+
                      |
                      v
             +--------+--------+
             |                 |
             |    MongoDB      |
             |                 |
             +-----------------+
```

---

## 📁 Project Structure

```
Microservice-Architecture/
└── python/
    └── src/
        ├── auth/             # Authentication microservice
        ├── converter/        # Video-to-MP3 conversion microservice
        ├── gateway/          # API gateway microservice
        ├── notification/     # Email notification microservice
        ├── rabbit/           # RabbitMQ configuration
        ├── Mongodb/          # MongoDB deployment configs
        ├── mysql/            # MySQL deployment configs
        ├── metallb-config.yaml # Load balancer configuration
        └── website/          # Frontend interface
```

---

## ⚙️ Prerequisites

Ensure the following are installed:

- [Docker](https://www.docker.com/)
- [Kubernetes](https://kubernetes.io/)
- [Minikube](https://minikube.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Python 3.10+

---

## 🛠️ Setup Instructions

1. **Start Minikube**

```bash
minikube start
```

2. **Deploy MetalLB (Load Balancer)**

```bash
kubectl apply -f metallb-config.yaml
```

3. **Deploy Services**

```bash
# MongoDB
kubectl apply -f python/src/Mongodb/mongodb-deployment.yaml
kubectl apply -f python/src/Mongodb/mongodb-service.yaml

# MySQL
kubectl apply -f python/src/mysql/manifests/pod.yaml
kubectl apply -f python/src/mysql/manifests/volume.yaml
kubectl apply -f python/src/mysql/manifests/mysql-service.yaml

# RabbitMQ
kubectl apply -f python/src/rabbit/manifests/

# Microservices
kubectl apply -f python/src/auth/manifests/
kubectl apply -f python/src/gateway/manifests/
kubectl apply -f python/src/converter/manifests/
kubectl apply -f python/src/notification/manifests/
```

4. **Access the Application**

- Open the frontend in `python/src/website/`.
- Update `AUTH_URL` and `GATEWAY_URL` in `script.js` with the correct Minikube IP and NodePorts.

---

## 🔧 Configuration

Each microservice uses environment variables managed via Kubernetes `ConfigMap` and `Secret` manifests. Refer to each service's manifest folder for details.

---

## 🛠️ Technologies

- **Backend**: Python (Flask, MoviePy, Pika)
- **Frontend**: HTML, CSS, JavaScript
- **Databases**: MongoDB, MySQL
- **Messaging**: RabbitMQ
- **Containerization**: Docker
- **Orchestration**: Kubernetes

---

## 🤝 Contributing

Contributions are welcome! Please fork this repository, create a feature branch, and submit a pull request.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
