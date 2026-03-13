import * as fs from "fs/promises";
import { EtfInfo, fetchEtfInfo } from "../stock-data/etf/info";
import { Etf, fetchEtfs } from "../stock-data/etfs";

export type EtfWithInfo = Pick<Etf, "name" | "code" | "type"> & EtfInfo;

export const reptileEtfAndInfo = async () => {
  console.log("Start fetching ETFs and their info...");
  const etfs = await fetchEtfs();
  console.log(`Fetched ${etfs.length} ETFs. Now fetching their info...`);
  const etfWithInfos: EtfWithInfo[] = [];
  for (const etf of etfs) {
    console.log(`Fetching info for ETF ${etf.code} - ${etf.name}...`);
    const info = await fetchEtfInfo(etf.code);
    await new Promise((resolve) => setTimeout(resolve, 200)); // avoid being blocked
    etfWithInfos.push({
      ...info,
      name: etf.name,
      code: etf.code,
      type: etf.type,
    });
  }
  await fs.writeFile(
    "etf-with-info.json",
    JSON.stringify(etfWithInfos, null, 2),
  );
  return {
    ok: true,
  };
};
