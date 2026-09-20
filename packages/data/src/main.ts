import { fetchEtfs } from "./etfs";
import { fetchAllLinkFunds } from "./linkFund";
import { saveFile } from "./utils/saveFile";

const main = async () => {
  const etfs = await fetchEtfs();
  saveFile("etfs.json", etfs);

  await fetchAllLinkFunds(etfs);
};

main();
