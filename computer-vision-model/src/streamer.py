"""
streamer.py
-----------
Provides:

1. MJPEG live video stream at /video
2. Flask API routes for the React dashboard
3. Local MP4 recording
"""

import threading
import time
import cv2
from flask import Flask, Response
from datetime import datetime
import os

from src.api import register_api


app = Flask(__name__)

_latest_frame = None
_lock = threading.Lock()


def update_frame(frame_bgr):
    """Update the latest frame used by the MJPEG stream."""

    global _latest_frame

    with _lock:
        _latest_frame = frame_bgr.copy()


def _mjpeg_generator():

    while True:

        with _lock:

            frame = (
                _latest_frame.copy()
                if _latest_frame is not None
                else None
            )

        if frame is None:
            time.sleep(0.05)
            continue

        ok, buffer = cv2.imencode(".jpg", frame)

        if not ok:
            continue

        jpg_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpg_bytes
            + b"\r\n"
        )


@app.route("/video")
def video_feed():

    return Response(
        _mjpeg_generator(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


def setup_api(reset_callback):
    """
    Connect the API layer to main.py's reset function.
    """

    register_api(
        app,
        reset_callback,
    )


def start_server(host="0.0.0.0", port=5000):

    app.run(
        host=host,
        port=port,
        threaded=True,
        use_reloader=False,
    )


class LocalRecorder:
    """Writes frames to timestamped local MP4."""

    def __init__(
        self,
        output_dir="recordings",
        fps=20,
        frame_size=(640, 480),
    ):

        os.makedirs(
            output_dir,
            exist_ok=True,
        )

        filename = datetime.now().strftime(
            "experiment_%Y%m%d_%H%M%S.mp4"
        )

        path = os.path.join(
            output_dir,
            filename,
        )

        fourcc = cv2.VideoWriter_fourcc(
            *"mp4v"
        )

        self.writer = cv2.VideoWriter(
            path,
            fourcc,
            fps,
            frame_size,
        )

        self.path = path

    def write(self, frame_bgr):
        self.writer.write(frame_bgr)

    def release(self):
        self.writer.release()