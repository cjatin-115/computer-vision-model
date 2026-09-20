"""
api.py
------
Flask API state layer for the React dashboard.

The AI pipeline updates the shared state from main.py.
The React frontend reads it through /api/state and can reset
the experiment through /api/reset.
"""

import threading
from flask import Blueprint, jsonify

api = Blueprint("api", __name__)

_state_lock = threading.Lock()
_synced_event_count = 0

_state = {
    "system": {
        "camera": "STARTING",
        "yolo": "STARTING",
        "hand_tracking": "STARTING",
        "step_engine": "STARTING",
        "recording": "STARTING",
    },
    "perception": {
        "hand_status": "OUT OF FRAME",
        "hand_near": None,
        "closest_object": None,
        "distance": None,
        "objects": [],
    },
    "procedure": {
        "current_step": None,
        "completed": 0,
        "total": 0,
        "finished": False,
        "steps": [],
    },
    "alert": {
        "active": False,
        "message": "",
        "type": "info",
        "timestamp": None,
    },
    "events": [],
}


def register_api(app, reset_callback):
    """
    Register API routes on the Flask app.

    reset_callback is supplied by main.py so the API does not
    directly depend on StepSequenceEngine.
    """

    app.register_blueprint(api)

    api.reset_callback = reset_callback

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response


def update_state(
    perception_state=None,
    engine=None,
    system=None,
    event=None,
):
    """Update the dashboard state from the main AI loop."""

    global _synced_event_count

    with _state_lock:

        if perception_state is not None:
            hand_points = perception_state.get("hand_points", [])

            _state["perception"] = {
                "hand_status": (
                    "DETECTED"
                    if hand_points
                    else "OUT OF FRAME"
                ),
                "hand_near": perception_state.get("hand_near"),
                "closest_object": perception_state.get("closest_obj"),
                "distance": perception_state.get("closest_dist"),
                "objects": perception_state.get(
                    "objects_visible", []
                ),
            }

        if engine is not None:
            expected = engine.expected_step

            _state["procedure"] = {
                "current_step": (
                    expected.name
                    if expected
                    else None
                ),
                "completed": len(engine._completed_names),
                "total": len(engine.steps),
                "finished": engine.is_finished(),
                "steps": _step_statuses(engine),
            }

            _state["system"]["step_engine"] = "ACTIVE"

            if len(engine.events) < _synced_event_count:
                _synced_event_count = 0

            for new_event in engine.events[_synced_event_count:]:
                _add_event(new_event)
            _synced_event_count = len(engine.events)

        if system:
            _state["system"].update(system)



def _step_statuses(engine):
    statuses = {step.name: "pending" for step in engine.steps}
    for event in engine.events:
        if event.status in {"completed", "skipped", "out_of_sequence"}:
            statuses[event.step_name] = event.status

    expected = engine.expected_step
    if expected and statuses[expected.name] == "pending":
        statuses[expected.name] = "active"

    return [
        {"name": step.name, "description": step.description, "status": statuses[step.name]}
        for step in engine.steps
    ]


def _add_event(event):
    """Convert a StepEvent into JSON-safe data."""

    event_data = {
        "step_name": event.step_name,
        "status": event.status,
        "timestamp": event.timestamp,
        "note": event.note,
    }

    _state["events"].append(event_data)

    # Keep the frontend log reasonably small.
    _state["events"] = _state["events"][-100:]

    if event.status == "completed":
        _state["alert"] = {
            "active": False,
            "message": "",
            "type": "success",
            "timestamp": event.timestamp,
        }

    elif event.status == "skipped":
        _state["alert"] = {
            "active": True,
            "message": f"Step skipped: {event.step_name}",
            "type": "warning",
            "timestamp": event.timestamp,
        }

    elif event.status == "out_of_sequence":
        _state["alert"] = {
            "active": True,
            "message": (
                f"Out of sequence: {event.step_name}"
            ),
            "type": "warning",
            "timestamp": event.timestamp,
        }


def clear_alert():
    global _synced_event_count

    with _state_lock:
        _state["alert"] = {
            "active": False,
            "message": "",
            "type": "info",
            "timestamp": None,
        }


def reset_state(total_steps=0):
    """Reset frontend-visible state."""

    with _state_lock:
        _state["procedure"] = {
            "current_step": None,
            "completed": 0,
            "total": total_steps,
            "finished": False,
            "steps": [],
        }

        _state["alert"] = {
            "active": False,
            "message": "",
            "type": "info",
            "timestamp": None,
        }

        _state["events"] = []
        _synced_event_count = 0


@api.route("/api/state", methods=["GET"])
def get_state():
    with _state_lock:
        # Return a copy so callers cannot modify shared state.
        import copy

        return jsonify(copy.deepcopy(_state))


@api.route("/api/health", methods=["GET"])
def health():
    with _state_lock:
        return jsonify({
            "status": "ok",
            "system": _state["system"],
        })


@api.route("/api/reset", methods=["POST"])
def reset():
    callback = getattr(api, "reset_callback", None)

    if callback is None:
        return jsonify({
            "success": False,
            "error": "Reset callback not configured",
        }), 500

    try:
        callback()

        return jsonify({
            "success": True,
            "message": "Sequence reset successfully",
        })

    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
        }), 500