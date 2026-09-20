import {
  CheckCircle2,
  Circle,
  Activity,
  Box,
} from "lucide-react";


export function Step({ step }) {

  const completed = step.status === "completed";
  const active = step.status === "active";

  return (
    <div
      className={`mb-2 flex items-center gap-4 rounded-lg border p-3 ${
        active
          ? "border-blue-500/30 bg-blue-500/5"
          : "border-transparent"
      }`}
    >

      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          completed
            ? "bg-emerald-500/15 text-emerald-400"
            : active
              ? "bg-blue-500/15 text-blue-400"
              : "bg-slate-800 text-slate-500"
        }`}
      >

        {completed ? (
          <CheckCircle2 size={17} />
        ) : active ? (
          <Activity size={17} />
        ) : (
          <Circle size={17} />
        )}

      </div>


      <div className="min-w-0">

        <p
          className={`text-sm ${
            active
              ? "font-medium text-white"
              : completed
                ? "text-slate-300"
                : "text-slate-500"
          }`}
        >
          {step.name}
        </p>

        <p className="mt-0.5 text-[11px] uppercase tracking-wide text-slate-600">

          {completed
            ? "Completed"
            : active
              ? "In progress"
              : "Pending"}

        </p>

      </div>

    </div>
  );
}


export function InfoBox({
  label,
  value,
  positive,
}) {

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">

      <p className="text-[10px] font-medium tracking-wider text-slate-600">
        {label}
      </p>

      <p
        className={`mt-2 text-sm font-semibold ${
          positive
            ? "text-emerald-400"
            : "text-slate-200"
        }`}
      >
        {value}
      </p>

    </div>
  );
}


export function ObjectTag({ name }) {

  return (
    <div className="flex items-center gap-2 rounded-md border border-slate-700 bg-slate-900 px-3 py-2">

      <Box
        size={14}
        className="text-blue-400"
      />

      <span className="text-xs text-slate-300">
        {name}
      </span>

    </div>
  );
}


export function StatusRow({
  name,
  status,
}) {

  return (
    <div className="flex items-center justify-between border-b border-slate-800 py-3 last:border-0">

      <div className="flex items-center gap-3">

        <span className="h-2 w-2 rounded-full bg-emerald-400" />

        <span className="text-sm text-slate-300">
          {name}
        </span>

      </div>

      <span className="text-[11px] font-medium text-emerald-400">
        {status}
      </span>

    </div>
  );
}