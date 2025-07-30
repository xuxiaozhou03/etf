import { getEtfs } from "./data/getEtfs";

const main = async () => {
  const etfs = await getEtfs();
  console.log("ETF 列表:", etfs);
};

main();
