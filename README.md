# Smart Bin IoT Monitoring System

This project is a full-stack IoT application designed to monitor the status of smart waste bins. It simulates sensor data, processes it in real-time, stores it in a database, generates alerts, and provides a web interface to visualize the data.

## Features

*   **Real-time Data Simulation**: A Python script (`publisher.py`) simulates smart bin sensors, sending capacity data over MQTT.
*   **MQTT Data Ingestion**: A subscriber service listens to MQTT topics for incoming sensor data.
*   **Data Processing & Alerting**: The system processes incoming data, stores it in MongoDB, and generates real-time alerts for events like "Bin Full" or "Bin Emptied".
*   **REST API**: A FastAPI backend provides endpoints to access the collected sensor readings, alerts, and reports.
*   **Web Dashboard**: A frontend application (in the `frontend` directory) consumes the API to display the system's status.

## System Architecture

The application consists of several key components:

1.  **Publisher (`publisher.py`)**: Simulates IoT devices. It reads sample data and publishes it to an MQTT broker on the `/smartbin/data` topic.
2.  **Subscriber (`subscriber.py`)**: The core of the backend. It subscribes to the MQTT topic, receives the data, and passes it to the processing module.
3.  **Data Processor (`methods/data_processor_alerts_generator.py`)**:
    *   Stores every raw sensor reading in a MongoDB `raw_logs` collection.
    *   Maintains the state of each bin.
    *   Generates alerts in the `alerts` collection when a bin's capacity crosses a defined threshold (e.g., becomes full or is emptied).
4.  **Database (`methods/database.py`)**: Manages the connection to a MongoDB database which contains collections for raw logs, alerts, and periodic reports.
5.  **API (`api.py`)**: A FastAPI server that exposes the data stored in MongoDB through a set of RESTful endpoints:
    *   `/api/readings`: Get the latest sensor readings.
    *   `/api/alerts`: Get the latest alerts.
    *   `/api/reports`: Get generated reports.
6.  **Frontend (`frontend/`)**: A web application that interacts with the API to provide a user-friendly dashboard for monitoring the smart bins.

## Getting Started

### Prerequisites

*   Python 3.x
*   MongoDB
*   An MQTT Broker (like Mosquitto)
*   Node.js (for the frontend)

### Backend Setup

1.  Clone the repository.
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt 
    ```
    *(Note: A `requirements.txt` file should be created from the virtual environment.)*
3.  Make sure your MongoDB and MQTT broker are running.
4.  Configure the connection strings in `methods/config.py` if they are not on localhost.
5.  Run the services:
    *   Start the subscriber to begin listening for data:
        ```bash
        python subscriber.py
        ```
    *   In a new terminal, start the data simulation:
        ```bash
        python publisher.py
        ```
    *   In another terminal, start the API server:
        ```bash
        uvicorn api:app --reload
        ```

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the frontend application:
    ```bash
    npm start
    ```
