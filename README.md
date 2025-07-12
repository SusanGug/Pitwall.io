# F1 24 Real-Time Telemetry Dashboard

## Overview

This project provides a professional-grade, real-time telemetry analysis platform for the F1 24 game. The core purpose is to empower drivers to use data-driven insights to improve their performance, refine their race craft, and gain a competitive edge.

By capturing and visualizing live data from the car—such as throttle, brake, steering, and speed—you can move beyond guesswork and start analyzing your driving with precision. This tool is designed for serious racers who want to:

-   **Analyze Driving Technique:** Dissect every corner to see exactly where you are applying throttle, braking, and turning. Identify inconsistencies and opportunities for improvement.
-   **Optimize Lap Times:** Compare laps side-by-side to understand where you are gaining or losing time. Pinpoint the specific braking points and racing lines that lead to faster results.
-   **Train Effectively:** Use the real-time feedback during practice sessions to immediately correct mistakes and build better habits.
-   **Gain a Deeper Understanding:** See the direct relationship between your inputs and the car's performance, leading to a more intuitive feel for the vehicle dynamics.

The entire system is orchestrated with Docker, providing a high-performance pipeline that takes raw UDP game data and transforms it into actionable insights on a live Grafana dashboard.

### Features
- **Real-Time Visualization:** See your speed, throttle, brake, gear, and more updated live in Grafana.
- **Custom Python Parser:** Easily extendable to parse any F1 24 UDP packet. Full control over the data format.
- **Persistent Data Storage:** InfluxDB stores all your session data, allowing for post-race analysis.
- **One-Command Setup:** The entire stack (Parser, Telegraf, InfluxDB, Grafana) is orchestrated with Docker Compose for a simple startup.
- **Pre-configured Grafana:** The Grafana service is pre-configured with the InfluxDB data source, so you can start building panels immediately.

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- A copy of the F1 24 game
- [Git](https://git-scm.com/downloads) for cloning the repository

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Build and Start the Services**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up -d --build
    ```
    This command builds the custom Telegraf image and starts all services in the background.

3.  **Configure F1 24 Telemetry**
    In the F1 24 game, go to `Settings > Telemetry Settings` and configure it to send data to your computer's local IP address.
    
    - **UDP IP Address:** The IP address of the machine running Docker.
        - **Windows:** Open Command Prompt and type `ipconfig`. Look for the "IPv4 Address".
        - **macOS/Linux:** Open a terminal and type `ifconfig` or `ip a`. Look for the `inet` address.
    - **UDP Port:** `20777`
    - **UDP Send Rate:** `60 Hz` is recommended for smooth data.
    - **UDP Format:** `2024`

4.  **Access Grafana**
    - Open your web browser and navigate to [http://localhost:3000](http://localhost:3000).
    - Log in with the default credentials:
      - **Username:** `admin`
      - **Password:** `admin`
    - You will be prompted to change the password on first login.

## Creating Dashboards

The Grafana instance is already connected to your InfluxDB database. The data source is named `InfluxDB F1 Telemetry` and it reads from the `f1-telemetry` bucket.

To create a new panel:
1.  Create a new dashboard or open an existing one.
2.  Click "Add panel" -> "Add new panel".
3.  In the query editor, make sure the `InfluxDB F1 Telemetry` data source is selected.
4.  Switch to the "Code" view and paste in a Flux query.

### Example Flux Queries

Here are some queries to get you started.

#### Throttle & Brake for All Cars
```flux
inputs = from(bucket: "f1-telemetry")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r._measurement == "CarTelemetry")
    |> filter(fn: (r) => r._field == "throttle" or r._field == "brake")
    |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

names = from(bucket: "f1-telemetry")
    |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r._measurement == "Participants" and r._field == "name")
    |> last()
    |> keep(columns: ["carIndex", "_value"])
    |> rename(columns: {_value: "driverName"})

join(tables: {data: inputs, names: names}, on: ["carIndex"])
    |> keep(columns: ["_time", "_value", "_field", "driverName"])
    |> pivot(rowKey:["_time"], columnKey: ["driverName", "_field"], valueColumn: "_value")
    |> yield(name: "Throttle and Brake")
```

## Troubleshooting

- **"No Data" in Grafana:** If your queries are valid but return no data, it usually means data isn't reaching InfluxDB. Check the Telegraf logs for errors:
  ```bash
  docker-compose logs telegraf
  ```
- **`bucket not found` error:** This means the `f1-telemetry` bucket doesn't exist. This can happen if the InfluxDB volume was cleared. You can manually create it in the [InfluxDB UI](http://localhost:8086) under `Data > Buckets`.

## Project Internals

- **Services Overview:**
  - **InfluxDB:** Time-series database listening on `http://localhost:8086`.
  - **Telegraf:** Executes the Python parser to collect telemetry data.
  - **Grafana:** Visualization dashboard available at `http://localhost:3000`.
- **`docker-compose.yml`**: Orchestrates all the services.
- **`f1_24_telemetry_parser.py`**: The Python script that listens for UDP packets and prints them in InfluxDB Line Protocol format.
- **`packets/`**: Contains Python dataclasses for each F1 24 UDP packet type, making the parser modular and easy to read.
- **`telegraf/`**: Holds the `telegraf.conf` and a `Dockerfile` to build a custom Telegraf image with Python installed.
- **`grafana/`**: Contains provisioning files to automatically configure the Grafana data source. 