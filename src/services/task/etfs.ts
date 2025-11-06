import * as fs from "fs/promises";
import { EtfInfo, fetchEtfInfo } from "../stock-data/etf/info";
import { Etf, fetchEtfs } from "../stock-data/etfs";

type EtfWithInfo = Pick<Etf, "name" | "code" | "type"> & EtfInfo;

export const reptileEtfAndInfo = async () => {
  const etfs = await fetchEtfs();
  const etfWithInfos: EtfWithInfo[] = [];
  for (const etf of etfs) {
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
    JSON.stringify(etfWithInfos, null, 2)
  );
  return {
    ok: true,
  };
};
