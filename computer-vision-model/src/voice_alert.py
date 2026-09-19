"""
voice_alert.py
--------------
Offline text-to-speech alerts. pyttsx3 works fully offline (uses the
OS's built-in TTS engine), which matters here since the whole system
is supposed to run standalone without ground-station connectivity.

Runs speech in a background thread so it never blocks the video loop.
"""

import threading
import queue
import platform
import time
import pyttsx3


class VoiceAlert:
    def __init__(self, rate: int = 170):
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._rate = rate
        self._last_spoken = {}
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        if platform.system() == "Windows":
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            while True:
                text = self._queue.get()
                if text is None:
                    break
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            print(f"[voice_alert] TTS error: {e}")

    def say(self, text: str, cooldown_sec: float = 0.0):
        """Non-blocking: queues the message for the speech thread with optional cooldown."""
        now = time.time()
        with self._lock:
            last = self._last_spoken.get(text, 0)
            if cooldown_sec > 0 and (now - last) < cooldown_sec:
                return  # Skip repeated prompt within cooldown window
            self._last_spoken[text] = now

        self._queue.put(text)

    def say_warning(self, text: str, cooldown_sec: float = 4.0):
        self.say(f"Warning. {text}", cooldown_sec=cooldown_sec)

    def alert_missing_target(self, target_name: str, cooldown_sec: float = 6.0):
        self.say_warning(f"Hand detected, but no {target_name} visible in frame.", cooldown_sec=cooldown_sec)

    def alert_hand_far(self, target_name: str, cooldown_sec: float = 6.0):
        self.say_warning(f"Please move your hand closer to the {target_name}.", cooldown_sec=cooldown_sec)

    def alert_skipped(self, step_name: str):
        self.say(f"Warning. Step {step_name} was skipped.", cooldown_sec=3.0)

    def alert_out_of_sequence(self, step_name: str, expected_name: str = None):
        if expected_name:
            self.say(f"Warning. {step_name} performed out of sequence. Next expected step is {expected_name}.", cooldown_sec=4.0)
        else:
            self.say(f"Warning. {step_name} performed out of sequence.", cooldown_sec=4.0)

    def confirm_step(self, step_name: str, next_step_name: str = None):
        if next_step_name:
            self.say(f"{step_name} complete. Next, {next_step_name}.")
        else:
            self.say(f"{step_name} complete. Procedure finished.")

