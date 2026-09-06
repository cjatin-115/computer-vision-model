"""
test_mediapipe_only.py
-----------------------
Tests ONLY MediaPipe Hands on one webcam frame. No YOLO/torch, no GUI.
If this crashes silently, MediaPipe itself is the problem on this machine.
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
print("[2] Frame captured. Loading MediaPipe Hands...")

import mediapipe as mp
hands = mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5)
print("[3] Model loaded. Running inference...")

rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
result = hands.process(rgb)
print("[4] Inference finished OK. Hands found:", 0 if not result.multi_hand_landmarks else len(result.multi_hand_landmarks))
print("SUCCESS: MediaPipe works fine on this machine.")
