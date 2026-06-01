import sys
import pigpio
import time
import logging
import threading
import os
import glob
import csv
from datetime import datetime
import cv2
from picamera2 import Picamera2
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QSlider, QGroupBox, QFrame, QStatusBar,
                            QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor, QPalette, QIcon, QLinearGradient, QBrush

# Configure logging
logging.basicConfig(level=logging.INFO)
pi = pigpio.pi()
if not pi.connected:
    logging.error("Failed to connect to pigpio daemon. Exiting...")
    exit(1)

# Motor and sensor pin configuration
MOTOR_PINS = [12, 13, 18, 19]  # GPIO pins using BCM numbering
TRIGGER_PIN, ECHO_PIN = 23, 24  # JSN-SR04T sensor pins
OBSTACLE_THRESHOLD = 25  # cm

# Directory paths
PHOTO_DIR = "/home/fantastic4/Desktop/Data/captures/"
TEMP_DIR = "/home/fantastic4/Desktop/Data/temp/"
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Temperature sensor configuration
BASE_DIR = '/sys/bus/w1/devices/'
TEMP_LOG_PATH = '/home/fantastic4/Desktop/Data/temp/temperature_log.csv'
MEASUREMENT_LIMIT = 10

# Global variables
is_obstacle_detected = False
current_speed = 1200  # Default motor speed

# Define UI colors
DARK_BLUE = "#1E3A8A"
LIGHT_BLUE = "#3B82F6"
ACCENT_COLOR = "#10B981"
TEXT_COLOR = "#F1F5F9" 
BACKGROUND_COLOR = "#0F172A"
BUTTON_COLOR = "#2563EB"
BUTTON_HOVER = "#1D4ED8"
BUTTON_PRESSED = "#1E40AF"
BUTTON_TEXT = "#FFFFFF"
SLIDER_COLOR = "#6366F1"
WARNING_COLOR = "#EF4444"

class RobotControlUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Underwater Robot Control Center")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};")
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Track key states
        self.key_pressed = {
            "Up": False,
            "Down": False,
            "Left": False,
            "Right": False,
            "Space": False
        }
        
        # Initialize temperature sensor
        self.device_file = self.find_sensor()
        self.temp_data = []
        self.current_temp_c = None
        self.current_temp_f = None
        
        # Initialize camera
        self.picam2 = Picamera2()
        preview_config = self.picam2.create_preview_configuration(
            main={"size": (800, 600), "format": "RGB888"}
        )
        self.picam2.configure(preview_config)
        self.picam2.start()
        
        # Create main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create camera panel
        self.setup_camera_panel()
        
        # Create control panel
        self.setup_control_panel()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: {DARK_BLUE}; color: {TEXT_COLOR};")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Ready")
        
        # Start camera update timer
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self.update_camera_feed)
        self.camera_timer.start(30)  # Update every 30ms
        
        # Start temperature monitoring thread
        self.temp_thread = threading.Thread(target=self.temperature_update_loop, daemon=True)
        self.temp_thread.start()
        
        # Install event filter for key press events
        self.installEventFilter(self)
    
    def find_sensor(self):
        """Locate the DS18B20 sensor directory."""
        try:
            device_folder = glob.glob(BASE_DIR + '28*')[0]
            return device_folder + '/w1_slave'
        except IndexError:
            logging.error("Temperature sensor not found. Check connections.")
            return None
    
    def read_temp_raw(self):
        """Read raw temperature data from the sensor."""
        if self.device_file is None:
            logging.error("Sensor device file is None.")
            return None
        try:
            with open(self.device_file, 'r') as f:
                return f.readlines()
        except Exception as e:
            logging.error(f"Error reading temperature data: {e}")
            return None
    
    def read_temp(self):
        """Convert raw temperature data to Celsius and Fahrenheit."""
        if self.device_file is None:
            return None, None
        
        lines = self.read_temp_raw()
        if not lines:
            return None, None
        
        try:
            attempts = 0
            while lines[0].strip()[-3:] != 'YES':
                if attempts >= 5:
                    logging.error("Max retries reached while waiting for valid sensor reading.")
                    return None, None
                time.sleep(0.2)
                lines = self.read_temp_raw()
                attempts += 1
            
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * 9.0 / 5.0 + 32.0
                return temp_c, temp_f
        except Exception as e:
            logging.error(f"Error processing temperature: {e}")
            return None, None
    
    def setup_camera_panel(self):
        """Set up the camera panel with feed and controls."""
        self.camera_panel = QGroupBox("Live Camera Feed")
        self.camera_panel.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {LIGHT_BLUE};
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: {TEXT_COLOR};
            }}
        """)
        self.camera_layout = QVBoxLayout(self.camera_panel)
        
        # Camera feed
        self.camera_feed = QLabel()
        self.camera_feed.setAlignment(Qt.AlignCenter)
        self.camera_feed.setMinimumSize(800, 600)
        self.camera_feed.setStyleSheet("background-color: #000000; border: 1px solid #3B82F6; border-radius: 5px;")
        self.camera_layout.addWidget(self.camera_feed)
        
        # Camera controls
        self.camera_controls = QWidget()
        self.camera_controls_layout = QHBoxLayout(self.camera_controls)
        self.camera_controls_layout.setContentsMargins(0, 10, 0, 0)
        
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: {BUTTON_TEXT};
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 5px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BUTTON_PRESSED};
            }}
        """)
        self.capture_button.clicked.connect(self.capture_image)
        self.camera_controls_layout.addWidget(self.capture_button)
        
        self.camera_layout.addWidget(self.camera_controls)
        self.main_layout.addWidget(self.camera_panel, 2)
    
    def setup_control_panel(self):
        """Set up the control panel with all control widgets."""
        self.control_panel = QWidget()
        self.control_panel_layout = QVBoxLayout(self.control_panel)
        
        # Navigation controls
        self.setup_navigation_controls()
        
        # Temperature widget
        self.setup_temperature_widget()
        
        # Speed controls
        self.setup_speed_controls()
        
        # Instructions
        self.setup_instructions()
        
        self.main_layout.addWidget(self.control_panel, 1)
    
    def setup_navigation_controls(self):
        """Set up navigation control buttons."""
        self.nav_group = QGroupBox("Navigation Controls")
        self.nav_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {LIGHT_BLUE};
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: {TEXT_COLOR};
            }}
        """)
        
        self.nav_layout = QGridLayout(self.nav_group)
        
        # Button style
        button_style = f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: {BUTTON_TEXT};
                font-weight: bold;
                padding: 15px;
                border: none;
                border-radius: 5px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BUTTON_PRESSED};
            }}
        """
        
    # Create navigation buttons
        self.btn_forward = QPushButton("Forward")
        self.btn_forward.setFocusPolicy(Qt.NoFocus)  # Add this line
        self.btn_forward.setStyleSheet(button_style)
        self.btn_forward.pressed.connect(self.move_forward)
        self.btn_forward.released.connect(self.stop)
        
        self.btn_up = QPushButton("Up")
        self.btn_up.setFocusPolicy(Qt.NoFocus)  # Add this line
        self.btn_up.setStyleSheet(button_style)
        self.btn_up.pressed.connect(self.move_up)
        self.btn_up.released.connect(self.stop)
        
        self.btn_left = QPushButton("Left")
        self.btn_left.setFocusPolicy(Qt.NoFocus)  # Add this line
        self.btn_left.setStyleSheet(button_style)
        self.btn_left.pressed.connect(self.move_left)
        self.btn_left.released.connect(self.stop)
        
        self.btn_right = QPushButton("Right")
        self.btn_right.setFocusPolicy(Qt.NoFocus)  # Add this line
        self.btn_right.setStyleSheet(button_style)
        self.btn_right.pressed.connect(self.move_right)
        self.btn_right.released.connect(self.stop)
        
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setFocusPolicy(Qt.NoFocus)  # Add this line
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background-color: {WARNING_COLOR};
                color: {BUTTON_TEXT};
                font-weight: bold;
                padding: 15px;
                border: none;
                border-radius: 5px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:pressed {{
                background-color: #B91C1C;
            }}
        """)
        self.btn_stop.clicked.connect(self.stop)
        
        # Add buttons to grid
        self.nav_layout.addWidget(QWidget(), 0, 0)
        self.nav_layout.addWidget(self.btn_forward, 0, 1)
        self.nav_layout.addWidget(QWidget(), 0, 2)
        self.nav_layout.addWidget(self.btn_left, 1, 0)
        self.nav_layout.addWidget(self.btn_stop, 1, 1)
        self.nav_layout.addWidget(self.btn_right, 1, 2)
        self.nav_layout.addWidget(QWidget(), 2, 0)
        self.nav_layout.addWidget(self.btn_up, 2, 1)
        self.nav_layout.addWidget(QWidget(), 2, 2)
        
        self.control_panel_layout.addWidget(self.nav_group)
    
    def setup_temperature_widget(self):
        """Set up temperature display and control widgets."""
        self.temp_group = QGroupBox("Temperature Monitor")
        self.temp_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {LIGHT_BLUE};
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: {TEXT_COLOR};
            }}
        """)
        
        self.temp_layout = QVBoxLayout(self.temp_group)
        
        # Temperature display
        self.temp_display = QLabel("Measuring temperature...")
        self.temp_display.setAlignment(Qt.AlignCenter)
        self.temp_display.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {ACCENT_COLOR};
            padding: 10px;
            background-color: {DARK_BLUE};
            border-radius: 5px;
        """)
        self.temp_layout.addWidget(self.temp_display)
        
        # Temperature log button
        self.btn_log_temp = QPushButton("Log Temperature Data")
        self.btn_log_temp.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_COLOR};
                color: {BUTTON_TEXT};
                font-weight: bold;
                padding: 12px;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {BUTTON_PRESSED};
            }}
        """)
        self.btn_log_temp.clicked.connect(self.save_current_temperature)
        self.temp_layout.addWidget(self.btn_log_temp)
        
        self.control_panel_layout.addWidget(self.temp_group)
    
    def setup_speed_controls(self):
        """Set up motor speed control slider."""
        self.speed_group = QGroupBox("Motor Speed Control")
        self.speed_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {LIGHT_BLUE};
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: {TEXT_COLOR};
            }}
        """)
        
        self.speed_layout = QVBoxLayout(self.speed_group)
        
        # Speed slider
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setFocusPolicy(Qt.NoFocus) 
        self.speed_slider.setRange(800, 1800)
        self.speed_slider.setValue(current_speed)
        self.speed_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {DARK_BLUE};
                height: 10px;
                border-radius: 5px;
            }}
            QSlider::handle:horizontal {{
                background: {LIGHT_BLUE};
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }}
            QSlider::sub-page:horizontal {{
                background: {SLIDER_COLOR};
                border-radius: 5px;
            }}
        """)
        self.speed_slider.valueChanged.connect(self.update_speed)
        self.speed_layout.addWidget(self.speed_slider)
        
        self.control_panel_layout.addWidget(self.speed_group)

    def setup_instructions(self):
        """Set up control instructions panel."""
        self.instructions_group = QGroupBox("Controls")
        self.instructions_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {LIGHT_BLUE};
                border-radius: 8px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: {TEXT_COLOR};
            }}
        """)
        
        self.instructions_layout = QVBoxLayout(self.instructions_group)
        
        instructions = [
            "Up Arrow: Move Forward",
            "Down Arrow: Move Up",
            "Left Arrow: Turn Left",
            "Right Arrow: Turn Right",
            "Space: Emergency Stop"
        ]
        
        for text in instructions:
            label = QLabel(text)
            label.setStyleSheet(f"font-size: 13px; color: {TEXT_COLOR}; padding: 5px;")
            self.instructions_layout.addWidget(label)
        
        self.control_panel_layout.addWidget(self.instructions_group)

    @pyqtSlot()
    def update_camera_feed(self):
        """Update the camera feed display."""
        try:
            frame = self.picam2.capture_array()
            # Mirror the frame horizontally
            frame = cv2.flip(frame, 1)  # 1 means horizontal flip
            img = QImage(frame, frame.shape[1], frame.shape[0], 
                       QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(img)
            self.camera_feed.setPixmap(pixmap.scaled(
                self.camera_feed.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        except Exception as e:
            self.status_bar.showMessage(f"Camera error: {str(e)}")

    def eventFilter(self, source, event):
        """Handle key press events for robot control."""
        
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_Up:
                self.key_pressed["Up"] = True
                self.btn_forward.setDown(True)
                self.btn_forward.repaint()
                self.move_forward()
                return True  # Always return True to consume the event
                
            elif event.key() == Qt.Key_Down:
                self.key_pressed["Down"] = True
                self.btn_up.setDown(True)
                self.btn_up.repaint()
                self.move_up()
                return True
                
            elif event.key() == Qt.Key_Left:
                self.key_pressed["Left"] = True
                self.btn_left.setDown(True)
                self.btn_left.repaint()
                self.move_left()
                return True
                
            elif event.key() == Qt.Key_Right:
                self.key_pressed["Right"] = True
                self.btn_right.setDown(True)
                self.btn_right.repaint()
                self.move_right()
                return True
                
            elif event.key() == Qt.Key_Space:
                self.key_pressed["Space"] = True
                self.stop()
                return True

        elif event.type() == event.KeyRelease:
            if event.key() == Qt.Key_Up:
                self.key_pressed["Up"] = False
                self.btn_forward.setDown(False)
                self.btn_forward.repaint()
                self.stop()
                return True
                
            elif event.key() == Qt.Key_Down:
                self.key_pressed["Down"] = False
                self.btn_up.setDown(False)
                self.btn_up.repaint()
                self.stop()
                return True
                
            elif event.key() == Qt.Key_Left:
                self.key_pressed["Left"] = False
                self.btn_left.setDown(False)
                self.btn_left.repaint()
                self.stop()
                return True
                
            elif event.key() == Qt.Key_Right:
                self.key_pressed["Right"] = False
                self.btn_right.setDown(False)
                self.btn_right.repaint()
                self.stop()
                return True
                
            elif event.key() == Qt.Key_Space:
                self.key_pressed["Space"] = False
                return True

        # For other event types, call the base class implementation
        return super().eventFilter(source, event)

    def capture_image(self):
        """Capture and save image from camera."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            photo_path = f"{PHOTO_DIR}photo_{timestamp}.jpg"
            self.picam2.capture_file(photo_path)
            self.status_bar.showMessage(f"Image saved: {photo_path}")
        except Exception as e:
            self.status_bar.showMessage(f"Capture error: {str(e)}")

    def set_motor_speed(self, pin, pulse_width):
        """Set speed for a specific motor."""
        pi.set_servo_pulsewidth(pin, pulse_width if not is_obstacle_detected else 800)

    def set_all_motors(self, speed):
        """Set all motors to the same speed."""
        for pin in MOTOR_PINS:
            self.set_motor_speed(pin, speed)

    def stop(self):
        """Stop all motors."""
        self.set_all_motors(800)
        self.status_bar.showMessage("All motors stopped")

    def move_forward(self):
        """Move the robot forward."""
        self.set_motor_speed(MOTOR_PINS[0], current_speed)
        self.set_motor_speed(MOTOR_PINS[2], current_speed)
        self.status_bar.showMessage("Moving Forward")

    def move_up(self):
        """Move the robot upward."""
        self.set_motor_speed(MOTOR_PINS[1], current_speed)
        self.set_motor_speed(MOTOR_PINS[3], current_speed)
        self.status_bar.showMessage("Ascending")

    def move_left(self):
        """Turn the robot left."""
        self.set_motor_speed(MOTOR_PINS[2], current_speed)
        self.status_bar.showMessage("Turning Left")

    def move_right(self):
        """Turn the robot right."""
        self.set_motor_speed(MOTOR_PINS[0], current_speed)
        self.status_bar.showMessage("Turning Right")

    def update_speed(self, value):
        """Update motor speed."""
        global current_speed
        current_speed = value
        self.status_bar.showMessage(f"Motor speed set to {current_speed}")

    def temperature_update_loop(self):
        """Continuously update temperature readings."""
        while True:
            temp_c, temp_f = self.read_temp()
            if temp_c is not None:
                self.current_temp_c = temp_c
                self.current_temp_f = temp_f
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.temp_data.append([timestamp, f"{temp_c:.2f}", f"{temp_f:.2f}"])
                self.temp_display.setText(f"{temp_c:.1f}°C / {temp_f:.1f}°F")
                
                if len(self.temp_data) >= MEASUREMENT_LIMIT:
                    self.save_temperature(self.temp_data)
                    self.temp_data = []
            
            time.sleep(2)

    def save_temperature(self, temp_data):
        """Save temperature data to CSV."""
        try:
            write_header = not os.path.exists(TEMP_LOG_PATH)
            with open(TEMP_LOG_PATH, 'a', newline='') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["Timestamp", "Temperature (°C)", "Temperature (°F)"])
                writer.writerows(temp_data)
            self.status_bar.showMessage(f"Temperature data saved to {TEMP_LOG_PATH}")
        except Exception as e:
            self.status_bar.showMessage(f"Error saving temperature data: {str(e)}")

    def save_current_temperature(self):
        """Manually save current temperature reading."""
        if self.temp_data:
            self.save_temperature(self.temp_data)
            self.temp_data = []
            self.status_bar.showMessage("Temperature data manually saved")
        else:
            self.status_bar.showMessage("No temperature data to save")

    def closeEvent(self, event):
        """Handle window close event."""
        try:
            self.picam2.stop()
            self.stop()
            pi.stop()
        except Exception as e:
            logging.error(f"Error during shutdown: {str(e)}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotControlUI()
    window.setFocus()  # Set focus to window when starting
    window.show()
    sys.exit(app.exec_())