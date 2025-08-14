import React from "react";
import NFTMintPanel from "./components/NFTMintPanel";
import VaultViewer from "./components/VaultViewer";

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-6">🔥 Prometheus NFT Dashboard</h1>
      <NFTMintPanel />
      <VaultViewer />
    </div>
  );
}

export default App;