require("@nomiclabs/hardhat-waffle");

module.exports = {
  solidity: "0.8.20",
  networks: {
    polygon: {
      url: "https://polygon-mainnet.infura.io/v3/<YOUR-API-KEY>",
      accounts: ["YOUR_WALLET_PRIVATE_KEY"]
    },
    custom: {
      url: "https://your-network-rpc-url",
      accounts: ["YOUR_WALLET_PRIVATE_KEY"]
    }
  }
};