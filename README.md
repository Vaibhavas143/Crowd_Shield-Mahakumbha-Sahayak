# Crowd_Shield-Mahakumbha-Sahayak
An AI-driven platform for real-time crowd monitoring, density analysis, and disaster management, specifically designed for large-scale events like the Nashik Kumbh Mela.

# CrowdShield: Kumbha Sahayak 🛡️

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.11+-brightgreen.svg)
![React Version](https://img.shields.io/badge/react-18.2.0-blue.svg)
![Status](https://img.shields.io/badge/status-in%20development-orange.svg)

An AI-driven platform for real-time crowd monitoring, density analysis, and disaster management, specifically designed for large-scale events like the Nashik Kumbh Mela.

---

## 📋 Table of Contents
- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [AI Core Setup](#ai-core-setup)
- [Usage](#usage)
- [Project Roadmap](#project-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🌟 About The Project

Managing mega-gatherings like the Kumbh Mela presents immense logistical and safety challenges. Overcrowding, stampedes, and medical emergencies are significant risks. **Kumbha Sahayak** (meaning "Kumbh Helper") is an AI-powered solution designed to provide law enforcement and event organizers with real-time, actionable intelligence to mitigate these risks.

By leveraging computer vision on live CCTV and drone feeds, the system automates the process of crowd counting and density analysis, presenting this information on an intuitive, map-based dashboard. This allows authorities to proactively identify potential hotspots, reroute crowds, and respond to emergencies with greater speed and efficiency.

## ✨ Key Features

* **Real-Time People Counting:** Utilizes YOLOv8 to detect and count individuals from live video streams.
* **Live Density Heatmaps:** Visualizes crowd concentration on a Google Maps interface, allowing for instant identification of congested areas.
* **Predictive Alerts:** Aims to forecast potential overcrowding events before they reach critical thresholds.
* **Optimized Route Recommendations:** Calculates and suggests the safest alternate paths for crowd dispersal or emergency evacuations.
* **Centralized Emergency Protocols:** Provides a single-click interface for authorities to trigger predefined emergency responses (e.g., medical, fire).

## 💻 Technology Stack

This project is a full-stack application built with a modern and scalable tech stack.

| Category | Technology |
| :--- | :--- |
| **Backend** | Python, Flask, Flask-RESTx, SQLAlchemy, Flask-Migrate, PyJWT, Flask-CORS |
| **Frontend** | React, Vite, React Router, Axios, Google Maps API |
| **AI Core** | Python, OpenCV, Ultralytics (YOLOv8) |
| **Database**| SQLite (Development), PostgreSQL (Production Recommended) |
| **Deployment** | Docker, Nginx (Planned) |

## 🏗️ Architecture

The project is designed with a decoupled microservice-like architecture:
1.  **Frontend (React):** The user interface / dashboard that operators interact with. It communicates with the backend via REST APIs.
2.  **Backend (Flask):** The central brain of the application. It handles API requests, user authentication, business logic, and database interactions.
3.  **AI Core (Python Script):** A separate process that handles the heavy computational work of video processing and people counting. It sends its findings to the Backend API.

## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing.

### Prerequisites

* Python 3.10+
* Node.js and npm
* Git

### Backend Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/kumbha-sahayak.git](https://github.com/your-username/kumbha-sahayak.git)
    cd kumbha-sahayak/backend
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv .venv
    .\.venv\Scripts\activate  # On Windows
    # source .venv/bin/activate # On macOS/Linux
    ```
3.  **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Create a `.env` file** in the `backend` folder and add your configuration:
    ```env
    FLASK_CONFIG=development
    SECRET_KEY=your_super_strong_random_secret_key
    DEV_DATABASE_URL=sqlite:///dev-db.sqlite
    GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    ```
5.  **Initialize and upgrade the database:**
    ```sh
    set FLASK_APP=run.py # On Windows
    # export FLASK_APP=run.py # On macOS/Linux
    flask db init
    flask db migrate -m "Initial schema"
    flask db upgrade
    ```
6.  **Create an admin user and add sample data:**
    ```sh
    flask create-admin
    flask add-sample-data
    ```

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```sh
    cd ../frontend # From the backend directory
    ```
2.  **Install npm packages:**
    ```sh
    npm install
    ```
3.  **Install Google Maps and other libraries:**
    ```sh
    npm install @react-google-maps/api react-router-dom axios
    ```

### AI Core Setup

1.  **Install AI dependencies** into the backend virtual environment:
    ```sh
    # From the backend directory with .venv active
    pip install requests opencv-python ultralytics
    ```

## 🚦 Usage

To run the full application, you need to start all three services in **separate terminals**.

1.  **Terminal 1 (Backend):**
    ```sh
    # In .../backend/ with .venv active
    python run.py
    ```
2.  **Terminal 2 (Frontend):**
    ```sh
    # In .../frontend/
    npm run dev
    ```
3.  **Terminal 3 (AI Core):**
    ```sh
    # In .../backend/ with .venv active
    python ai_core/stream_processor.py
    ```
Access the application by navigating to the URL provided by the frontend server (usually `http://localhost:5173`).

## 🗺️ Project Roadmap

- [x] Full-Stack Foundation & Database Setup
- [x] User Authentication with JWT
- [x] Basic Dashboard with Map & Markers
- [x] AI Core Simulator with Live Data Updates
- [ ] Implement Real-Time Updates with WebSockets
- [ ] Integrate Full YOLOv8 Model for Video File Processing
- [ ] Enhance Dashboard with Clickable Markers and Info Windows
- [ ] Build UI for Alerts and Route Recommendations
- [ ] Dockerize the Entire Application for Easy Deployment

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.


