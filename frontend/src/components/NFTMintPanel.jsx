import React, { useState } from "react";

function NFTMintPanel() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");

  const handleMint = () => {
    alert("Mint function will trigger backend AI + IPFS + Web3 pipeline.");
  };

  return (
    <div className="bg-gray-800 p-4 rounded shadow-md">
      <h2 className="text-xl font-bold mb-2">🧠 Mint New Knowledge NFT</h2>
      <input className="w-full mb-2 p-2 text-black" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <textarea className="w-full mb-2 p-2 text-black" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
      <input className="w-full mb-2 p-2 text-black" placeholder="Tags (comma separated)" value={tags} onChange={(e) => setTags(e.target.value)} />
      <button onClick={handleMint} className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700">Mint NFT</button>
    </div>
  );
}

export default NFTMintPanel;