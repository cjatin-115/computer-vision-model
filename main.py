"""
main.py
-------
Entry point. Wires everything together:

  webcam -> Perception -> StepSequenceEngine -> VoiceAlert + log
                                 |
                                 v
                         Dashboard (GUI) <- annotated frame
                                 |
                                 v
                    streamer.update_frame() -> MJPEG /video + local .mp4

Run:
    python main.py
Then open http://localhost:5000/video in a browser to see the remote stream.
"""

import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")  # avoid Windows OpenMP DLL conflict crash

import threading
import time
import sys
import traceback
import cv2

from src.perception import Perception
from src.step_engine import Step, StepSequenceEngine
from src.voice_alert import VoiceAlert
from src.gui import Dashboard
from src import streamer

TUBE_OBJECTS = {"bottle", "cell phone", "remote", "book", "scissors", "toothbrush"}
RACK_OBJECTS = {"cup", "mouse", "bowl", "keyboard"}
TARGET_CLASSES = list(TUBE_OBJECTS | RACK_OBJECTS)


def build_demo_steps():
    """
    Defines a toy 4-step procedure using COCO stand-in objects:
      1. Pick up sample tube               -> hand near bottle / cell phone
      2. Place tube in rack                -> hand near cup / mouse / bowl
      3. Retrieve tube from rack           -> hand near bottle / cell phone again
      4. Return to rest position           -> hand away from all objects (allow_out_of_sequence=False)
    """
    steps = [
        Step("Pick up sample tube",
             detector=lambda s: s["hand_near"] in TUBE_OBJECTS,
             description="Hand moves to within range of the tube (bottle/phone)",
             allow_out_of_sequence=True),

        Step("Place tube in rack",
             detector=lambda s: s["hand_near"] in RACK_OBJECTS,
             description="Hand moves to the rack (cup/mouse/bowl)",
             allow_out_of_sequence=True),

        Step("Retrieve tube from rack",
             detector=lambda s: s["hand_near"] in TUBE_OBJECTS,
             description="Hand returns to the tube (bottle/phone)",
             allow_out_of_sequence=True),

        Step("Return to rest position",
             detector=lambda s: s["hand_near"] is None and len(s.get("hand_points", [])) > 0,
             description="Hand moves away from all tracked objects",
             allow_out_of_sequence=False),  # Prevents premature wildcard matching!
    ]
    return steps


def main():
    steps = build_demo_steps()
    engine = StepSequenceEngine(steps, log_path="logs/experiment_log.json")
    voice = VoiceAlert()

    def do_reset():
        engine.reset()
        if 'dashboard' in locals() and dashboard:
            dashboard.reset_steps()
            dashboard.log_event("Sequence reset. Waiting for Step 1.")
        voice.say("Sequence reset. Waiting for Step 1.")

    dashboard = Dashboard([s.name for s in steps], on_reset_callback=do_reset)
    perception = Perception(yolo_weights="yolov8n.pt", target_classes=TARGET_CLASSES)
    recorder = None

    # Start the MJPEG stream server in the background
    threading.Thread(target=streamer.start_server, daemon=True).start()

    import platform
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError(
            "Could not open webcam (index 0). Try a different index (1, 2...) "
            "if you have multiple cameras."
        )

    from src.streamer import LocalRecorder
    recorder = LocalRecorder(output_dir="recordings", fps=20,
                              frame_size=(int(cap.get(3)) or 640, int(cap.get(4)) or 480))

    voice.say("Experiment monitoring started. Ready for step 1.")
    dashboard.log_event("System started. Waiting for step 1: " + steps[0].name)
    print("[main] Setup complete. System active. Press 'r' to reset sequence, Ctrl+C to stop.")

    frame_count = 0
    consecutive_failed_reads = 0
    completion_time = None

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                consecutive_failed_reads += 1
                if consecutive_failed_reads >= 30:
                    print("[main] 30 failed reads in a row. Camera disconnected?")
                    break
                time.sleep(0.1)
                continue
            consecutive_failed_reads = 0
            frame_count += 1

            perception_state, annotated = perception.process_frame(frame)

            # Check sequence progress
            event = engine.process(perception_state)
            if event:
                dashboard.mark_step(event.step_name, event.status)
                dashboard.log_event(f"[{event.timestamp}] {event.step_name}: {event.status}")

                if event.status == "completed":
                    nxt = engine.expected_step
                    voice.confirm_step(event.step_name, nxt.name if nxt else None)
                elif event.status == "skipped":
                    voice.alert_skipped(event.step_name)
                elif event.status == "out_of_sequence":
                    nxt = engine.expected_step
                    voice.alert_out_of_sequence(event.step_name, nxt.name if nxt else None)

            # Continuous spoken diagnostics when hand is in frame but action not completing
            if perception_state.get("hand_points") and not engine.is_finished():
                exp = engine.expected_step
                if exp:
                    vis = set(perception_state.get("objects_visible", []))
                    if exp.name in ("Pick up sample tube", "Retrieve tube from rack"):
                        if not (vis & TUBE_OBJECTS):
                            voice.alert_missing_target("sample tube or bottle", cooldown_sec=6.0)
                        elif perception_state.get("hand_near") is None:
                            voice.alert_hand_far(perception_state.get("closest_obj") or "sample tube", cooldown_sec=6.0)
                    elif exp.name == "Place tube in rack":
                        if not (vis & RACK_OBJECTS):
                            voice.alert_missing_target("sample rack or cup", cooldown_sec=6.0)
                        elif perception_state.get("hand_near") is None:
                            voice.alert_hand_far(perception_state.get("closest_obj") or "sample rack", cooldown_sec=6.0)

            # Handle sequence completion and auto-reset without stopping app
            if engine.is_finished():
                if completion_time is None:
                    completion_time = time.time()
                    dashboard.log_event("Experiment sequence complete! Resetting in 5s...")
                elif time.time() - completion_time > 5.0:
                    do_reset()
                    completion_time = None
            else:
                completion_time = None

            # Push frame to GUI, streamer, and recorder
            dashboard.update_frame(annotated)
            streamer.update_frame(annotated)
            recorder.write(cv2.resize(annotated, (int(cap.get(3)) or 640, int(cap.get(4)) or 480)))

            dashboard.tick()

    except KeyboardInterrupt:
        print("[main] Keyboard interrupt detected. Exiting cleanly.")
    except Exception as e:
        print(f"\n[main] Error encountered: {e}")
        traceback.print_exc()
        voice.say("Warning. System encountered a temporary error. Continuing execution.")
    finally:
        cap.release()
        if recorder:
            recorder.release()
        perception.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\n[main] CRASHED WITH AN EXCEPTION:\n")
        traceback.print_exc()
        sys.exit(1)

