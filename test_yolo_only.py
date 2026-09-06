"""
test_yolo_only.py
------------------
Tests ONLY YOLOv8 inference on one webcam frame. No mediapipe, no GUI.
If this crashes silently, YOLO/PyTorch itself is the problem on this machine.
"""
import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import platform
import cv2

print("[1] Opening camera...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if platform.system() == "Windows" else cv2.VideoCapture(0)
ok, frame = cap.read()
cap.release()
if not ok:
    print("FAILED: could not read a frame.")
    raise SystemExit(1)
print("[2] Frame captured. Loading YOLO model (this may download yolov8n.pt)...")

from ultralytics import YOLO
model = YOLO("yolov8n.pt")
print("[3] Model loaded. Running inference...")

results = model(frame, verbose=False)[0]
print("[4] Inference finished OK. Detections:", len(results.boxes))
print("SUCCESS: YOLO works fine on this machine.")
