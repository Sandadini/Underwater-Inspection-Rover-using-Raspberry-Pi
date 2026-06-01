# Smart Underwater Inspection Rover using Raspberry Pi 🌊🚀

## Overview

The Smart Underwater Inspection Rover is a remotely operated underwater vehicle (ROV) developed using Raspberry Pi 4 for real-time navigation, live video streaming, and environmental monitoring. The system is designed to provide reliable underwater operation through a tethered Ethernet connection while collecting visual and sensor data from aquatic environments.

The rover utilizes four brushless thrusters controlled via Electronic Speed Controllers (ESCs), enabling stable maneuverability in both horizontal and vertical directions. An onboard Raspberry Pi Camera provides live video feedback to the operator, while a waterproof temperature sensor continuously monitors water temperature and logs measurements for further analysis.

This project demonstrates the integration of embedded systems, robotics, networking, and environmental sensing technologies to create a cost-effective underwater inspection platform.

---

## Features

- Real-time underwater navigation and control
- Live video streaming using Raspberry Pi Camera
- Four-thruster propulsion system
- Waterproof temperature monitoring
- Ethernet-based tethered communication
- Custom Python-based GUI
- CSV data logging for sensor readings
- Stable underwater operation with balanced propulsion
- Modular architecture for future upgrades

---

## Hardware Components

| Component | Purpose |
|------------|------------|
| Raspberry Pi 4 | Main Controller |
| Raspberry Pi Camera Module | Live Video Streaming |
| 4 Brushless DC Motors | Underwater Propulsion |
| 4 ESCs | Motor Speed Control |
| Waterproof Temperature Sensor | Environmental Monitoring |
| Ethernet Cable | Communication Link |
| LiPo Battery Pack | Power Supply |
| Waterproof Enclosure | Protection of Electronics |

---

## System Architecture

```text
Operator Laptop
       │
   Ethernet Tether
       │
 Raspberry Pi 4
 ├── Camera Module
 ├── Temperature Sensor
 ├── ESC Controller
 │     ├── Thruster 1
 │     ├── Thruster 2
 │     ├── Thruster 3
 │     └── Thruster 4
 └── PyQt Control Interface
```

---

## Software Stack

- Python 3
- PyQt5
- OpenCV
- pigpio
- RPi.GPIO
- Raspberry Pi OS
- RealVNC

---

## Project Structure

```text
Underwater-Rover/
│
├── README.md
├── requirements.txt
│
├── code/
│   ├── main.py
│   ├── motor_control.py
│   ├── camera_stream.py
│   ├── temperature_sensor.py
│   └── gui.py
│
├── images/
│   ├── rover.jpg
│   ├── pool_test.jpg
│   └── system_diagram.png
│
└── docs/
    └── project_report.pdf
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/underwater-rover.git
cd underwater-rover
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

---

## Testing Results

The rover was successfully tested in a controlled pool environment.

### Test Outcomes

- Stable underwater operation
- Smooth horizontal and vertical navigation
- Successful live video transmission
- Accurate temperature monitoring
- Reliable Ethernet communication
- No water leakage detected during testing

---

## Applications

- Underwater inspections
- Environmental monitoring
- Aquaculture observation
- Educational robotics projects
- Marine research applications

---

## Future Improvements

- IMU-based stabilization
- Depth and pressure sensing
- Sonar integration
- Autonomous navigation
- AI-based object detection
- Cloud-based telemetry dashboard

---

## Demonstration

Add your project photos and testing videos here.

### Pool Testing

![Pool Test](images/pool_test.jpg)

---

## Author

Developed as an embedded systems and robotics project focused on underwater exploration, remote inspection, and environmental monitoring using Raspberry Pi and Python.
