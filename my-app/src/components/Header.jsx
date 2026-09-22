import { Activity } from "lucide-react";

function Header({ connected, system }) {
  const online = connected && system.camera !== "OFFLINE";

  return (
    <header className="border-b border-slate-800 bg-[#0d131c]">

      <div className="mx-auto flex max-w-[1600px] items-center justify-between px-6 py-4">

        <div className="flex items-center gap-4">

          <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-blue-600/15">
            <Activity
              className="text-blue-400"
              size={24}
            />
          </div>

          <div>
            <h1 className="text-lg font-semibold tracking-wide">
              ON-BOARD HAR MONITOR
            </h1>

            <p className="text-xs text-slate-500">
              AI Human Activity Recognition System
            </p>
          </div>

        </div>


        <div className="flex items-center gap-3">

          <div className={`flex items-center gap-2 rounded-full border px-4 py-2 ${online ? "border-emerald-500/20 bg-emerald-500/10" : "border-amber-500/20 bg-amber-500/10"}`}>

            <span className={`h-2 w-2 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />

            <span className={`text-xs font-medium ${online ? "text-emerald-400" : "text-amber-400"}`}>
              {online ? "SYSTEM ONLINE" : "CONNECTING"}
            </span>

          </div>

          <div className="hidden text-right sm:block">

            <p className="text-xs text-slate-500">
              EXPERIMENT
            </p>

            <p className="text-sm font-medium">
              EXP-001
            </p>

          </div>

        </div>

      </div>

    </header>
  );
}

export default Header;