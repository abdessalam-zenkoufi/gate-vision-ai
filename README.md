# Gate Vision AI 🛡️👁️

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-blue)](https://github.com/TomSchimansky/CustomTkinter)
[![Computer Vision](https://img.shields.io/badge/Vision-OpenCV-green)](https://opencv.org/)
[![Face Recognition](https://img.shields.io/badge/Model-dlib_ResNet-orange)](https://github.com/ageitgey/face_recognition)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent access control and surveillance desktop workstation featuring real-time biometric face verification, multi-filter edge detection analytics, and real-time security gate simulation.

---

## ⚡ Key Capabilities

### 1. Biometric Authentication & Verification
* Real-time face detection and 128-d facial embedding extraction utilizing deep metric learning (dlib ResNet backbone).
* Dual-tier authorization routing: Instant identification for authorized profiles vs. immediate blacklist alert triggers.
* Audio-visual alarm integration via Pygame for unauthorized or blacklisted intrusions.

### 2. Multi-Spectral Edge Detection Pipeline
For every access attempt, facial regions are isolated, normalized, and processed through multiple edge-detection kernels:
* **Sobel Gradient Operator:** Computes directional horizontal and vertical gradient magnitude approximations.
* **Canny Edge Detector:** Multi-stage optimal edge isolation via Gaussian smoothing, non-maximum suppression, and hysteresis thresholding.
* **Laplacian Operator:** Second-order isotropic spatial derivative highlighting high-frequency structural contours.

### 3. Integrated Audit Logging
* Automated telemetry logging linking identity timestamps, verification verdicts, and structural feature extractions into a persistent audit trail.

---

## 📊 Pipeline Overview

* Step 1 (Frame Capture): Live video stream capture with multi-encoding fallback.
* Step 2 (Biometric Inference): Face localization -> ResNet 128-d embedding -> Distance metric comparison.
* Step 3 (Decision Matrix): Allowed (Gate Open) | Banned (Alarm Trigger) | Unknown (Restricted).
* Step 4 (Feature Extraction): Crop ROI -> Generate Sobel, Canny, and Laplacian maps -> Persist audit entry.

---

## 🛠️ Tech Stack

* Language: Python 3.10+
* Interface: CustomTkinter
* Computer Vision: OpenCV (cv2), face_recognition, dlib, Pillow
* Audio Alerts: Pygame Mixer
* Storage: CSV Audit Logger with UTF-8 byte-buffer image serialization

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.10 or higher.
* CMake (required for building `dlib`).
* A functional webcam/camera device.

### 1. Clone Repository
git clone https://github.com/abdessalam-zenkoufi/gate-vision-ai.git
cd gate-vision-ai

### 2. Create Virtual Environment
Windows:
python -m venv venv
venv\Scripts\activate

Linux / macOS:
python3 -m venv venv
source venv/bin/activate

### 3. Install Requirements
pip install -r requirements.txt

---

## 🖥️ Running the Application

python main_app.py

---

## 📁 Repository Structure

gate-vision-ai/
├── assets/                  # UI gate graphics and alarm audio
│   ├── gate_closed.jpg
│   ├── gate_opened.jpg
│   └── alarm.wav
├── students_data/           # Biometric database
│   ├── allowed/
│   └── banned/
├── logs/                    # Audit logs and edge filter records
│   ├── images/
│   └── access_logs.csv
├── main_app.py              # Application core and orchestration logic
├── requirements.txt         # Dependency manifest
├── .gitignore               # Excludes sensitive images and audit data
├── LICENSE                  # MIT Open-Source License
└── README.md                # System documentation

---

## 📄 License
Distributed under the MIT License. See LICENSE for more information.