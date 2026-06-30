# PC Health Assistant

A lightweight, draggable desktop-style widget that monitors your computer's health in real time. It features a modern HTML/CSS/JavaScript frontend and a Flask Python backend to fetch real-time system metrics. It is designed to present technical telemetry in a simple, friendly manner for non-technical users.

---

## Features

- **Health Score**: A weighted overall system health score (0-100) calculated based on RAM, CPU, Storage, and Temperature.
- **RAM Arc Gauge**: A primary circular gauge display showing current RAM usage in percent and gigabytes.
- **Key Metrics Panel**: Sleek status progress bars tracking:
  - CPU load (%)
  - Storage space used (%)
  - CPU temperature (°C) — with intelligent system temperature simulation on Windows where direct bios/driver access is restricted.
- **Top Consumer Micro-Card**: Displays the application currently consuming the most memory (e.g. `Chrome — 3.8 GB RAM`).
- **Smart Recommendations**: Evaluates all system parameters and flags the single most critical action required (e.g. warning to check ventilation if temperature is high or advising to close heavy apps if RAM is full).
- **Interactive AI Diagnosis Modal**: Click on `[Why is my PC behaving this way?]` to preview the real-time JSON payload prepared for future Gemini/OpenAI diagnostic models.
- **Minimize & Drag**: Can be dragged anywhere on your desktop and minimized into a compact status pill.

---

## Setup & Running Instructions

### Prerequisites
Make sure you have Python installed. The system requires Python launcher (`py`).

### 1. Install Dependencies
Install the required libraries for the Python environment:
```bash
py -m pip install flask flask-cors psutil
```

### 2. Start the Backend Server
Run the Flask server script:
```bash
py app.py
```
This runs a local API server at `http://127.0.0.1:5000/api/stats`.

### 3. Open the Widget
Simply double-click or open **[pc_health_sticker.html](pc_health_sticker.html)** in any web browser. 

The widget will connect to your local backend and start updating dynamically every 3.5 seconds.
