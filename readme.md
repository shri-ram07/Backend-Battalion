
# 🔌 Automated Power Monitoring System  – Backend Battalion

## 📌 Problem Statement

Energy wastage is a common problem in households and offices, primarily caused by unattended appliances running in unoccupied rooms. Manual appliance control is inconvenient and often neglected, and the absence of real-time monitoring leads to inefficiencies. This results in higher electricity bills and environmental harm.

> 💡 **Key Insight**: Current systems lack automation and real-time feedback, making energy usage inefficient and unsustainable.

---

## 🚀 Proposed Solution

We present a **Automated Power Monitoring System** that automates appliance control using real-time computer vision and IoT hardware. The system utilizes **YOLOv3** for detecting the presence of people and automatically turns on/off appliances (lights, fans, etc.) via an **Arduino**.

### ✅ Key Features

- 👁️‍🗨️ Real-time automated monitoring with a webcam
- ⚙️ Automatic and Manual operation modes
- 🧠 YOLOv3-based people detection
- 🔌 Appliance control via Arduino and relays
- 📊 Electricity savings and live stats display
- 🔌 Auto-detects COM ports
- 🔲 Flexible room area setup using customizable corner points

---

## 🧰 Tech Stack

| Component      | Technology Used      |
| -------------- | -------------------- |
| 🧠 AI Model    | YOLOv3 (Real-time Object Detection) |
| 🎥 Video Processing | OpenCV |
| 🖥️ GUI         | PyQt (Desktop Interface) |
| 🤖 Hardware Control | PyFirmata + Arduino UNO + Relays |
| 💻 Hardware     | Webcam, Arduino, Electrical Relays |

---

## ⚡ Impact & Benefits

### 🌍 Environmental Impact

- Reduces unnecessary energy usage
- Contributes to SDG 7 (Affordable and Clean Energy)

### 💸 Economic Impact

- Cuts down electricity bills
- Supports SDG 12 (Responsible Consumption and Production)

### 🧑‍🤝‍🧑 Social Benefits

- Increases user convenience
- Promotes automation in everyday life
- Supports SDG 9 (Industry, Innovation, and Infrastructure)

### 📈 Scalability

- Adaptable to homes, offices, schools, and commercial spaces

---

## 🔮 Future Enhancements

- ☁️ Cloud-based data monitoring and analytics
- 📱 Mobile app support for remote control
- 🌡️ Sensor integration (temperature, humidity)
- 🧠 Improved AI models for better accuracy

---

## 🧪 How It Works

1. Webcam captures live feed
2. YOLOv3 processes frames to detect humans
3. PyQt GUI shows real-time stats and modes
4. Arduino receives signals via PyFirmata
5. Appliances are automatically controlled based on occupancy

---


![img.png](img.png)


## 📁 Project Structure

```
smart-room-monitoring/
├──                  
├──                  
├──               
├── 
├── 
└── README.md
```

---

## 🎯 Conclusion

The Smart Room Monitoring System showcases how the integration of AI and IoT can solve real-world challenges. It brings sustainability, efficiency, and innovation together — one smart room at a time.

> 🌱 **Join us in building smarter, greener spaces.**

---

## 🤝 Team - Backend Battalion

- 🧠 Ideation & AI: [Shri Ram Dwivedi]
- 💡 Hardware & Integration: [Amaya Kumar Sahu]
- 💻 UI/UX & Software: [Surya Kumar Srivastave & Ananya Shahi]
