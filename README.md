# Smart Underwater Inspection Rover using Raspberry Pi 🌊🚀

## Overview

This project is a remotely operated underwater rover (ROV) built using Raspberry Pi 4 for real-time navigation, live video streaming, and environmental monitoring. The system is designed for stable underwater control using a tethered Ethernet connection, allowing low-latency communication and reliable operation in aquatic environments.

The rover integrates a four-thruster propulsion system controlled via pigpio PWM signals, a Raspberry Pi Camera for live video feedback, and a waterproof temperature sensor for real-time environmental data logging. A custom PyQt5-based GUI provides full manual control, system monitoring, and camera interaction.

This project demonstrates embedded systems design, robotics control, and real-time data acquisition in underwater conditions.

---

## Features

- Real-time underwater navigation and control via GUI
- Live video streaming using Raspberry Pi Camera (Picamera2)
- Four-motor propulsion system using ESCs and pigpio PWM
- Waterproof temperature sensing with CSV logging
- Keyboard and button-based control interface
- Image capture from underwater camera feed
- Multi-threaded sensor monitoring and GUI updates
- Tethered Ethernet communication for stable control

---

## Hardware Components

- Raspberry Pi 4
- Raspberry Pi Camera Module
- 4 × Brushless DC Motors (Thrusters)
- 4 × Electronic Speed Controllers (ESCs)
- DS18B20 Waterproof Temperature Sensor
- JSN-SR04T Ultrasonic Sensor (Obstacle detection)
- Ethernet Cable (Tethered Communication)
- LiPo Battery Pack
- Waterproof Enclosure

---

## Software Stack

- Python 3
- PyQt5 (GUI Development)
- OpenCV (Image Processing)
- Picamera2 (Camera Interface)
- pigpio (PWM Motor Control)
- PIL (Image Handling)
- CSV Logging System
- Raspberry Pi OS

---

## Project Structure

```
Underwater-Inspection-Rover-using-Raspberry-Pi/
│
├── README.md
├── requirements.txt
│
├── code/
│   └── Underwater_Rover.py
│
├── images/
│   ├── rover.jpg
│   ├── pool_test.jpg
│   └── system_diagram.png
│
└── docs/
    └── Underwater_Rover_Presentation.pptx
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/Sandadini/Underwater-Inspection-Rover-using-Raspberry-Pi.git
cd Underwater-Inspection-Rover-using-Raspberry-Pi
```

---

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Install Raspberry Pi System Dependencies

```bash
sudo apt update
sudo apt install python3-picamera2 python3-pigpio
sudo systemctl start pigpiod
```

---

## Running the Project

```bash
python code/Underwater_Rover.py
```

---

## System Architecture

```
Operator Laptop
       │
   Ethernet Tether
       │
 Raspberry Pi 4
 ├── Camera Module (Live Feed)
 ├── Temperature Sensor (DS18B20)
 ├── Ultrasonic Sensor (Obstacle Detection)
 ├── pigpio PWM Controller
 │     ├── Thruster 1
 │     ├── Thruster 2
 │     ├── Thruster 3
 │     └── Thruster 4
 └── PyQt5 Control Interface
```

---

## Testing Results

The rover was tested in a controlled pool environment.

### Results:
- Stable underwater navigation
- Smooth directional control
- Real-time camera streaming
- Accurate temperature monitoring
- Reliable tethered communication
- No water leakage during testing

---

## Applications

- Underwater structure inspection
- Environmental monitoring
- Aquaculture observation
- Educational robotics projects
- Remote marine exploration

---

## Future Improvements

- IMU-based stabilization system
- Depth sensing and pressure monitoring
- Autonomous navigation mode
- Sonar-based obstacle detection
- AI-based underwater object detection
- Wireless control interface

---

## Demonstration

### Pool Testing
```
images/rover.jpg
```

---

## Author

Developed as an embedded systems and robotics project focused on underwater inspection, real-time control systems, and environmental monitoring using Raspberry Pi and Python.
