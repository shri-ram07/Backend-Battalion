from ele_consumption_cal import calculate
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QGridLayout, QFrame, QMessageBox, QLineEdit
from PyQt5.QtGui import QImage, QPixmap, QFont, QLinearGradient, QColor, QBrush, QPainter
from PyQt5.QtCore import QTimer, Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import cv2
import numpy as np
from pyfirmata import Arduino
from Automatic_com_port_Detection import find_port
from dela_y import delay
import time

# Set Matplotlib to dark background style
plt.style.use('dark_background')

appliance_states = {
    0: {"state": False, "last_toggle_time": time.time(), "on_duration": 0},  # S1
    1: {"state": False, "last_toggle_time": time.time(), "on_duration": 0},  # S2
    2: {"state": False, "last_toggle_time": time.time(), "on_duration": 0},  # S3
    3: {"state": False, "last_toggle_time": time.time(), "on_duration": 0},  # S4
}

# Initialize Arduino board
board = Arduino(f'{find_port()}')

pins = {
    0: board.get_pin('d:13:o'),
    1: board.get_pin('d:12:o'),
    2: board.get_pin('d:11:o'),
    3: board.get_pin('d:10:o')
}

# Load YOLOv3 model
net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


cap = cv2.VideoCapture(0)

# Default corner points (if user doesn't set them)
DEFAULT_CORNER_POINTS = [(520, 108), (105, 214), (820, 255), (517, 591)]

# Global variables for statistics
total_people = 0
electricity_saved = 0
automatic_mode = True  # Start in Automatic Mode

class GradientBackground(QWidget):
    """Custom widget to draw gradient backgrounds."""
    def __init__(self, color1, color2, parent=None):
        super().__init__(parent)
        self.color1 = color1
        self.color2 = color2

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, self.color1)
        gradient.setColorAt(1.0, self.color2)
        painter.fillRect(event.rect(), QBrush(gradient))

class PowerConsumptionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Power Consumption Calculator")
        self.setGeometry(100, 100, 600, 400)

        # Set gradient background
        self.background = GradientBackground(QColor("#2c3e50"), QColor("#000000"), self)
        self.background.setGeometry(self.rect())

        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.appliance_labels = ["Fans", "Coolers", "ACs", "Light Bulbs"]
        self.entries = {}

        for i, label in enumerate(self.appliance_labels):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 14px; color: #ecf0f1; font-family: 'Roboto', sans-serif;")
            entry = QLineEdit()
            entry.setPlaceholderText(f"Enter {label.lower()} count")
            entry.setStyleSheet("""
                QLineEdit {
                    background-color: #34495e;
                    color: white;
                    border: none;
                    border-bottom: 2px solid #2c3e50;
                    border-radius: 3px;
                    padding: 5px;
                    font-family: 'Roboto', sans-serif;
                }
                QLineEdit:focus {
                    border-bottom: 2px solid #3498db;
                }
            """)
            entry.setToolTip(f"Enter the number of {label.lower()}")
            self.entries[label] = entry
            layout.addWidget(lbl, i, 0)
            layout.addWidget(entry, i, 1)

        self.calculate_button = QPushButton("Calculate Consumption")
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Roboto', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #2980b9, stop: 1 #2471a3);
            }
        """)
        self.calculate_button.setToolTip("Calculate total power consumption")
        self.calculate_button.clicked.connect(self.calculate_consumption)
        layout.addWidget(self.calculate_button, len(self.appliance_labels), 0, 1, 2)

        self.result_label = QLabel("Total Power Consumption: 0 Watts")
        self.result_label.setStyleSheet("""
            font-size: 18px;
            color: #ecf0f1;
            background-color: #34495e;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Roboto', sans-serif;
        """)
        layout.addWidget(self.result_label, len(self.appliance_labels) + 1, 0, 1, 2)

        self.next_button = QPushButton("Next")
        self.next_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #2ecc71, stop: 1 #27ae60);
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Roboto', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #27ae60, stop: 1 #229954);
            }
        """)
        self.next_button.setToolTip("Proceed to setup corner points")
        self.next_button.clicked.connect(self.next_)
        layout.addWidget(self.next_button, len(self.appliance_labels) + 2, 0, 1, 2)

        # Add Matplotlib FigureCanvas for chart display
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, len(self.appliance_labels) + 3, 0, 1, 2)

        self.setLayout(layout)

    def next_(self):
        global consumption_data
        consumption = self.consumption_data
        self.close()
        self.setup = SetupWindow(consumption)
        self.setup.show()

    def calculate_consumption(self):
        try:
            power_ratings = {"Fans": 60, "Coolers": 200, "ACs": 1500, "Light Bulbs": 10}
            total_power = 0
            self.consumption_data = []
            self.consumption_data_ = []
            labels = []

            for appliance, entry in self.entries.items():
                text_value = entry.text().strip()
                if text_value.isdigit():
                    count = int(text_value)
                else:
                    count = 0
                consumption_ = count * power_ratings[appliance]
                consumption = count
                total_power += consumption_
                if count > 0:
                    self.consumption_data.append(consumption)
                    self.consumption_data_.append(consumption_)
                    labels.append(appliance)

            if not labels:
                self.result_label.setText("Please enter valid appliance counts.")
            else:
                self.result_label.setText(f"Total Hourly Consumption: {total_power} Watts")
                self.update_chart(labels, self.consumption_data_)
        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")

    def update_chart(self, labels, data):
        self.ax.clear()
        self.ax.bar(labels, data, color=['#3498db', '#2980b9', '#2471a3', '#1f618d'])
        self.ax.set_ylabel("Power Consumption (Watts)", color='#ecf0f1')
        self.ax.set_title("Appliance Power Usage", color='#ecf0f1')
        self.ax.set_facecolor('#2c3e50')
        self.figure.patch.set_facecolor('#2c3e50')
        self.ax.tick_params(colors='#ecf0f1')
        self.canvas.draw()

class SetupWindow(QWidget):
    def __init__(self, consumption_data):
        super().__init__()
        self.setWindowTitle("Setup Corner Points")
        self.setGeometry(100, 100, 800, 600)
        self.consumption_data = consumption_data
        self.cons_ = calculate(self.consumption_data[0], self.consumption_data[1], self.consumption_data[2], self.consumption_data[3])

        # Set gradient background
        self.background = GradientBackground(QColor("#2c3e50"), QColor("#000000"), self)
        self.background.setGeometry(self.rect())

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Video Feed Section
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border-radius: 10px;
                border: 2px solid #3498db;
                box-shadow: 0px 0px 10px #3498db;
            }
        """)
        self.layout.addWidget(self.video_label)

        # Instructions Label
        self.instructions_label = QLabel("Click on the video feed to set the 4 corner points.", self)
        self.instructions_label.setStyleSheet("""
            font-size: 18px;
            color: #ecf0f1;
            font-weight: bold;
            font-family: 'Roboto', sans-serif;
            background-color: rgba(52, 73, 94, 0.8);
            padding: 10px;
            border-radius: 5px;
        """)
        self.instructions_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.instructions_label)

        # Save Button
        self.save_button = QPushButton("Save and Proceed", self)
        self.save_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Roboto', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #2980b9, stop: 1 #2471a3);
            }
        """)
        self.save_button.setToolTip("Save corner points and proceed to main window")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_and_proceed)
        self.layout.addWidget(self.save_button)

        # Timer for video feed updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(30)

        # Variables for point selection
        self.corner_points = []
        self.click_count = 0

    def update_video_feed(self):
        success, image = cap.read()
        if not success:
            return

        # Draw existing points on the video feed
        for point in self.corner_points:
            cv2.circle(image, point, 15, (0, 255, 0), -1)

        # Convert image to PyQt-compatible format
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def mousePressEvent(self, event):
        if len(self.corner_points) < 4:
            x, y = event.pos().x() - self.video_label.pos().x(), event.pos().y() - self.video_label.pos().y()
            video_width = self.video_label.width()
            video_height = self.video_label.height()
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            mapped_x = int(x / video_width * frame_width)
            mapped_y = int(y / video_height * frame_height)
            self.corner_points.append((mapped_x, mapped_y))
            self.click_count += 1
            self.instructions_label.setText(f"Point {self.click_count} of 4 set")
            if self.click_count == 4:
                self.save_button.setEnabled(True)
                self.instructions_label.setText("All 4 points set! Click 'Save and Proceed'.")

    def save_and_proceed(self):
        global corner_points, cons_
        corner_points = self.corner_points
        cons_ = self.cons_
        self.close()
        self.main_window = MainWindow(corner_points, cons_)
        self.main_window.show()

class MainWindow(QMainWindow):
    def __init__(self, corner_points, cons_):
        super().__init__()
        self.setWindowTitle("Smart Room Monitoring")
        self.setGeometry(100, 100, 1200, 800)
        self.cons_ = cons_

        # Set gradient background
        self.central_widget = GradientBackground(QColor("#2c3e50"), QColor("#000000"))
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Video Feed Section
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border-radius: 10px;
                border: 2px solid #3498db;
                box-shadow: 0px 0px 10px #3498db;
            }
        """)
        self.layout.addWidget(self.video_label, 0, 0, 1, 2)

        # Mode Toggle Section
        self.mode_toggle_frame = QFrame(self)
        self.mode_toggle_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.mode_toggle_layout = QVBoxLayout(self.mode_toggle_frame)

        self.mode_toggle_button = QPushButton("Switch to Manual Mode", self)
        self.mode_toggle_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Roboto', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #2980b9, stop: 1 #2471a3);
            }
        """)
        self.mode_toggle_button.setToolTip("Toggle between Automatic and Manual Mode")
        self.mode_toggle_button.clicked.connect(self.toggle_mode)
        self.mode_toggle_layout.addWidget(self.mode_toggle_button)
        self.layout.addWidget(self.mode_toggle_frame, 1, 0)

        # Manual Switch Controller Section
        self.switch_frame = QFrame(self)
        self.switch_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.switch_layout = QVBoxLayout(self.switch_frame)
        self.switch_buttons = []

        for i in range(4):
            btn = QPushButton(f"Switch {i+1} (OFF)", self)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, i=i: self.toggle_manual_switch(i))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 15px;
                    min-width: 60px;
                    font-family: 'Roboto', sans-serif;
                }
                QPushButton:checked {
                    background-color: #2ecc71;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:checked:hover {
                    background-color: #27ae60;
                }
            """)
            btn.setToolTip(f"Toggle Switch {i+1}")
            btn.setEnabled(False)
            self.switch_layout.addWidget(btn)
            self.switch_buttons.append(btn)
        self.layout.addWidget(self.switch_frame, 1, 1)

        # Statistics Section
        self.stats_label = QLabel("Total People: 0\nElectricity Saved: 0 kWh\nAppliances Count: 0", self)
        self.stats_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #ecf0f1;
                background-color: #34495e;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Roboto', sans-serif;
            }
        """)
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.stats_label, 2, 0, 1, 2)

        # Timer for video feed updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(30)

        # Global variables
        self.total_people = 0
        self.electricity_saved = 0
        self.corner_points = corner_points

    def toggle_mode(self):
        global automatic_mode
        automatic_mode = not automatic_mode
        if automatic_mode:
            self.mode_toggle_button.setText("Switch to Manual Mode")
            for btn in self.switch_buttons:
                btn.setEnabled(False)
        else:
            self.mode_toggle_button.setText("Switch to Automatic Mode")
            for btn in self.switch_buttons:
                btn.setEnabled(True)

    def toggle_manual_switch(self, switch_id):
        global appliance_states
        current_state = pins[switch_id].read()
        new_state = 1 if current_state == 0 else 0
        pins[switch_id].write(new_state)

        # Update appliance state and calculate ON duration
        now = time.time()
        if appliance_states[switch_id]["state"]:
            appliance_states[switch_id]["on_duration"] += now - appliance_states[switch_id]["last_toggle_time"]
        appliance_states[switch_id]["state"] = not appliance_states[switch_id]["state"]
        appliance_states[switch_id]["last_toggle_time"] = now
        self.switch_buttons[switch_id].setText(f"Switch {switch_id+1} ({'ON' if new_state else 'OFF'})")

    def update_video_feed(self):
        global total_people, electricity_saved, automatic_mode, appliance_states
        success, image = cap.read()
        if not success:
            return

        small_image = cv2.resize(image, (608, 608))
        blob = cv2.dnn.blobFromImage(small_image, 1/255.0, (608, 608), swapRB=True, crop=False)
        net.setInput(blob)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        detections = net.forward(output_layers)

        height, width, _ = image.shape
        boxes = []
        confidences = []
        class_ids = []

        for detection in detections:
            for obj in detection:
                scores = obj[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if class_id == 0 and confidence > 0.5:  # Class 0 is 'person'
                    box = obj[0:4] * np.array([width, height, width, height])
                    (x_center, y_center, w, h) = box.astype("int")
                    x_min = int(x_center - (w / 2))
                    y_min = int(y_center - (h / 2))
                    boxes.append([x_min, y_min, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        nearest_points = set()

        if len(indices) > 0:
            for i in indices.flatten():
                box = boxes[i]
                x_min, y_min, w, h = box
                x_max = x_min + w
                y_max = y_min + h
                x_center = (x_min + x_max) // 2
                y_center = (y_min + y_max) // 2

                distances = [np.linalg.norm(np.array([x_center, y_center]) - np.array(point)) for point in self.corner_points]
                nearest_point_index = np.argmin(distances)
                nearest_points.add(nearest_point_index)

                # Draw bounding box and label
                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (52, 152, 219), 2)  # #3498db in BGR
                cv2.putText(image, f'Person {confidences[i]:.2f}', (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (52, 152, 219), 2)
                cv2.putText(image, f'Nearest Point: {nearest_point_index + 1}', (x_min, y_min - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (46, 204, 113), 2)
                cv2.circle(image, self.corner_points[nearest_point_index], 10, (46, 204, 113), -1)

            self.total_people = len(indices)

        # Control appliances based on mode
        if automatic_mode:
            for i in range(4):
                if i in nearest_points:
                    new_state = 0
                else:
                    delay(15000)
                    new_state = 1
                pins[i].write(new_state)

                # Update appliance state and calculate ON duration
                now = time.time()
                if appliance_states[i]["state"]:
                    appliance_states[i]["on_duration"] += now - appliance_states[i]["last_toggle_time"]
                appliance_states[i]["state"] = new_state == 0
                appliance_states[i]["last_toggle_time"] = now

        # Convert image to PyQt-compatible format
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

        # Update statistics labels
        total_on_hours = sum(state["on_duration"] / 3600 for state in appliance_states.values())
        self.electricity_saved = total_on_hours * self.cons_
        self.stats_label.setText(
            f"Total People: {self.total_people}\n"
            f"Electricity Consumed: {round(self.electricity_saved, 2)} kWh\n"
            f"Total Appliances Active Time: {round(total_on_hours, 2)} hours"
        )