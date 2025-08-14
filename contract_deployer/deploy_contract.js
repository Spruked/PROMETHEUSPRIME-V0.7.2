// Deployment script for KnowledgeNFT using Hardhat
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contract with account:", deployer.address);

  const KnowledgeNFT = await ethers.getContractFactory("KnowledgeNFT");
  const contract = await KnowledgeNFT.deploy();
  await contract.deployed();

  console.log("KnowledgeNFT deployed to:", contract.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
