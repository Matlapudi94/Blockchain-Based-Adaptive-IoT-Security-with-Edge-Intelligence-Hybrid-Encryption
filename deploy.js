const fs = require("fs");
const path = require("path");

async function main() {
  const Contract = await ethers.getContractFactory("AdaptiveSecurityAudit");
  const contract = await Contract.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("AdaptiveSecurityAudit deployed to:", address);

  const envPath = path.join(__dirname, "..", "..", ".env");
  let env = "";
  if (fs.existsSync(envPath)) {
    env = fs.readFileSync(envPath, "utf8");
  }

  const nextLine = `ETH_CONTRACT_ADDRESS=${address}`;
  if (env.includes("ETH_CONTRACT_ADDRESS=")) {
    env = env.replace(/ETH_CONTRACT_ADDRESS=.*/g, nextLine);
  } else {
    env += `${env.endsWith("\n") || env.length === 0 ? "" : "\n"}${nextLine}\n`;
  }
  fs.writeFileSync(envPath, env, "utf8");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
