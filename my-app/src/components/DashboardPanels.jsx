import {
  Camera,
  Video,
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


function DashboardPanels() {

  const steps = [
    {
      id: 1,
      name: "Pick up sample tube",
      status: "completed",
    },
    {
      id: 2,
      name: "Place tube in rack",
      status: "active",
    },
    {
      id: 3,
      name: "Retrieve tube from rack",
      status: "pending",
    },
    {
      id: 4,
      name: "Return to rest position",
      status: "pending",
    },
  ];


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

            <div className="flex items-center gap-2 text-xs text-emerald-400">

              <span className="h-2 w-2 rounded-full bg-emerald-400" />

              CAMERA CONNECTED

            </div>

          </div>


          <div className="aspect-video bg-black">

            <div className="flex h-full flex-col items-center justify-center text-slate-600">

              <Video
                size={48}
                strokeWidth={1.2}
              />

              <p className="mt-3 text-sm">
                Live camera stream
              </p>

              <p className="mt-1 text-xs">
                Waiting for backend connection...
              </p>

            </div>

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
                25%
              </span>

            </div>


            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-800">

              <div className="h-full w-1/4 rounded-full bg-blue-500" />

            </div>

          </div>


          <div className="p-4">

            {steps.map((step) => (
              <Step
                key={step.id}
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
              value="DETECTED"
              positive
            />

            <InfoBox
              label="HAND NEAR"
              value="CUP"
            />

            <InfoBox
              label="CLOSEST OBJECT"
              value="CUP"
            />

            <InfoBox
              label="DISTANCE"
              value="73 PX"
            />

          </div>


          <div className="border-t border-slate-800 p-5">

            <p className="mb-3 text-xs text-slate-500">
              OBJECTS VISIBLE
            </p>

            <div className="flex gap-2">

              <ObjectTag name="Bottle" />

              <ObjectTag name="Cup" />

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
              status="ONLINE"
            />

            <StatusRow
              name="YOLO Object Detection"
              status="ACTIVE"
            />

            <StatusRow
              name="MediaPipe Hand Tracking"
              status="ACTIVE"
            />

            <StatusRow
              name="Step Sequence Engine"
              status="ACTIVE"
            />

            <StatusRow
              name="Local Recording"
              status="RECORDING"
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
              No active alerts
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Procedure is currently being monitored.
            </p>

          </div>

          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">
            NORMAL
          </span>

        </div>

      </section>

    </>
  );
}

export default DashboardPanels;