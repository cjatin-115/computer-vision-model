"""
step_engine.py
--------------
Core sequence-validation logic for the HAR system.

An "experiment" is defined as an ordered list of steps. Each step has:
  - a name
  - a detector function: given the current frame's perception state
    (which objects are visible, where the hand is, what it's near),
    returns True if that step's action has just been completed.

This module does NOT care how you detect the step (color blob, YOLO
class + hand distance, a trained classifier...) - it only owns the
sequence logic: what step is expected next, did the user skip one,
did they do one out of order, log the outcome.

Swap `detector` functions with your real perception model later -
the state machine underneath does not change.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional
from datetime import datetime
import json
import os


@dataclass
class Step:
    name: str
    detector: Callable[[dict], bool]   # perception_state -> bool
    description: str = ""
    allow_out_of_sequence: bool = True


@dataclass
class StepEvent:
    step_name: str
    status: str          # "completed" | "skipped" | "out_of_sequence" | "info"
    timestamp: str
    note: str = ""


class StepSequenceEngine:
    def __init__(self, steps: List[Step], log_path: str = "logs/experiment_log.json"):
        self.steps = steps
        self.current_index = 0          # index of the step we're expecting next
        self.events: List[StepEvent] = []
        self.log_path = log_path
        self._completed_names = set()
        self._started = False

    @property
    def expected_step(self) -> Optional[Step]:
        if self.current_index >= len(self.steps):
            return None
        return self.steps[self.current_index]

    def reset(self):
        """Reset the sequence engine back to step 1."""
        self.current_index = 0
        self.events.clear()
        self._completed_names.clear()
        self._started = False
        self._log_event(StepEvent("Sequence Reset", "info", self._now(), note="Sequence reset"))

    def _now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log_event(self, event: StepEvent):
        self.events.append(event)
        self._write_log()

    def _write_log(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        payload = {
            "experiment": "Sample rack loading procedure",
            "generated_at": self._now(),
            "steps_total": len(self.steps),
            "steps_completed": len(self._completed_names),
            "events": [e.__dict__ for e in self.events],
        }
        with open(self.log_path, "w") as f:
            json.dump(payload, f, indent=2)

    def process(self, perception_state: dict) -> Optional[StepEvent]:
        """
        Call this once per frame (or per few frames) with the current
        perception_state, e.g.:
            {"objects_visible": ["tube", "rack"], "hand_near": "tube"}

        Returns a StepEvent if something notable happened this call,
        else None.
        """
        # Track whether the person has actually started interacting yet.
        if perception_state.get("hand_points") or perception_state.get("hand_near"):
            self._started = True

        # 1. Check if the expected step just got completed
        expected = self.expected_step
        if expected and expected.detector(perception_state):
            self._completed_names.add(expected.name)
            event = StepEvent(expected.name, "completed", self._now())
            self._log_event(event)
            self.current_index += 1
            return event

        # 2. Check if a FUTURE step was detected out of order (skip ahead)
        #    - only once the person has actually started interacting, so a
        #    trivially-true detector can't fire before anything has happened.
        #    - only for steps that allow out-of-sequence execution.
        if self._started:
            for idx in range(self.current_index + 1, len(self.steps)):
                future_step = self.steps[idx]
                if not future_step.allow_out_of_sequence:
                    continue
                if future_step.detector(perception_state):
                    skipped = self.steps[self.current_index:idx]
                    for s in skipped:
                        self._log_event(StepEvent(s.name, "skipped", self._now(),
                                                   note=f"Skipped before '{future_step.name}'"))
                    event = StepEvent(future_step.name, "out_of_sequence", self._now(),
                                       note=f"Performed early, expected '{expected.name if expected else 'N/A'}'")
                    self._log_event(event)
                    self.current_index = idx + 1
                    return event

        return None

    def is_finished(self) -> bool:
        return self.current_index >= len(self.steps)

    def progress_text(self) -> str:
        return f"{len(self._completed_names)}/{len(self.steps)} steps done"

