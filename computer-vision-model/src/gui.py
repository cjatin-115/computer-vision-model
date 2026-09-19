"""
gui.py
------
Lightweight Tkinter dashboard (no extra install needed - ships with
Python). Shows:
  - live annotated camera feed
  - checklist of experiment steps with status (pending/done/skipped)
  - a scrolling alert/event log

main.py pushes updates into this GUI via `update_frame()` and
`update_steps()` - it does not run any perception logic itself.
"""

import tkinter as tk
from PIL import Image, ImageTk
import cv2


class Dashboard:
    def __init__(self, step_names, on_reset_callback=None):
        self.root = tk.Tk()
        self.root.title("On-board HAR Monitor")
        self.on_reset_callback = on_reset_callback

        # --- Left: video panel ---
        self.video_label = tk.Label(self.root)
        self.video_label.grid(row=0, column=0, rowspan=3, padx=8, pady=8)

        # --- Top right: step checklist ---
        checklist_frame = tk.LabelFrame(self.root, text="Experiment steps")
        checklist_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.step_labels = {}
        for name in step_names:
            lbl = tk.Label(checklist_frame, text=f"\u25CB  {name}", anchor="w", width=36)
            lbl.pack(fill="x")
            self.step_labels[name] = lbl

        # --- Middle right: control panel ---
        btn_frame = tk.Frame(checklist_frame)
        btn_frame.pack(fill="x", pady=5)
        self.reset_btn = tk.Button(btn_frame, text="🔄 Reset Sequence (Press 'R')",
                                   command=self._on_reset_clicked, bg="#3498db", fg="white", font=("Arial", 9, "bold"))
        self.reset_btn.pack(padx=5, pady=2, fill="x")

        # --- Bottom right: event log ---
        log_frame = tk.LabelFrame(self.root, text="Event log")
        log_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.log_box = tk.Text(log_frame, width=42, height=12, state="disabled")
        self.log_box.pack(fill="both", expand=True)

    def _on_reset_clicked(self):
        if self.on_reset_callback:
            self.on_reset_callback()

    def reset_steps(self):
        for name, lbl in self.step_labels.items():
            lbl.config(text=f"\u25CB  {name}", fg="black")

    def update_frame(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk  # keep a reference or it gets garbage collected
        self.video_label.configure(image=imgtk)

    def mark_step(self, name: str, status: str):
        # status: "completed" | "skipped" | "out_of_sequence"
        symbol = {"completed": "\u25CF", "skipped": "\u2716", "out_of_sequence": "\u26A0"}.get(status, "\u25CB")
        color = {"completed": "green", "skipped": "red", "out_of_sequence": "orange"}.get(status, "black")
        if name in self.step_labels:
            self.step_labels[name].config(text=f"{symbol}  {name}", fg=color)

    def log_event(self, text: str):
        self.log_box.config(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def tick(self):
        """Call once per loop from main.py instead of root.mainloop(),
        so the same loop can also read camera frames."""
        try:
            self.root.update_idletasks()
            self.root.update()
        except Exception:
            pass

