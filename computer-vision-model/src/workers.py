"""
workers.py
----------
Each function here is the entry point for its OWN separate OS process
(started via multiprocessing.Process). This is the fix for the
PyTorch + MediaPipe native crash: as long as torch and mediapipe are
never imported into the *same* process, they cannot conflict with
each other's native thread pools/DLLs.

Communication is via multiprocessing.Queue: the main process puts a raw
frame in, the worker puts its result back. Send `None` to stop a worker.
"""
import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")


def yolo_worker(in_queue, out_queue, weights_path, target_classes):
    """Runs in its own process. Only this process ever imports torch/ultralytics."""
    import torch
    torch.set_num_threads(1)
    from ultralytics import YOLO

    model = YOLO(weights_path)

    while True:
        frame = in_queue.get()
        if frame is None:
            break
        results = model(frame, verbose=False)[0]
        objects = []  # (name, cx, cy, x1, y1, x2, y2)
        for box in results.boxes:
            cls_id = int(box.cls[0])
            name = model.names[cls_id]
            if target_classes and name not in target_classes:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            objects.append((name, cx, cy, x1, y1, x2, y2))
        annotated = results.plot()  # plain numpy array - safe to send through the queue
        out_queue.put((objects, annotated))


def hand_worker(in_queue, out_queue):
    """Runs in its own process. Only this process ever imports mediapipe."""
    import cv2
    import mediapipe as mp

    hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )

    while True:
        frame = in_queue.get()
        if frame is None:
            break
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        hand_landmark_lists = []  # one list of 21 (x_px, y_px) points per detected hand
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                pts = [(lm.x * w, lm.y * h) for lm in hand_landmarks.landmark]
                hand_landmark_lists.append(pts)
        out_queue.put(hand_landmark_lists)
