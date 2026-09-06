"""
perception.py
-------------
Turns a raw video frame into the small "perception_state" dict that
step_engine.py consumes:

    {
        "objects_visible": ["tube", "rack"],
        "hand_near": "tube",
        "raw_objects": [...],
        "hand_points": [(x, y), ...]
    }

IMPORTANT - process isolation:
YOLO (PyTorch) and MediaPipe each run in their OWN separate OS process
(see workers.py). This process never imports torch or mediapipe itself -
it only talks to the two worker processes over multiprocessing.Queue.
This is deliberate: running both libraries' native code in a single
process caused unrecoverable crashes on Windows (PyTorch's and
MediaPipe's native CPU thread pools conflict). Full process isolation
guarantees that can never happen, regardless of machine/driver quirks.

NEAR_THRESHOLD_PX controls how close a hand must be to an object's
bounding box center to count as "interacting with it" - tune this
for your camera distance.
"""

import multiprocessing
import cv2

from src.workers import yolo_worker, hand_worker

NEAR_THRESHOLD_PX = 120


class Perception:
    def __init__(self, yolo_weights: str = "yolov8n.pt", target_classes=None):
        self.yolo_in = multiprocessing.Queue(maxsize=2)
        self.yolo_out = multiprocessing.Queue(maxsize=2)
        self.hand_in = multiprocessing.Queue(maxsize=2)
        self.hand_out = multiprocessing.Queue(maxsize=2)

        self.yolo_proc = multiprocessing.Process(
            target=yolo_worker,
            args=(self.yolo_in, self.yolo_out, yolo_weights, target_classes),
            daemon=True,
        )
        self.hand_proc = multiprocessing.Process(
            target=hand_worker,
            args=(self.hand_in, self.hand_out),
            daemon=True,
        )
        print("[perception] Starting YOLO worker process...")
        self.yolo_proc.start()
        print("[perception] Starting MediaPipe worker process...")
        self.hand_proc.start()

    def process_frame(self, frame_bgr):
        # Send the same frame to both workers, then wait for both replies.
        self.yolo_in.put(frame_bgr)
        self.hand_in.put(frame_bgr)

        objects, annotated = self.yolo_out.get()
        hand_landmark_lists = self.hand_out.get()

        # Use each hand's wrist point (landmark 0) as its anchor for proximity checks
        hand_points = [pts[0] for pts in hand_landmark_lists if pts]

        hand_near = None
        closest_obj = None
        closest_dist = float("inf")
        best_near_dist = float("inf")

        for name, cx, cy, *_ in objects:
            for hx, hy in hand_points:
                dist = ((cx - hx) ** 2 + (cy - hy) ** 2) ** 0.5
                if dist < closest_dist:
                    closest_dist = dist
                    closest_obj = name
                if dist < NEAR_THRESHOLD_PX and dist < best_near_dist:
                    best_near_dist = dist
                    hand_near = name

                # Draw proximity indicator line between hand and object
                color = (0, 255, 0) if dist < NEAR_THRESHOLD_PX else (0, 165, 255)
                cv2.line(annotated, (int(hx), int(hy)), (int(cx), int(cy)), color, 1, cv2.LINE_AA)

        # Draw hand landmarks with plain OpenCV
        for pts in hand_landmark_lists:
            for (x, y) in pts:
                cv2.circle(annotated, (int(x), int(y)), 3, (0, 255, 0), -1)

        # Draw HUD status overlay on annotated frame
        hand_status = "DETECTED" if hand_points else "OUT OF FRAME"
        hand_color = (0, 255, 0) if hand_points else (0, 0, 255)
        cv2.putText(annotated, f"Hand: {hand_status}", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, hand_color, 2, cv2.LINE_AA)

        near_str = hand_near.upper() if hand_near else "NONE"
        cv2.putText(annotated, f"Hand Near: {near_str}", (15, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        perception_state = {
            "objects_visible": [o[0] for o in objects],
            "hand_near": hand_near,
            "raw_objects": objects,
            "hand_points": hand_points,
            "closest_obj": closest_obj,
            "closest_dist": closest_dist if closest_dist != float("inf") else None,
        }
        return perception_state, annotated

    def close(self):
        """Call when shutting down to stop both worker processes cleanly."""
        try:
            self.yolo_in.put(None)
            self.hand_in.put(None)
            self.yolo_proc.join(timeout=2)
            self.hand_proc.join(timeout=2)
        except Exception:
            pass
