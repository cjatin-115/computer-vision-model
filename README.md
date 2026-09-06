# On-board HAR prototype (SIH 2026)

A working, runnable scope-down of the "AI Human Activity Recognition for
On-board BAS Experiments" problem statement. This is a **ground-analog
demo**: it proves the full pipeline (detect → validate sequence → alert →
log → stream → GUI) using a webcam and everyday objects, which you then
swap for real trained models once you have your own footage.

## 1. Install

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

First run will auto-download `yolov8n.pt` (~6MB).

## 2. Run the demo (zero training required)

```bash
python main.py
```

- A Tkinter window opens: live feed + step checklist + event log.
- Open `http://localhost:5000/video` in a browser (or from another device
  on the same network, `http://<your-ip>:5000/video`) to see the remote
  stream.
- A local backup recording is saved to `recordings/`.
- A timestamped structured log is written to `logs/experiment_log.json`.

The demo procedure uses a bottle and a cup on your desk as stand-ins for
"sample tube" and "sample rack":
1. Pick up the bottle → hand near it
2. Move it to the cup ("place in rack")
3. Pick it back up
4. Move your hand away ("return to rest")

Try doing them out of order or skipping one — you'll hear a spoken alert
and see it flagged red/orange in the checklist and the JSON log.

## 3. Moving from demo objects to your real experiment

Replace two things; the state machine in `src/step_engine.py` never changes:

**a) Object classes** — fine-tune YOLOv8 on your own kit:
1. Record 100–200 photos/frames of your actual experiment objects (tube,
   rack, tool, etc.) from the camera angle you'll actually use.
2. Label them with [LabelImg](https://github.com/HumanSignal/labelImg) or
   [Roboflow](https://roboflow.com) (free tier) in YOLO format.
3. `yolo detect train data=your_data.yaml model=yolov8n.pt epochs=50`
4. Point `Perception(yolo_weights="runs/detect/train/weights/best.pt")` at
   the new weights in `main.py`.

**b) Step detectors** — in `main.py`, `build_demo_steps()`, replace the
`detector=lambda s: ...` lines with logic (or a small trained classifier)
based on your real objects, e.g. `s["hand_near"] == "sample_tube"`.

## 4. Public datasets you can train/validate against instead of recording your own

All of these are "hand-object interaction during a multi-step procedure"
datasets — the closest available proxy for astronaut experiment steps
(no public space-station footage exists):

| Dataset | Why it fits | Link |
|---|---|---|
| **MECCANO** | Egocentric toy assembly, hand-object interaction, industrial-like setting | francescoragusa.github.io/MECCANO |
| **Assembly101** | Large multi-view assembly dataset with step + mistake labels | assembly-101.github.io |
| **IndustReal** | Built specifically for "Procedure Step Recognition" with skipped/incorrect steps | github.com/TimSchoonbeek/IndustReal |
| **HoloAssist** | Adds a mistake/intervention signal on top of step sequences | holoassist.github.io |

Recommended: fine-tune your object detector on MECCANO or your own
recordings, but write your own `Step` list in `step_engine.py` for
whatever specific procedure you demo on stage — that part is inherently
task-specific.

## 5. What's stubbed vs. real in this prototype

| Requirement in the PS | Status here |
|---|---|
| Local edge processing, no raw video to ground | Done — everything runs on-device |
| Object detection | Real (YOLOv8), swap weights for your kit |
| Hand tracking / hand-object interaction | Real (MediaPipe Hands) |
| Step sequence validation, skip/out-of-order detection | Real, fully general state machine |
| Voice alerts | Real, fully offline (pyttsx3) |
| Timestamped structured log | Real (JSON) |
| Stream to IP + local storage | Real (Flask MJPEG + OpenCV VideoWriter) |
| GUI | Real (Tkinter) |
| 3D pose estimation | **Stubbed** — MediaPipe gives 2D/2.5D wrist point only |
| Orientation-agnostic 3D Human Mesh Recovery (optional PS stretch goal) | **Not implemented** — this needs a research-grade model (e.g. HMR2.0/4D-Humans) and is a stretch goal even for a full team; mention it as "future work" in your pitch, don't try to build it in 36 hours |

## 6. Next upgrades worth mentioning in your pitch (not required for demo)

- Swap MediaPipe wrist-point proximity for a proper hand-object interaction
  classifier trained on MECCANO/Assembly101 annotations.
- Replace the rule-based `Step.detector` with a small temporal model
  (e.g. an LSTM/Transformer over a sliding window of perception states)
  for robustness to occlusion.
- Add the HMR stretch goal as a "phase 2" slide, referencing 4D-Humans
  (github.com/shubham-goel/4D-Humans) as the starting point.
