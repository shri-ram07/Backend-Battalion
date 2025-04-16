
# ️Automated Power Monitoring System

This project combines real-time computer vision with Arduino-based hardware control to automate appliances based on the detected presence and position of people in a room.

---

## Overview

Using a webcam and the YOLOv3 object detection model, the system detects humans in a live video stream. Based on the detected position, it identifies the nearest corner zone in the room and activates a corresponding Arduino-controlled output (like a relay or LED).

---

## How It Works

1. **YOLOv3** processes the webcam feed to detect people.
2. For each detected person, the bottom-center of the bounding box is computed.
3. This point is compared against 4 predefined room corner coordinates.
4. The closest corner point is determined using Euclidean distance.
5. Each point is linked to a digital pin on an **Arduino** via **pyFirmata**.
6. The Arduino pin corresponding to the nearest corner point is activated, while others are turned off.

---

## Requirements

###  Python Libraries

- `opencv-python`
- `numpy`
- `pyfirmata`

Install using:

```bash
pip install opencv-python numpy pyfirmata
```

###  Files Needed

- `yolov3.cfg`
- `yolov3.weights`
- COCO class labels (optional but helpful)

---

##  Hardware Setup

- **Webcam** (for video feed)
- **Arduino UNO** (connected to PC via USB)
- **Digital output devices** like LEDs or relays connected to pins D13, D12, D11, and D10

>  Make sure to replace `'COM4'` in the script with your actual Arduino COM port.

---

## Arduino Pin Mapping

| Corner Point | Arduino Digital Pin |
|--------------|---------------------|
| Point 1      | D13                 |
| Point 2      | D12                 |
| Point 3      | D11                 |
| Point 4      | D10                 |

---

##  Functionality Breakdown

- **Video Capture**: `cv2.VideoCapture(1)`
- **YOLOv3 Inference**: Run object detection using pre-trained weights
- **Bounding Box Center**: Used to determine person’s relative position
- **Corner Proximity**: Calculate nearest corner using `np.linalg.norm()`
- **Relay Control**: Write to Arduino pins based on detected proximity

---

##  Output Display

- Detected people are shown with bounding boxes.
- Labels display detection confidence and the nearest zone.
- Nearest room corner is marked with a green circle.

---

##  Example Use Cases

- Automating lights or fans based on a person’s location in a room.
- Smart energy saving systems for homes, offices, or labs.
- Room-based activity tracking and ambient response.

---

##  Live Preview

When the system runs, it will display:
- A real-time video feed
- Blue boxes for detected people
- Nearest corner indicator and confidence scores

Press `ESC` to exit the application.

---

