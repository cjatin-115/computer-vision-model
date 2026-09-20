import Header from "./components/Header";
import DashboardPanels from "./components/DashboardPanels";
import EventLog from "./components/EventLog";
import { useBackendState } from "./useBackendState";

function App() {
  const { state, connected, resetSequence } = useBackendState();

  return (
    <div className="min-h-screen bg-[#080c12] text-white">
      <Header connected={connected} system={state.system} />

      <main className="mx-auto max-w-[1600px] space-y-5 p-6">
        <DashboardPanels state={state} connected={connected} />
        <EventLog events={state.events} onReset={resetSequence} />
      </main>
    </div>
  );
}

export default App;