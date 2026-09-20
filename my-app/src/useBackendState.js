import { useEffect, useState } from "react";

export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

const initialState = {
  system: {},
  perception: { objects: [] },
  procedure: { steps: [], completed: 0, total: 0 },
  alert: { active: false },
  events: [],
};

export function useBackendState() {
  const [state, setState] = useState(initialState);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let active = true;

    const loadState = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/state`);
        if (!response.ok) throw new Error("Backend request failed");
        const nextState = await response.json();
        if (active) {
          setState(nextState);
          setConnected(true);
        }
      } catch {
        if (active) setConnected(false);
      }
    };

    loadState();
    const intervalId = window.setInterval(loadState, 500);

    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const resetSequence = async () => {
    await fetch(`${BACKEND_URL}/api/reset`, { method: "POST" });
  };

  return { state, connected, resetSequence };
}