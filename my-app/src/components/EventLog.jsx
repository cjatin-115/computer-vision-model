import { RotateCcw } from "lucide-react";

function EventLog() {
  const events = [
    {
      time: "23:41:02",
      text: "System started. Waiting for step 1.",
      type: "info",
    },
    {
      time: "23:41:08",
      text: "Pick up sample tube",
      type: "success",
    },
    {
      time: "23:41:14",
      text: "Place tube in rack",
      type: "success",
    },
  ];

  return (
    <section className="rounded-xl border border-slate-800 bg-[#0d131c]">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">

        <div>
          <h2 className="text-sm font-semibold">
            EVENT LOG
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Experiment activity
          </p>
        </div>

        <button
          type="button"
          className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 transition hover:bg-slate-800"
        >
          <RotateCcw size={14} />
          Reset
        </button>

      </div>

      {/* Events */}
      <div>
        {events.map((event, index) => (
          <Event
            key={`${event.time}-${index}`}
            time={event.time}
            text={event.text}
            type={event.type}
          />
        ))}
      </div>

    </section>
  );
}


function Event({ time, text, type }) {
  const dotColor =
    type === "success"
      ? "bg-emerald-400"
      : type === "warning"
        ? "bg-amber-400"
        : type === "error"
          ? "bg-red-400"
          : "bg-blue-400";

  return (
    <div className="flex items-center gap-4 border-b border-slate-800 px-5 py-3 last:border-0">

      <span className="w-20 shrink-0 font-mono text-xs text-slate-600">
        {time}
      </span>

      <span
        className={`h-2 w-2 shrink-0 rounded-full ${dotColor}`}
      />

      <span className="text-sm text-slate-300">
        {text}
      </span>

    </div>
  );
}


export default EventLog;