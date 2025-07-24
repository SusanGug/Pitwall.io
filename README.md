# F1 24 Telemetry Dashboard

## Overview

This project provides self-hosted, real-time telemetry analysis platform for the **F1 24** game. It captures live UDP data from the game, processes it with a custom Python parser, stores it in InfluxDB, and visualizes it on a pre-configured Grafana dashboard.

![ApexDashboardDemoVideo](assets/ApexDashboardDemo.gif)

This tool is designed for sim racers who want to improve their race craft, optimize lap times, and gain a competitive edge.

### Features
- **Pre-configured Dashboard:** An "F1 Apex Dashboard" is automatically provisioned in Grafana, showing essential metrics like speed, gear, engine/brake temperatures, and throttle/brake inputs.
- **Real-Time Visualization:** All data is updated live, allowing for immediate feedback during a session (Like a race enginerring, a cool new way to play co-op).
- **Extensible Python Parser:** The parser is modular and can be easily extended to process more of the F1 24 UDP packets (You are welcome to contribute your own parser and Dashboard Design).
- **Persistent Data Storage:** InfluxDB stores all session data, enabling post-race analysis and lap comparisons.
- **One-Command Setup:** The entire stack (Parser, Telegraf, InfluxDB, Grafana) is managed with a single `docker-compose` command.
- **Export and Import Data for sharing:** Working on it

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- A copy of the F1 24 game
- [Git](https://git-scm.com/downloads) for cloning the repository

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/F1Dashboard.git
    cd F1Dashboard
    ```

2.  **Build and Start the Services**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up -d --build
    ```
    This command builds the custom Telegraf image and starts all services in the background.

3.  **Configure F1 24 Telemetry**
    In the F1 24 game, go to `Settings > Telemetry Settings` and configure it to send data to the IP address of the machine running Docker.
    
    - **UDP Port:** `20777` (This is the default port in the game, only edit if you know what you are doing).
    - **UDP Send Rate:** `60 Hz` is recommended for smooth data.
    - **UDP Format:** `2024`

4.  **Access Grafana**
    - Open your web browser and navigate to [http://localhost:3000](http://localhost:3000).
    - Log in with the default credentials:
      - **Username:** `admin`
      - **Password:** `admin`
    - You will be prompted to change the password on first login.
    - Pre-configured **"F1 Apex Dashboard"** will be available in the "Dashboards" section.

## Troubleshooting

- **How to Reset All Data:** If you want to start with a clean slate, you can stop the containers and remove the data volumes. This will delete all stored telemetry and Grafana settings.
  ```bash
  docker-compose down --volumes
  ```
  Then, restart the services with `docker-compose up -d`.
