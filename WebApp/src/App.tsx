import "./App.css";
import { ModeToggle } from "./components/mode-toggle";
import { RaspberryCard } from "./components/RaspberryCard";

function App() {
  return (
    <>
      <div className="flex justify-end p-4">
        <ModeToggle />
      </div>
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-center mb-8">
          SkyVault - Monitoring
        </h1>
        <div className="max-w-lg mx-auto">
          <RaspberryCard />
        </div>
      </div>
    </>
  );
}

export default App;
