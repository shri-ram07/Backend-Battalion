import cv2
import numpy as np
from pyfirmata import Arduino, util
import sys



board = Arduino("COM4")  # Update with your Arduino port

# Define the digital pins for each point
pins = {
    0: board.get_pin('d:7:o'),  # Point 0.1
    1: board.get_pin('d:13:o'),  # Point 0.2
    2: board.get_pin('d:11:o'),  # Point 0.3
    3: board.get_pin('d:10:o')   # Point 0.4
}

# Function to turn on switches based on detected points
def turn_on_switches(nearest_points):
    for i in range(4):
        pins[i].write(0 if i in nearest_points else 1)

# Load YOLOv3 model
net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)  # Change to DNN_TARGET_CUDA if you have a GPU

# Define the four corner points (assuming a 640x480 resolution for simplicity)
corner_points = [
    (520, 108),        # Top-left corner
    (105, 214),         # Top-right corner
    (820, 255),       # Bottom-left corner
    (517, 591)         # Bottom-right corner
]

# Open video capture
cap = cv2.VideoCapture(0)
while cap.isOpened():
    _, image = cap.read()
    if not _:
        break

    # Reduce the input size for faster processing
    small_image = cv2.resize(image, (320, 320))

    # Prepare the image for YOLO
    blob = cv2.dnn.blobFromImage(small_image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    detections = net.forward(output_layers)

    # Get the dimensions of the image
    height, width, _ = image.shape

    boxes = []
    confidences = []
    class_ids = []

    # Draw body detections and determine the nearest corner point
    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if class_id == 0 and confidence > 0.5:  # Class 0 is 'person' in COCO dataset
                box = obj[0:4] * np.array([width, height, width, height])
                (x_center, y_center, w, h) = box.astype("int")
                x_min = int(x_center - (w / 2))
                y_min = int(y_center - (h / 2))
                x_max = x_min + w
                y_max = y_min + h

                boxes.append([x_min, y_min, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply Non-Maximum Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    nearest_points = set()

    if len(indices) > 0:
        for i in indices.flatten():
            box = boxes[i]
            x_min, y_min, w, h = box
            x_max = x_min + w
            y_max = y_min + h

            # Calculate the center of the bounding box
            x_center = (x_min + x_max) // 2
            y_center = (y_max)

            # Calculate distances to each corner point
            distances = [np.linalg.norm(np.array([x_center, y_center]) - np.array(point)) for point in corner_points]

            # Find the nearest corner point
            nearest_point_index = np.argmin(distances)
            nearest_point = corner_points[nearest_point_index]

            # Add the nearest point index to the set
            nearest_points.add(nearest_point_index)

            # Display the nearest corner point on the image
            label = f'Person {confidences[i]:.2f}'
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
            cv2.putText(image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            cv2.putText(image, f'Nearest Point: {nearest_point_index + 1}', (x_min, y_min - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.circle(image, nearest_point, 10, (0, 255, 0), -1)

    # Turn on the switches based on the nearest points
    turn_on_switches(nearest_points)

    # Display the image
    cv2.imshow('YOLOv3 Body Detection with Nearest Corner Point', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()