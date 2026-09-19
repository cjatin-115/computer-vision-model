"""
streamer.py
-----------
- Streams the annotated video feed over HTTP (MJPEG) so a remote
  viewer at http://<this-machine-ip>:5000/video can watch, without
  needing a full video call stack.
- Simultaneously writes the feed to a local .mp4 file, so nothing is
  lost even if the network link drops (matches the low-bandwidth,
  store-locally requirement in the PS).

Run this file's `start_server()` in a background thread from main.py.
"""

import threading
import time
import cv2
from flask import Flask, Response
from datetime import datetime
import os

app = Flask(__name__)
_latest_frame = None
_lock = threading.Lock()


def update_frame(frame_bgr):
    """Call this every loop iteration with the latest annotated frame."""
    global _latest_frame
    with _lock:
        _latest_frame = frame_bgr.copy()


def _mjpeg_generator():
    while True:
        with _lock:
            frame = _latest_frame.copy() if _latest_frame is not None else None
        if frame is None:
            time.sleep(0.05)
            continue
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        jpg_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpg_bytes + b"\r\n")


@app.route("/video")
def video_feed():
    return Response(_mjpeg_generator(),
                     mimetype="multipart/x-mixed-replace; boundary=frame")


def start_server(host="0.0.0.0", port=5000):
    """Blocking call - run in a background thread from main.py:
        threading.Thread(target=streamer.start_server, daemon=True).start()
    """
    app.run(host=host, port=port, threaded=True, use_reloader=False)


class LocalRecorder:
    """Writes frames to a timestamped local .mp4 as a backup / archive."""

    def __init__(self, output_dir="recordings", fps=20, frame_size=(640, 480)):
        os.makedirs(output_dir, exist_ok=True)
        filename = datetime.now().strftime("experiment_%Y%m%d_%H%M%S.mp4")
        path = os.path.join(output_dir, filename)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(path, fourcc, fps, frame_size)
        self.path = path

    def write(self, frame_bgr):
        self.writer.write(frame_bgr)

    def release(self):
        self.writer.release()
