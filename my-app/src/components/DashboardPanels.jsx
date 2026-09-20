import {
  Camera,
  Hand,
  Server,
  AlertTriangle,
} from "lucide-react";

import {
  Step,
  InfoBox,
  ObjectTag,
  StatusRow,
} from "./UIComponents";
import { BACKEND_URL } from "../useBackendState";


function DashboardPanels({ state, connected }) {
  const { system, perception, procedure, alert } = state;
  const steps = procedure.steps || [];
  const progress = procedure.total ? Math.round((procedure.completed / procedure.total) * 100) : 0;


  return (
    <>

      {/* TOP ROW */}
      <div className="grid gap-5 lg:grid-cols-[1.7fr_1fr]">

        {/* LIVE CAMERA */}
        <section className="overflow-hidden rounded-xl border border-slate-800 bg-[#0d131c]">

          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">

            <div className="flex items-center gap-3">

              <Camera
                size={18}
                className="text-blue-400"
              />

              <h2 className="text-sm font-semibold">
                LIVE CAMERA
              </h2>

            </div>

            <div className={`flex items-center gap-2 text-xs ${connected ? "text-emerald-400" : "text-amber-400"}`}>

              <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-400" : "bg-amber-400"}`} />

              {system.camera || "STARTING"}

            </div>

          </div>


          <div className="aspect-video bg-black">
            <img className="h-full w-full object-contain" src={`${BACKEND_URL}/video`} alt="Live annotated camera stream" />

          </div>

        </section>


        {/* PROCEDURE */}
        <section className="rounded-xl border border-slate-800 bg-[#0d131c]">

          <div className="border-b border-slate-800 px-5 py-4">

            <div className="flex items-center justify-between">

              <div>

                <h2 className="text-sm font-semibold">
                  PROCEDURE
                </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Sample rack loading procedure
                </p>

              </div>

              <span className="text-sm font-semibold text-blue-400">
                {progress}%
              </span>

            </div>


            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-800">

              <div className="h-full rounded-full bg-blue-500 transition-all" style={{ width: `${progress}%` }} />

            </div>

          </div>


          <div className="p-4">

            {steps.map((step) => (
              <Step
                key={step.name}
                step={step}
              />
            ))}

          </div>

        </section>

      </div>


      {/* SECOND ROW */}
      <div className="grid gap-5 lg:grid-cols-2">

        {/* LIVE PERCEPTION */}
        <section className="rounded-xl border border-slate-800 bg-[#0d131c]">

          <div className="border-b border-slate-800 px-5 py-4">

            <div className="flex items-center gap-3">

              <Hand
                size={18}
                className="text-blue-400"
              />

              <h2 className="text-sm font-semibold">
                LIVE PERCEPTION
              </h2>

            </div>

          </div>


          <div className="grid grid-cols-2 gap-3 p-5">

            <InfoBox
              label="HAND STATUS"
              value={perception.hand_status || "STARTING"}
              positive={perception.hand_status === "DETECTED"}
            />

            <InfoBox
              label="HAND NEAR"
              value={perception.hand_near || "NONE"}
            />

            <InfoBox
              label="CLOSEST OBJECT"
              value={perception.closest_object || "NONE"}
            />

            <InfoBox
              label="DISTANCE"
              value={perception.distance == null ? "NONE" : `${Math.round(perception.distance)} PX`}
            />

          </div>


          <div className="border-t border-slate-800 p-5">

            <p className="mb-3 text-xs text-slate-500">
              OBJECTS VISIBLE
            </p>

            <div className="flex flex-wrap gap-2">
              {(perception.objects || []).map((objectName) => (
                <ObjectTag key={objectName} name={objectName} />
              ))}
              {!perception.objects?.length && <span className="text-xs text-slate-600">No objects detected</span>}

            </div>

          </div>

        </section>


        {/* SYSTEM STATUS */}
        <section className="rounded-xl border border-slate-800 bg-[#0d131c]">

          <div className="border-b border-slate-800 px-5 py-4">

            <div className="flex items-center gap-3">

              <Server
                size={18}
                className="text-blue-400"
              />

              <h2 className="text-sm font-semibold">
                SYSTEM STATUS
              </h2>

            </div>

          </div>


          <div className="p-5">

            <StatusRow
              name="Camera"
              status={system.camera || "STARTING"}
            />

            <StatusRow
              name="YOLO Object Detection"
              status={system.yolo || "STARTING"}
            />

            <StatusRow
              name="MediaPipe Hand Tracking"
              status={system.hand_tracking || "STARTING"}
            />

            <StatusRow
              name="Step Sequence Engine"
              status={system.step_engine || "STARTING"}
            />

            <StatusRow
              name="Local Recording"
              status={system.recording || "STARTING"}
            />

          </div>

        </section>

      </div>


      {/* ALERT */}
      <section className="rounded-xl border border-amber-500/20 bg-[#0d131c]">

        <div className="flex items-center gap-3 border-b border-slate-800 px-5 py-4">

          <AlertTriangle
            size={18}
            className="text-amber-400"
          />

          <h2 className="text-sm font-semibold">
            CURRENT ALERT
          </h2>

        </div>


        <div className="flex items-center justify-between px-5 py-4">

          <div>

            <p className="text-sm text-slate-300">
              {alert.active ? alert.message : "No active alerts"}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              {alert.active ? "Review the current procedure state." : "Procedure is currently being monitored."}
            </p>

          </div>

          <span className={`rounded-full px-3 py-1 text-xs ${alert.active ? "bg-amber-500/10 text-amber-400" : "bg-emerald-500/10 text-emerald-400"}`}>
            {alert.active ? alert.type.toUpperCase() : "NORMAL"}
          </span>

        </div>

      </section>

    </>
  );
}

export default DashboardPanels;