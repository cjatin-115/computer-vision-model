import Header from "./components/Header";
import DashboardPanels from "./components/DashboardPanels";
import EventLog from "./components/EventLog";

function App() {
  return (
    <div className="min-h-screen bg-[#080c12] text-white">
      <Header />

      <main className="mx-auto max-w-[1600px] space-y-5 p-6">
        <DashboardPanels />
        <EventLog />
      </main>
    </div>
  );
}

export default App;